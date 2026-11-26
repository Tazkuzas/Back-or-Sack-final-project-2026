import pandas as pd
from pathlib import Path


ROOT = Path(__file__).parent.parent

results = pd.read_csv(ROOT/"data/processed/sdid_results_points.csv", dtype={"season": str})
games_manager = pd.read_csv(ROOT/"data/processed/team_games_manager.csv", dtype={"season": str})
games = pd.read_csv(ROOT/"data/processed/team_games.csv", dtype={"season": str})

results = results[results["pre_fit_ok"] == True]

long_names = games_manager[["league", "season", "round", "position", "team"]]

short_names = games[["league", "season", "round", "position", "team"]]
short_names = short_names.rename(columns={"team": "club"})

names = long_names.merge(short_names, on=["league", "season", "round", "position"])

names = names[["team", "club"]]
names = names.drop_duplicates()

cases = results.merge(names, on="team")


# Part 1: clubs that sacked their coach

collect = []

for index, case in cases.iterrows():
    league_games = games_manager[games_manager["league"] == case["league"]]
    season_games = league_games[league_games["season"] == case["season"]]
    club_games = season_games[season_games["team"] == case["team"]]

    game_before = club_games[club_games["round"] == case["sacking_round"] - 1]
    coach_out = game_before["effective_manager"].iloc[0]

    first_game_new = club_games[club_games["round"] == case["sacking_round"]]
    coach_in = first_game_new["effective_manager"].iloc[0]

    old_coach_games = club_games[club_games["team_manager"] == coach_out]
    old_coach_games = old_coach_games[old_coach_games["round"] < case["sacking_round"]]
    decision_round = old_coach_games["round"].max()

    decision_game = club_games[club_games["round"] == decision_round]
    position = decision_game["position"].iloc[0]
    points = decision_game["cum_points"].iloc[0]
    form = decision_game["form_last5"].iloc[0]

    games_up_to = club_games[club_games["round"] <= decision_round]
    games_after = club_games[club_games["round"] > decision_round]
    change = games_after["points"].mean() - games_up_to["points"].mean()

    last_game = club_games[club_games["round"] == club_games["round"].max()]
    final_position = last_game["position"].iloc[0]
    final_points = last_game["cum_points"].iloc[0]

    collect.append({
        "coach": coach_out,
        "coach_in": coach_in,
        "decision_round": decision_round,
        "position": position,
        "points": points,
        "form": form,
        "change": change,
        "games_left": len(games_after),
        "final_position": final_position,
        "final_points": final_points,
    })

found = pd.DataFrame(collect)
cases = pd.concat([cases, found], axis=1)

cases["points_swing"] = cases["att"] * cases["n_post_games"]
cases["directors_call"] = "Sack"


# Part 2: clubs in a crisis that kept their coach

games_manager["teams_in_league"] = games_manager.groupby(["league", "season"])["team"].transform("nunique")

one_coach = games_manager[games_manager["total_stints"] == 1]

crisis = one_coach[one_coach["round"] >= 6]
crisis = crisis[crisis["round"] <= 32]
crisis = crisis[crisis["form_last5"] <= 0.8]
crisis = crisis[crisis["position"] > crisis["teams_in_league"] / 2]

crisis = crisis.sample(frac=1, random_state=1)
crisis = crisis.drop_duplicates(subset=["league", "season", "team"])

collect_kept = []

for index, moment in crisis.iterrows():
    league_games = games_manager[games_manager["league"] == moment["league"]]
    season_games = league_games[league_games["season"] == moment["season"]]
    club_games = season_games[season_games["team"] == moment["team"]]

    decision_round = moment["round"]

    games_up_to = club_games[club_games["round"] <= decision_round]
    games_after = club_games[club_games["round"] > decision_round]
    change = games_after["points"].mean() - games_up_to["points"].mean()

    similar = cases[(cases["decision_round"] - decision_round).abs() <= 5]
    similar = similar[(similar["form"] - moment["form_last5"]).abs() <= 0.4]

    if len(similar) < 3:
        continue

    points_swing = (similar["change"].mean() - change) * len(games_after)

    last_game = club_games[club_games["round"] == club_games["round"].max()]

    collect_kept.append({
        "unit_id": moment["team"] + "_" + moment["season"],
        "league": moment["league"],
        "season": moment["season"],
        "team": moment["team"],
        "coach": moment["effective_manager"],
        "decision_round": decision_round,
        "position": moment["position"],
        "points": moment["cum_points"],
        "games_left": len(games_after),
        "final_position": last_game["position"].iloc[0],
        "final_points": last_game["cum_points"].iloc[0],
        "points_swing": points_swing,
        "directors_call": "Back",
    })

kept = pd.DataFrame(collect_kept)
kept = kept.merge(names, on="team")


# Part 3: put both together and save

all_cases = pd.concat([cases, kept], ignore_index=True)

all_cases["points_swing"] = all_cases["points_swing"].round(1)
all_cases["case_id"] = all_cases.index

all_cases = all_cases[["case_id", "unit_id", "league", "season", "team", "club", "coach", "coach_in", "directors_call", "decision_round", "position", "points", "games_left", "final_position", "final_points", "points_swing"]]

all_cases.to_csv(ROOT/"data/processed/cases.csv", index=False)

print(all_cases["directors_call"].value_counts())