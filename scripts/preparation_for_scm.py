import pandas as pd
import numpy as np
from scipy.optimize import minimize

all_games = pd.read_csv("../data/processed/team_games_manager.csv")
all_games = all_games.sort_values(["team", "date"])
all_games["game_index"] = all_games.groupby(["team", "season", "league"]).cumcount()
all_games["total_games"] = all_games.groupby(["team", "season", "league"])["game_index"].transform("count")
all_games["new_stint"] = (all_games["team_manager"] != all_games.groupby("team")["team_manager"].shift(1)).astype(int)
all_games["stint_id"] = all_games.groupby(["team", "season", "league"])["new_stint"].cumsum()
all_games["stint_length"] = all_games.groupby(["team", "season", "stint_id"])["game_index"].transform("count")

def seasonleague(season, league):
    sl = all_games[(all_games["season"] == season) & (all_games["league"] == league)]
    return sl

treated_dfs = {}

def treated(season, league):
    df = all_games[(all_games["season"] == season) & (all_games["league"] == league)].copy()
    df["previous_manager"] = df.groupby("team")["team_manager"].shift(1)
    df["previous_stint_length"] = df.groupby("team")["stint_length"].shift(1)
    change = (
        (df["team_manager"] != df["previous_manager"])
        & df["team_manager"].notna()
        & df["previous_manager"].notna()
        & (df["stint_length"] > 3)
    )
    not_early = df["game_index"] >= 5
    not_late = (df["total_games"] - df["game_index"]) >= 5
    changes = df[change & not_early & not_late].copy()
    
    return changes

leagues = ["SA", "LL", "BL", "PL", "L1"]
seasons = [2122, 2223, 2324, 2425, 2526]

for season in seasons: 
    for league in leagues: 
        treated_dfs[f"{league}_{season}"] = treated(season, league)

print(treated_dfs["SA_2122"]["team"] + " " + treated_dfs["SA_2122"]["date"])
print(treated_dfs["SA_2223"]["team"] + " " + treated_dfs["SA_2223"]["date"])
print(treated_dfs["SA_2324"]["team"] + " " + treated_dfs["SA_2324"]["date"])
print(treated_dfs["SA_2425"]["team"] + " " + treated_dfs["SA_2425"]["date"])
print(treated_dfs["SA_2526"]["team"] + " " + treated_dfs["SA_2526"]["date"])
