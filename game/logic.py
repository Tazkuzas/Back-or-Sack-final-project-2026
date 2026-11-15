
import pandas as pd


def load_data(path="data/processed/team_games.csv"):
    return pd.read_csv(path, dtype={"season": str})


def load_cases(data):
    # random team
    candidates = data[(data["round"] >= 10) & (data["round"] <= 24)]
    fake = candidates.sample(50, random_state=1)[["league", "season", "team", "round"]]
    fake = fake.rename(columns={"round": "sack_round"}).reset_index(drop=True)
    fake["case_id"] = fake.index
    return fake

#Pick n random case ids for one game.
def pick_cases(cases, n):
    
    return cases.sample(n)["case_id"].tolist()

#Return one case as a single row
def get_case(cases, case_id):
   
    return cases[cases["case_id"] == case_id].iloc[0]

#All games of the case's team in the case's season
def team_season(data, case):
    
    return data[
        (data["league"] == case["league"])
        & (data["season"] == case["season"])
        & (data["team"] == case["team"])
    ]

#Everything the player sees before decision
def situation(data, case):
    
    team = team_season(data, case)
    before = team[team["round"] <= case["sack_round"]]
    now = before.iloc[-1] 

    return {
        "team": case["team"],
        "league": case["league"],
        "season": case["season"],
        "round": int(case["sack_round"]),
        "position": int(now["position"]),
        "points": int(now["cum_points"]),
        "form": float(now["form_last5"]),
        "last10": before.tail(10),
        "history": before,
    }


def counterfactual_ppg(case):
   
    return 1.3 #change later


def outcome(data, case, games=10):
    """What happened after the decision point, for both choices."""
    team = team_season(data, case)
    after = team[team["round"] > case["sack_round"]].head(games)

    sack_ppg = float(after["points"].mean())  
    back_ppg = counterfactual_ppg(case)       

    if sack_ppg > back_ppg:
        better = "sack"
    else:
        better = "back"

    return {"sack_ppg": sack_ppg, "back_ppg": back_ppg, "better": better}