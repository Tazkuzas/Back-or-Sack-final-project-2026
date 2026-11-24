import pandas as pd
from pathlib import Path
import numpy as np


ROOT = Path(__file__).parent.parent

results = pd.read_csv(ROOT/"data/processed/sdid_results_points.csv", dtype={"season": str})
games_manager = pd.read_csv(ROOT/"data/processed/team_games_manager.csv", dtype={"season": str})
games = pd.read_csv(ROOT/"data/processed/team_games.csv", dtype={"season": str})

results = results[results["pre_fit_ok"] == True]

# print(len(results))

long_names = games_manager[["league", "season", "round", "position", "team"]]

short_names = games[["league", "season", "round", "position", "team"]]
short_names = short_names.rename(columns={"team": "club"})

names = long_names.merge(short_names, on=["league", "season", "round", "position"])

names = names[["team", "club"]]
names = names.drop_duplicates()

cases = results.merge(names, on="team")


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

    last_game = club_games[club_games["round"] == club_games["round"].max()]
    final_position = last_game["position"].iloc[0]
    final_points = last_game["cum_points"].iloc[0]

    collect.append({
        "coach_out": coach_out,
        "coach_in": coach_in,
        "decision_round": decision_round,
        "position": position,
        "points": points,
        "final_position": final_position,
        "final_points": final_points,
    })

found = pd.DataFrame(collect)
cases = pd.concat([cases, found], axis=1)

cases["points_swing"] = cases["att"] * cases["n_post_games"]
cases["points_swing"] = cases["points_swing"].round(1)

cases["case_id"] = cases.index

cases = cases[["case_id", "unit_id", "league", "season", "team", "club", "coach_out", "coach_in", "decision_round", "sacking_round", "position", "points", "final_position", "final_points", "n_post_games", "att", "ci_low", "ci_high", "points_swing"]]

cases.to_csv(ROOT/"data/processed/cases.csv", index=False)

