import pandas as pd
import numpy as np
from azcausal.core.error import Placebo
from azcausal.core.panel import CausalPanel
from azcausal.estimators.panel.sdid import SDID

# this is a fix proposed by gemini as placebo doesn't work atm, don't understand it yet
import inspect
print(inspect.getsource(CausalPanel.setup))

import azcausal.util.solver as az_solver
_orig_sparsify = az_solver.func_simple_sparsify

def _writable_sparsify(x, *args, **kwargs):
    return _orig_sparsify(x.copy(), *args, **kwargs)

az_solver.func_simple_sparsify = _writable_sparsify
# here, this fix ends


all_games = pd.read_csv("../data/processed/team_games_manager.csv")

def prepare_panel(league: str) -> pd.DataFrame:
    df = all_games[all_games["league"] == league].copy()
    df = df[df["total_stints"] <= 2]
    min_stint = df.groupby(["team", "season"])["stint_length"].transform("min")
    df = df[min_stint >= 4]
    df["unit_id"] = df["team"] + "_" + df["season"].astype(str)
    
    return df.reset_index(drop=True)

def prepare_donors(df: pd.DataFrame, team: str, season: int) -> pd.DataFrame:
    target_unit = f"{team}_{season}"
    target_games = df.loc[df["unit_id"] == target_unit, "total_games"].iloc[0]
    target_league = df.loc[df["unit_id"] == target_unit, "league"].iloc[0]
    donor_pool = df[
        (df["total_games"] == target_games) & 
        (df["league"] == target_league) &
        (df["total_stints"] == 1) &
        (df["team"] != team)
    ].reset_index(drop=True)
    
    return donor_pool

def league_sdid(league, outcome_var) -> dict:
    seasons = [2122, 2223, 2324, 2425, 2526]
    prepared = prepare_panel(league)
    raw_results = {}
    for season in seasons:

        treated_teams = prepared.loc[
            (prepared["season"] == season) & (prepared["total_stints"] == 2),
            "team"
        ].unique()

        for team in treated_teams:
            target_unit = f"{team}_{season}"
            donors = prepare_donors(prepared, team, season)
            treated_df = prepared[prepared["unit_id"] == target_unit]

            sub_df = pd.concat([donors, treated_df], ignore_index=True)

            data = {
                "outcome": sub_df.pivot(index="round", columns="unit_id", values=outcome_var),
                "intervention": sub_df.pivot(index="round", columns="unit_id", values="treated").astype(int),
                    }

            panel = CausalPanel(data).setup()
            estimator = SDID()
            result = estimator.fit(panel)

            # estimator.error(result, Placebo())
            
            raw_results[target_unit] = result
            # estimator.plot(result)
            print(result.summary(title=target_unit))

    return raw_results

sdid_SA = league_sdid("SA", "points")
sdid_PL = league_sdid("PL", "points")
sdid_L1 = league_sdid("L1", "points")
sdid_BL = league_sdid("BL", "points")
sdid_LL = league_sdid("LL", "points")


