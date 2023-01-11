import pandas as pd
import os
import numpy as np

def create_positions_dict(roster):
    positions = dict()
    positions["CB"] = []
    positions["LB"] = []
    positions["D-Line"] = []
    positions["S"] = []
    positions["RB"] = []
    for sheet in roster.sheet_names:
        if "CB" in sheet:
            positions["CB"] = np.append(positions["CB"], list(roster.parse(sheet)["Name"]))
        elif "LB" in sheet:
            positions["LB"] = np.append(positions["LB"], list(roster.parse(sheet)["Name"]))
        elif "DT" in sheet or "DE" in sheet or "NT" in sheet:
            positions["D-Line"] = np.append(positions["D-Line"], list(roster.parse(sheet)["Name"]))
        elif "SS" in sheet or "FS" in sheet:
            positions["S"] = np.append(positions["S"], list(roster.parse(sheet)["Name"]))
        elif sheet == "RB" or sheet == "FB":
            positions["RB"] = np.append(positions["RB"], list(roster.parse(sheet)["Name"]))
        else:
            positions[sheet] = list(roster.parse(sheet)["Name"])
    return positions

def find_player_position(name, player_positions):
    for position in player_positions:
        if name in player_positions[position]:
            return position
    print("Error finding position of " + name)
    return "Error"

def clean_team(team):
    positions = {"Offense": ["QB", "RB", "WR", "TE"], "Defense": ["D-Line", "LB", "CB", "S"], "Special Teams": ["K", "P"]}
    corrected_opponents = dict()
    for t in os.listdir("Teams"):
        if t != "Commanders":
            corrected_opponents["@" + t] = t
        else:
            corrected_opponents["@Commanders"] = "Commanders"
            corrected_opponents["@Football Team"] = "Commanders"
            corrected_opponents["@Redskins"] = "Commanders"
    for section in positions:
        try:
            os.mkdir("Teams/" + team + "/" + section)
            for position in positions[section]:
                try:
                    os.mkdir("Teams/" + team + "/" + section + "/" + position)
                except FileExistsError:
                    None
                except:
                    print("Error creating " + position + " file for " + team)
        except FileExistsError:
            None
        except:
            print("Error creating " + section + " file for " + team)
        for position in positions[section]:
            for filename in os.listdir("Teams/" + team + "/" + section + "/" + position):
                os.remove("Teams/" + team + "/" + section + "/" + position + "/" + filename)
    roster_file = pd.ExcelFile("Teams/" + team + "/Rosters/Base Roster.xlsx")
    player_positions = create_positions_dict(roster_file)
    data_file = pd.ExcelFile("Teams/" + team + "/All Players Data.xlsx")
    for player in data_file.sheet_names:
        df = data_file.parse(player)
        position = find_player_position(player, player_positions)
        if df.shape[0] != 0:        
            df.fillna(0, inplace=True)
            try:
                df.drop(columns="Unnamed: 0", inplace=True)
            except:
                None
            if position == "QB":
                df = df[df["ATT"] >= 10]
                df.rename(columns={"ATT.1": "RATT", "YDS.1": "RYDS", "TD.1": "RTD", "AVG.1": "RAVG"}, inplace=True)
            elif position == "RB":
                df.rename(columns={"YDS.1": "RECYDS", "AVG.1": "RECAVG", "LNG.1": "RECLNG", "TD.1": "RECTD"}, inplace=True)
            elif position == "WR" or position == "TE":
                df.rename(columns={"YDS.1": "RYDS", "TD.1": "RTD", "LNG.1": "RLNG", "AVG.1": "RAVG"}, inplace=True)
            elif position == "K":
                df.rename(columns={"Avg.1": "RetAvg"}, inplace=True)
            opponents = list(df["OPP"])
            home_road = ["Road" if "@" in opponent else "Home" for opponent in opponents]
            df.insert(4, "Home/Road", home_road)
            df["OPP"].replace(corrected_opponents, inplace=True)
        other_sheets = list()
        team_section = "Offense" if position in positions["Offense"] else ("Defense" if position in positions["Defense"] else "Special Teams")
        try:
            file = pd.ExcelFile("Teams/" + team + "/" + team_section + "/" + position + "/" + player + ".xlsx")
            for sheet in file.sheet_names:
                if sheet != "Game logs":                    
                    other_sheets.append([file.parse(sheet).drop(columns="Unnamed: 0"), sheet])
        except:
            None
        with pd.ExcelWriter("Teams/" + team + "/" + team_section + "/" + position + "/" + player + ".xlsx") as writer:
            df.to_excel(writer, sheet_name="Game logs")
            for sheet in other_sheets:
                sheet[0].to_excel(writer, sheet_name=sheet[1])

for team in os.listdir("Teams"):
    print(team)
    clean_team(team)