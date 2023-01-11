import pandas as pd
import os

def format_name_for_url(name):
    return name.replace(" ", "-").lower()

def format_name_for_storing(name):
    return name.replace("'", "-").replace("Jr.", "Jr").replace("Sr.", "Sr").replace(". ", " ").replace(".", "-")

def check_name(name, different_names_df, web_roster):
    invalid_name = False
    f_name = format_name_for_url(name)
    if name in list(different_names_df["Name"]):
        filtered = different_names_df[different_names_df["Name"] == name]
        if filtered.shape[0] == 1:
            f_name = list(filtered["URLName"])[0]
        else:
            team_filtered = filtered[filtered["Team"] == team]
            f_name = list(team_filtered["URLName"])[0]
    try:
        page = pd.read_html("https://www.nfl.com/players/" + f_name + "/stats/")
    except:
        if name not in web_roster:
            invalid_name = True
    return f_name, invalid_name

def extract_player_data(name, different_names_df, team, web_roster, team_rookies=[]):
    f_name, invalid_name = check_name(name, different_names_df, web_roster)
    player_df = None
    try:
        career_page = pd.read_html("https://www.nfl.com/players/" + f_name + "/stats/")
        seasons = list(career_page[1]["SEASON"])
        seasons.remove("TOTAL")
        if "2018" in seasons and "2019" not in seasons:
            seasons.append(2019)
        years = [int(season) for season in seasons]
        years.sort()
        for year in years:
            tables = None
            try:
                tables = pd.read_html("https://www.nfl.com/players/" + f_name + "/stats/logs/" + str(year) + "/")
                tables_to_consider = [0, 1, 2]
                if len(tables) == 1:
                    tables_to_consider.remove(1)
                    tables_to_consider.remove(2)
                elif len(tables) == 2:
                    if tables[0].shape[0] > 5:
                        tables_to_consider.remove(2)
                    else:
                        tables_to_consider.remove(0)
                        tables_to_consider.remove(2)
                else:
                    tables_to_consider.remove(0)
                for k in tables_to_consider:
                    table = tables[k]
                    table.insert(0, "Year", year)
                    if player_df is None:
                        player_df = pd.DataFrame(table)
                    else:
                        player_df = pd.concat([player_df, table], axis=0)
            except:
                continue
    except:
        None               
    if player_df is not None:
        return player_df, invalid_name
    else:
        return pd.DataFrame(), invalid_name

def do_full_team_collection(team):
    full_team_name = full_team_names[team]
    web_roster = pd.read_html("https://www.nfl.com/teams/" + format_name_for_url(full_team_name) + "/roster")[0]
    web_roster_names = list(web_roster["Player"])
    for i in range(0, len(web_roster_names)):
        web_roster_names[i] = format_name_for_storing(web_roster_names[i])
    # rookies = list(web_roster[web_roster["Experience"] == "R"]["Player"])
    # for i in range(0, len(rookies)):
    #     rookies[i] = format_name_for_storing(rookies[i])
    roster = pd.ExcelFile("Teams/" + team + "/Rosters/Base Roster.xlsx")
    existing_data = None
    try:
        existing_data = pd.ExcelFile("Teams/" + team + "/All Players Data.xlsx")
    except:
        pd.DataFrame().to_excel("Teams/" + team + "/All Players Data.xlsx")
        existing_data = pd.ExcelFile("Teams/" + team + "/All Players Data.xlsx")
    team_invalids = list()
    dfs = dict()
    for position in roster.sheet_names:
        if position not in positions_not_for_collection:
            players = list(roster.parse(position)["Name"])
            for player in players:
                #if player in list(different_names_df["Name"]) or player not in existing_data.sheet_names:
                player_df, invalid_name = extract_player_data(player, different_names_df, team, web_roster_names)
                dfs[player] = player_df
                if invalid_name is True:
                    team_invalids.append(player)
                # else:
                #     f_name, invalid_name = check_name(player, different_names_df, web_roster_names)
                #     if invalid_name is True:
                #         team_invalids.append(player)
                #     player_df = existing_data.parse(player)
                #     try:
                #         player_df.drop(columns="Unnamed: 0", inplace=True)
                #     except:
                #         None
                #     dfs[player] = player_df
    with pd.ExcelWriter("Teams/" + team + "/All Players Data.xlsx") as writer:
        for player in dfs:
            dfs[player].to_excel(writer, sheet_name=player)
    pd.DataFrame({"Name": team_invalids}).to_excel("Teams/" + team + "/Invalid Names.xlsx", sheet_name="INVALIDS")
    #pd.DataFrame({"Name": rookies}).to_excel("Teams/" + team + "/Rookies.xlsx", sheet_name="Rookies")

def do_team_weekly_update(team, week, year=2022):
    x = 4


if __name__ == "__main__":
    full_team_names = {"Bills": "Buffalo Bills", "Dolphins": "Miami Dolphins", "Jets": "New York Jets", "Patriots": "New England Patriots", 
                    "Bengals": "Cincinnati Bengals", "Browns": "Cleveland Browns", "Ravens": "Baltimore Ravens", 
                    "Steelers": "Pittsburgh Steelers", "Colts": "Indianapolis Colts", "Jaguars": "Jacksonville Jaguars", 
                    "Texans": "Houston Texans", "Titans": "Tennessee Titans", 
                    "Broncos": "Denver Broncos", "Chargers": "Los Angeles Chargers", "Chiefs": "Kansas City Chiefs", 
                    "Raiders": "Las Vegas Raiders", "Cowboys": "Dallas Cowboys", "Eagles": "Philadelphia Eagles", 
                    "Commanders": "Washington Commanders", "Giants": "New York Giants", "Bears": "Chicago Bears", 
                    "Lions": "Detroit Lions", "Packers": "Green Bay Packers", "Vikings": "Minnesota Vikings", 
                    "Buccaneers": "Tampa Bay Buccaneers", "Falcons": "Atlanta Falcons", 
                    "Panthers": "Carolina Panthers", "Saints": "New Orleans Saints", "49ers": "San Francisco 49ers", 
                    "Cardinals": "Arizona Cardinals", 
                    "Rams": "Los Angeles Rams", "Seahawks": "Seattle Seahawks"}
    positions_not_for_collection = ["LT", "LG", "C", "RG", "RT", "H", "KR", "PR", "LS"]
    different_names_df = pd.read_excel("Names.xlsx")
    all_invalid_names_df = pd.DataFrame({"Name": [], "Team": []})

    for team in os.listdir("Teams"):
        print(team)
        do_full_team_collection(team)

        path = "Teams/" + team + "/Invalid Names.xlsx"
        table = pd.read_excel(path)
        table.insert(1, "Team", team)
        all_invalid_names_df = pd.concat([all_invalid_names_df, table], axis=0, join="inner")

    all_invalid_names_df.to_excel("Invalid names.xlsx")