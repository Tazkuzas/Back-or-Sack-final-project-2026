import pandas as pd
import numpy as np

original_data = pd.read_csv("../data/processed/team_games_manager.csv", index_col=0)
weights_points = pd.read_csv("../data/processed/sdid_weights_points.csv", index_col=0)
weights_gd = pd.read_csv("../data/processed/sdid_weights_gd.csv")
weights_expvp = pd.read_csv("../data/processed/sdid_weights_pvexp.csv", index_col=0)
original_data["unit_id"] = original_data["team"] + "_" + original_data["season"].astype(str)

def create_sdid_df(regressors, main_data, weight_data):
    donors = weight_data.columns.tolist()
    treated = weight_data.index.tolist()
#    data = []
    relevant_data = main_data[main_data["unit_id"].isin(treated)]
    for t in treated:
        for r in regressors:
            relevant_data[relevant_data["round"]][f"sdid_{r}"] = sum(d * main_data[[main_data["unit_id"] == t][r]][d] for d in donors)
    return relevant_data    


test1 = create_sdid_df(["points_vs_exp", "points", "goal_diff"], original_data, weights_expvp)
print(test1)
print(test2)
print(test3)

