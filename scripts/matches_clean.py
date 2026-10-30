import pandas as pd
import numpy as np
from pathlib import Path


COLUMNS = {
    "Date": "date",
    "HomeTeam": "home_team",
    "AwayTeam": "away_team",
    "FTHG": "home_goals",
    "FTAG": "away_goals",
    "FTR": "result",
    "AvgH": "odds_home",
    "AvgD": "odds_draw",
    "AvgA": "odds_away",
}

LEAGUES = {
    "PL": "PremierLeague",
    "LL": "LaLiga",
    "BL": "Bundesliga",
    "L1": "Ligue1",
    "SA": "SerieA",
}
seasons = ["2122", "2223", "2324", "2425", "2526"]




def tidy(file_name):

    data = pd.read_csv(file_name)
    data = data[list(COLUMNS.keys())]      
    data = data.rename(columns=COLUMNS)    
    return data

all_matches = []
raw = Path("data/raw")
for league, folder in LEAGUES.items():
    for season in seasons:
        file = raw / folder / f"{league}_{season}.csv"
        output = tidy(file)
        output["league"] = league
        output["season"] = season
        all_matches.append(output)

matches = pd.concat(all_matches, ignore_index=True)

print(matches.shape)

#normal date
matches["date"] = pd.to_datetime(matches["date"], format="%d/%m/%Y")

#sorting

matches = matches.sort_values(["league", "season", "date"]).reset_index(drop=True)

processed = Path("data/processed")
matches.to_csv(processed / "all_matches.csv", index=False)