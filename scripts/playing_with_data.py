import pandas as pd
import numpy as np
import pathlib as Path

AllMatches = "all_matches.csv"
AllTeamGames = "team_games.csv"



every_match = pd.read_csv(f"data/processed/{AllMatches}")
team_games = pd.read_csv(f"data/processed/{AllTeamGames}")


print(every_match)

print(team_games)