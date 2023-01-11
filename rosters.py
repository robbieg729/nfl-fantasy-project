import pandas as pd
import numpy as np
import os
from players_collection import format_name_for_storing

team_mnemonics = {"Buffalo Bills": "BUF", "Miami Dolphins": "MIA", "New York Jets": "NYJ", "New England Patriots": "NE", 
                  "Cincinnati Bengals": "CIN", "Cleveland Browns": "CLE", "Baltimore Ravens": "BAL", "Pittsburgh Steelers": "PIT", 
                  "Indianapolis Colts": "IND", "Jacksonville Jaguars": "JAX", "Houston Texans": "HOU", "Tennessee Titans": "TEN", 
                  "Denver Broncos": "DEN", "Los Angeles Chargers": "LAC", "Kansas City Chiefs": "KC", 
                  "Las Vegas Raiders": "LV", "Dallas Cowboys": "DAL", "Philadelphia Eagles": "PHI", 
                  "Washington Commanders": "WSH", "New York Giants": "NYG", "Chicago Bears": "CHI", "Detroit Lions": "DET", 
                  "Green Bay Packers": "GB", "Minnesota Vikings": "MIN", "Tampa Bay Buccaneers": "TB", "Atlanta Falcons": "ATL", 
                  "Carolina Panthers": "CAR", "New Orleans Saints": "NO", "San Francisco 49ers": "SF", "Arizona Cardinals": "ARI", 
                  "Los Angeles Rams": "LAR", "Seattle Seahawks": "SEA"}

def update_depth_chart(df, roster, positions, multiple_row_positions):    

    for position in positions:
        j = 0
        players = list()
        if position not in multiple_row_positions:
            players = list(df.iloc[positions.index(position)])
        else:
            all_players = list()
            j = positions.index(position)
            while positions[j] == position:
                all_players.append(list(df.iloc[j]))
                j += 1
            all_players = np.array(all_players)
            players = list(np.reshape(np.transpose(all_players), np.shape(all_players)[0] * np.shape(all_players)[1]))
        while "-" in players:
            players.remove("-")
        for i in range(0, len(players)):
            players[i] = format_name_for_storing(players[i])
            if players[i][-1] == "Q" or players[i][-1] == "O" or players[i][-1] == "D" or (players[i][-1] == "P" and "SUSP" not in players[i]):
                players[i] = players[i][0:-2]
            if "SUSP" in players[i]:
                players[i] = players[i][0:-5]
            if "IR" in players[i]:
                players[i] = players[i][0:-3]
            if "PUP" in players[i]:
                players[i] = players[i][0:-4]
        roster[position] = pd.DataFrame({"Name": players})
        j += 1

    return roster
    

def write_team_depth_chart(team, week=None):

    team_nickname = team.split(" ")[-1]

    try:
        os.mkdir("Teams/" + team_nickname + "/Rosters")
    except:
        None

    roster = dict()
    url = "https://www.espn.com/nfl/team/depth/_/name/" + team_mnemonics[team].lower() + "/" + team.replace(" ", "-").lower()
    page = pd.read_html(url)
    offense_positions = list(np.append(["QB"], list(page[0]["QB"])))
    offense = page[1]
    roster = update_depth_chart(offense, roster, offense_positions, ["WR"])
    defense_positions = list(np.append(["LDE"], list(page[2]["LDE"])))
    defense = page[3]
    roster = update_depth_chart(defense, roster, defense_positions, [])
    specials_positions = list(np.append(["K"], list(page[4]["PK"])))
    specials = page[5]
    roster = update_depth_chart(specials, roster, specials_positions, [])

    path = "Teams/" + team_nickname + "/Rosters/Base Roster.xlsx" if week is None else "Teams/" + team_nickname + "/Rosters/Week" + str(week) + ".xlsx"
    with pd.ExcelWriter(path) as writer:
        for position in roster:
            roster[position].to_excel(writer, sheet_name=position)

for team in team_mnemonics:
    write_team_depth_chart(team)