import pandas as pd
import numpy as np
from pathlib import Path

processed = Path("data/processed")
raw = Path("data/raw")


data = pd.read_csv(processed / "all_matches.csv", parse_dates=["date"], dtype={"season": str})

home = pd.DataFrame({
    "league": data["league"],
    "season": data["season"],
    "date": data["date"],
    "team": data["home_team"],
    "opponent": data["away_team"],
    "home": 1,
    "goals_for": data["home_goals"],
    "goals_against": data["away_goals"],
    "odds_win": data["odds_home"],
    "odds_draw": data["odds_draw"],
    "odds_loss": data["odds_away"],
})

away = pd.DataFrame({
    "league": data["league"],
    "season": data["season"],
    "date": data["date"],
    "team": data["away_team"],
    "opponent": data["home_team"],
    "home": 1,
    "goals_for": data["away_goals"],
    "goals_against": data["home_goals"],
    "odds_win": data["odds_away"],
    "odds_draw": data["odds_draw"],
    "odds_loss": data["odds_home"],
})

team_games = pd.concat([home, away], ignore_index=True)
team_games = team_games.sort_values(["league", "season", "team", "date"]).reset_index(drop=True)




team_games["result"] = np.select(
    [team_games["goals_for"] > team_games["goals_against"],
     team_games["goals_for"] == team_games["goals_against"]],
    ["W", "D"],
    default="L",
)
team_games["points"] = team_games["result"].map({"W": 3, "D": 1, "L": 0})

keys = ["league", "season", "team"]
group = team_games.groupby(keys)

team_games["round"] = group.cumcount() + 1
team_games["cum_points"] = group["points"].cumsum()



#some additional stats

team_games["form_last5"] = group["points"].transform(lambda s: s.rolling(5).mean())

team_games["goal_diff"] = team_games["goals_for"] - team_games["goals_against"]
team_games["cum_goal_diff"] = group["goal_diff"].cumsum()

team_games = team_games.sort_values(
    ["league", "season", "round", "cum_points", "cum_goal_diff"],
    ascending=[True, True, True, False, False],
)
team_games["position"] = team_games.groupby(["league", "season", "round"]).cumcount() + 1





team_games = team_games.sort_values(["league", "season", "team", "round"]).reset_index(drop=True)
team_games.to_csv(processed / "team_games.csv", index=False)