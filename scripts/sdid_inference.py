import pandas as pd
import numpy as np
from diff_diff import SyntheticDiD

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

            sub_df["ever_treated"] = (sub_df["unit_id"] == target_unit)
            post_rounds = treated_df.loc[treated_df["treated"] == 1, "round"].tolist()

            sdid = SyntheticDiD(variance_method="placebo", seed=251)
            result = sdid.fit(
                sub_df,
                outcome = outcome_var,
                treatment = "ever_treated",
                unit = "unit_id",
                time = "round",
                post_periods = post_rounds
            )
            
            raw_results[target_unit] = result
            print(raw_results)

    return raw_results

sdid_SA = league_sdid("SA", "points")
sdid_PL = league_sdid("PL", "points")
sdid_L1 = league_sdid("L1", "points")
sdid_BL = league_sdid("BL", "points")
sdid_LL = league_sdid("LL", "points")


