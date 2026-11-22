import pandas as pd
import numpy as np
from rapidfuzz import fuzz, process

clubs = pd.read_csv("../data/raw/managerial_data/clubs.csv")
games = pd.read_csv("../data/raw/managerial_data/games.csv")

relevant_clubs = clubs[clubs["domestic_competition_id"].isin({"L1", "FR1", "IT1", "ES1", "GB1"})]
relevant_clubs = relevant_clubs.drop(columns = ["stadium_name", "stadium_seats", "net_transfer_record", "coach_name", "last_season", "filename", "url"])
club_names_source = list(relevant_clubs["name"].drop_duplicates())
club_ids = list(relevant_clubs["club_id"])
relevant_games = games[(games["home_club_id"].isin(club_ids) | games["away_club_id"].isin(club_ids)) & (games["season"] >= 2021)].copy()
#find the unique club names in this data set
# print(relevant_games)
# club_names.to_csv("unique_names.csv", index = False)
# team_names.to_csv()

# find the unique names for each team in the data set used for the game-data

teams = pd.read_csv("../data/processed/team_games.csv")
club_names_target = list(teams["team"].drop_duplicates())
# team_names.to_csv("unique_teams.csv", index = False)

# as fuzz would match these wrongly (checked by looking at those with low fuzz.WRatio)

manual_alias = {
    "FC Koln": "1.FC Köln",
    "Rennes": "Stade Rennais FC",
    "Man City": "Manchester City",
    "Man United": "Manchester United",
    "Milan": "AC Milan",
}

alias = dict()
for i in club_names_target:
    if i in manual_alias:
        alias[i] = manual_alias[i]
    else:
        match, score, _ = process.extractOne(i, club_names_source, scorer=fuzz.WRatio)
        alias[i] = match
        if score < 90:
            print(f"{i:25s} -> {match:35s} (Score: {score:.1f})")
# print(alias)



team_games_new = teams.copy()
team_games_new["team"] = team_games_new["team"].map(alias)
team_games_new["opponent"] = team_games_new["opponent"].map(alias)
# team_games_new.to_csv("fullname_teams.csv", index = False)

name_to_id = dict(zip(relevant_clubs["name"], relevant_clubs["club_id"]))
team_games_new["team_id"] = team_games_new["team"].map(name_to_id)
team_games_new["opp_id"] = team_games_new["opponent"].map(name_to_id)

home_fixtures = set(
    zip(games["date"], games["home_club_id"], games["away_club_id"])
)

team_games_new["home"] = [
    1 if (d, t, o) in home_fixtures else 0
    for d, t, o in zip(team_games_new["date"], team_games_new["team_id"], team_games_new["opp_id"])
]

team_games_new["home_club_id"] = np.where(team_games_new["home"] == 1, team_games_new["team_id"], team_games_new["opp_id"])
team_games_new["away_club_id"] = np.where(team_games_new["home"] == 1, team_games_new["opp_id"], team_games_new["team_id"])

team_games_complete = team_games_new.copy()
team_games_complete = pd.merge(
    team_games_new,
    relevant_games[["date", "home_club_id", "away_club_id", "home_club_manager_name", "away_club_manager_name"]],
    on=["date", "home_club_id", "away_club_id"],
    how="left"
)

team_games_complete["team_manager"] = np.where(
    team_games_complete["home"],
    team_games_complete["home_club_manager_name"],
    team_games_complete["away_club_manager_name"]
)

team_games_complete = team_games_complete.sort_values(["team", "season", "league", "date"]).reset_index(drop=True)
#team_games_complete["round"] = team_games_complete.groupby(["team", "season", "league"]).cumcount() + 1
team_games_complete["total_games"] = team_games_complete.groupby(["team", "season", "league"])["round"].transform("count")

unit = ["team", "season", "league"]

is_new_spell = (
    team_games_complete["team_manager"] != team_games_complete.groupby(unit)["team_manager"].shift(1)
)
# Number each spell within each team-season-league

spell_num = is_new_spell.groupby([team_games_complete[col] for col in unit]).cumsum()
total_spells = spell_num.groupby([team_games_complete[col] for col in unit]).transform("max")
spell_games = team_games_complete.groupby(unit + [spell_num])["team_manager"].transform("count")
clean_manager = team_games_complete["team_manager"].mask((spell_games < 3) & (spell_num > 1))

team_games_complete["effective_manager"] = clean_manager
team_games_complete["effective_manager"] = (
    team_games_complete.groupby(unit)["effective_manager"].ffill()
)

prev_manager = team_games_complete.groupby(unit)["effective_manager"].shift(1)
team_games_complete["manager_change"] = (
    prev_manager.notna() & (team_games_complete["effective_manager"] != prev_manager)
).astype(int)
team_games_complete["treated"] = team_games_complete.groupby(unit)["manager_change"].cummax()

team_games_complete["stint_id"] = team_games_complete.groupby(unit)["manager_change"].cumsum() + 1
team_games_complete["stint_length"] = team_games_complete.groupby(unit + ["stint_id"])["round"].transform("count")
team_games_complete["total_stints"] = team_games_complete.groupby(unit)["stint_id"].transform("max")

team_games_complete.to_csv("../data/processed/team_games_manager.csv", index = False)

print(team_games_complete["total_games"].unique())