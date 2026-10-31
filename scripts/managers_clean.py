import pandas as pd
import numpy as np
from pathlib import Path
from rapidfuzz import fuzz, process

clubs = pd.read_csv("../data/raw/managerial_data/clubs.csv")

relevant_clubs = clubs[clubs["domestic_competition_id"].isin({"L1", "FR1", "IT1", "ES1", "GB1"})]
relevant_clubs = relevant_clubs.drop(columns = ["stadium_name", "stadium_seats", "net_transfer_record", "coach_name", "last_season", "filename", "url"])
club_names_source = list(relevant_clubs["name"].drop_duplicates())

#find the unique club names in this data set

# club_names.to_csv("unique_names.csv", index = False)
# team_names.to_csv()

# find the unique names for each team in the data set used for the game-data

teams = pd.read_csv("../data/processed/team_games.csv")
club_names_target = list(teams["team"].drop_duplicates())
# team_names.to_csv("unique_teams.csv", index = False)
alias = dict()
for i in club_names_target:
    match = process.extractOne(i, club_names_source)
    alias[i] = match[0]

print(alias)




