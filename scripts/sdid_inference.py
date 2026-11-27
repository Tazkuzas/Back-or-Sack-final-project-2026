import pandas as pd
import numpy as np
from diff_diff import SyntheticDiD

all_games = pd.read_csv("../data/processed/team_games_manager.csv")

def prepare_panel(league: str) -> pd.DataFrame:
    df = all_games[all_games["league"] == league].copy()
    df = df[df["total_stints"] <= 2]
    min_stint = df.groupby(["team", "season"])["stint_length"].transform("min")
    df = df[min_stint >= 6]
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

def league_sdid(league, outcome_var) -> tuple[list[dict], dict]:
    seasons = [2122, 2223, 2324, 2425, 2526]
    prepared = prepare_panel(league)
    rows = []
    weights = {}
    for season in seasons:

        treated_teams = prepared.loc[
            (prepared["season"] == season) & (prepared["total_stints"] == 2),
            "team"
        ].unique()

        for team in treated_teams:
            target_unit = f"{team}_{season}"
            donors = prepare_donors(prepared, team, season)
            donors = donors[
            donors.groupby("unit_id")[outcome_var].transform(lambda s: s.notna().all())
            ].reset_index(drop=True)
            treated_df = prepared[prepared["unit_id"] == target_unit]

            sub_df = pd.concat([donors, treated_df], ignore_index=True)

            sub_df["ever_treated"] = (sub_df["unit_id"] == target_unit)

            post_df = treated_df[treated_df["treated"] == 1]
            post_rounds = post_df["round"].tolist()
            total_games = int(treated_df["total_games"].iloc[0])
            n_post_games = len(post_rounds)
            n_pre_games = total_games - n_post_games

            sdid = SyntheticDiD(variance_method="placebo", seed=251)
            result = sdid.fit(
                sub_df,
                outcome = outcome_var,
                treatment = "ever_treated",
                unit = "unit_id",
                time = "round",
                post_periods = post_rounds
            )

            rows.append({
                            "unit_id": target_unit,
                            "league": league,
                            "season": int(season),
                            "team": team,
                            "att": result.att,
                            "se": result.se,
                            "p_value": result.p_value,
                            "ci_low": result.att - 1.96 * result.se,
                            "ci_high": result.att + 1.96 * result.se,
                            "sacking_round": int(post_df["round"].min()),
                            "n_pre_games": n_pre_games,
                            "n_post_games": n_post_games,
                            "total_games": total_games,
                            "n_donors": donors["unit_id"].nunique(),
                            "pre_fit_rmse": result.pre_treatment_fit,
                            "pre_fit_placebo_p": result.pre_fit_placebo_pvalue,
                            "pre_fit_ok": result.pre_fit_placebo_pvalue > 0.05,
                        })
            weights[target_unit] = dict(result.unit_weights)
    return rows, weights

def sdid_by_metric(metric) -> tuple[list[dict], dict]:
    leagues = ["SA", "PL", "L1", "LL", "BL"]
    league_rows = []
    weights = {}

    for league in leagues:
        run_sdid = league_sdid(league, metric)
        lsdid, wg = run_sdid
        league_rows.extend(lsdid)
        weights.update(wg)

    return league_rows, weights


# define some fct. as it is 3 times the same block
sdid_points = sdid_by_metric("points")
sdid_results_points = pd.DataFrame(sdid_points[0])
sdid_weights_points = pd.DataFrame.from_dict(sdid_points[1], orient="index").fillna(0.0)
sdid_results_points.to_csv("../data/processed/sdid_results_points.csv", index=False)
sdid_weights_points.to_csv("../data/processed/sdid_weights_points.csv")

sdid_gd = sdid_by_metric("goal_diff")
sdid_results_gd = pd.DataFrame(sdid_gd[0])
sdid_weights_gd = pd.DataFrame.from_dict(sdid_gd[1], orient="index").fillna(0.0)
sdid_results_gd.to_csv("../data/processed/sdid_results_goal_diff.csv", index=False)
sdid_weights_gd.to_csv("../data/processed/sdid_weights_gd.csv")

sdid_pvexp = sdid_by_metric("points_vs_exp")
sdid_results_pvexp = pd.DataFrame(sdid_pvexp[0])
sdid_weights_pvexp = pd.DataFrame.from_dict(sdid_pvexp[1], orient="index").fillna(0.0)
sdid_results_pvexp.to_csv("../data/processed/sdid_results_pvexp.csv", index=False)
sdid_weights_pvexp.to_csv("../data/processed/sdid_weights_pvexp.csv")