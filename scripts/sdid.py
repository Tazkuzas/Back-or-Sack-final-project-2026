import pandas as pd
import numpy as np
from azcausal.core.panel import Panel
from azcausal.estimators.panel.sdid import SDID


all_games = pd.read_csv("../data/processed/team_games_manager.csv")


def prepare_panel(league: str) -> pd.DataFrame:
    df = all_games[all_games["league"] == league].copy()
    df = df[df["total_stints"] <= 2]
    min_stint = df.groupby(["team", "season"])["stint_length"].transform("min")
    df = df[min_stint >= 4]
    df["unit_id"] = df["team"] + "_" + df["season"].astype(str)
    
    return df.reset_index(drop=True)

def league_sdid(league, outcome_var):
    panel = Panel(
        data= sub_df,
        outcome = outcome_var,
        time = "game_index",
        unit = "unit_id",
        intervention = "treated"
    )

#estimator = SDID()
#result = estimator.fit(panel)
#result = estimator.error(result, Placebo(n_samples=200))

#print(result.summary())
