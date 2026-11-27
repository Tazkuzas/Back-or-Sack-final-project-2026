import pandas as pd
import numpy as np

original_data = pd.read_csv("../data/processed/team_games_manager.csv", index_col=0)
weights_points = pd.read_csv("../data/processed/sdid_weights_points.csv", index_col=0)
weights_gd = pd.read_csv("../data/processed/sdid_weights_gd.csv", index_col=0)
weights_expvp = pd.read_csv("../data/processed/sdid_weights_pvexp.csv", index_col=0)
original_data["unit_id"] = original_data["team"] + "_" + original_data["season"].astype(str)

def create_sdid_df(regressors, main_data, weight_data):  
    treated = weight_data[0].index.tolist()
    relevant_data = main_data[main_data["unit_id"].isin(treated)].copy()

    for r in regressors:
        relevant_weights = weight_data[regressors.index(r)].copy()
        relevant_weights.index.name = "unit_id"
        donors = relevant_weights.columns.tolist()
        donor_data = main_data[main_data["unit_id"].isin(donors)]
    
        donor_pivot = donor_data.pivot(index="round", columns="unit_id", values=r)[donors]
        cf_matrix = donor_pivot.fillna(0).dot(relevant_weights.T)
        cf_long = cf_matrix.stack().rename(f"sdid_{r}").reset_index()
        relevant_data = relevant_data.merge(cf_long, on=["round", "unit_id"], how="left")
        
    return relevant_data


results = create_sdid_df(["points_vs_exp", "points", "goal_diff"], original_data, [weights_expvp, weights_points, weights_gd])
results.to_csv("../data/processed/round_counterfactuals.csv")