import numpy as np
import os
import pandas as pd
from players_cleaning import clean_team

def get_new_parameters(stat, params, position, years, game_logs_df, week=None):
    new_params = None
    if week is not None:
        years = [2021, 2022, "Total"]
        new_params = params[params["Year"] not in years]

    if stat == "Passing yards" or stat == "Passing completions" or stat == "Passing attempts":
        column = "YDS" if stat == "Passing yards" else ("COMP" if stat == "Passing completions" else "ATT")        
        for year in years:
            m0 = list(params[params["Year"] == year]["m"])[0]
            k0 = list(params[params["Year"] == year]["k"])[0]
            a0 = list(params[params["Year"] == year]["a"])[0]
            b0 = list(params[params["Year"] == year]["b"])[0]
            data = None
            if week is None:
                data = np.array(game_logs_df[column]) if year == "Total" else np.array(game_logs_df[game_logs_df["Year"] == year][column])
            else:
                data = np.array(game_logs_df[(game_logs_df["Year"] == 2022) & (game_logs_df["Week"] == week)][column])
            n = np.shape(data)[0]
            xbar = 0 if n == 0 else np.mean(data)
            s = 0 if n == 1 else np.sqrt((1/(n - 1)) * np.sum((data - xbar)**2)) 
            k1 = k0 + n
            a1 = a0 + n/2
            m1 = m0 if n == 0 else (k0 * m0 + n * xbar) / k1
            b1 = b0 if n == 0 else b0 + 0.5 * (n - 1) * (s**2) + (k0 * n * ((xbar - m0)**2)) / (2 * k1)
            updated = pd.DataFrame({"Year": [year], "m": [m1], "k": [k1], "a": [a1], "b": [b1]})
            if new_params is None:
                new_params = updated
            else:
                new_params = pd.concat([updated, new_params], axis=0)

    elif (stat == "Receiving yards" and (position == "WR" or position == "TE")) or (stat == "Rushing yards" and position == "RB"):
        for year in years:
            a0 = list(params[params["Year"] == year]["a"])[0]
            b0 = list(params[params["Year"] == year]["b"])[0]
            rec_yards = None
            if week is None:
                rec_yards = np.array(game_logs_df["YDS"]) if year == "Total" else np.array(game_logs_df[game_logs_df["Year"] == year]["YDS"])
            else:
                rec_yards = np.array(game_logs_df[(game_logs_df["Year"] == 2022) & (game_logs_df["Week"] == week)]["YDS"])
            a1 = a0 + np.shape(rec_yards)[0]
            b1 = b0 + 0.5 * np.sum(rec_yards**2)
            updated = pd.DataFrame({"Year": [year], "a": [a1], "b": [b1]})
            if new_params is None:
                new_params = updated
            else:
                new_params = pd.concat([updated, new_params], axis=0)

    elif (stat == "Receiving yards" and position == "RB") or (stat == "Rushing yards" and (position == "QB" or position == "WR")):
        column = "RECYDS" if stat == "Receiving yards" else "RYDS"
        for year in years:
            yards = np.clip(np.array(game_logs_df[column]) if year == "Total" else np.array(game_logs_df[game_logs_df["Year"] == year][column]), a_min=1/np.exp(1), a_max=None)
            N = np.shape(yards)[0]
            S = np.sum(yards)
            L = np.sum(np.log(yards))
            M = np.sum(yards * np.log(yards))
            ahat = 1
            bhat = 1
            if N == 1:
                ahat = S
            elif N > 1:
                ahat = 1 if (N * M - S*L) == 0 else (N*S) / (N * M - S*L)
                bhat = 1 if (N * M - S*L) == 0 else N**2 / (N*M - S*L)
            updated = pd.DataFrame({"Year": [year], "ahat": [ahat], "bhat": [bhat]})
            if new_params is None:
                new_params = updated
            else:
                new_params = pd.concat([updated, new_params], axis=0)

    else:
        column = None
        if stat == "Passing touchdowns" or (stat == "Rushing touchdowns" and position == "RB") or (stat == "Receiving touchdowns" and (position == "WR" or position == "TE")):
            column = "TD"
        elif stat == "Interceptions":
            column = "INT"
        elif (stat == "Rushing touchdowns" and (position == "QB" or position == "WR")):
            column = "RTD"
        elif stat == "Receptions":
            column = "REC"
        elif stat == "Receiving touchdowns" and position == "RB":
            column = "RECTD"
        else:
            column = "LOST"

        for year in years:
            a0 = list(params[params["Year"] == year]["a"])[0]
            b0 = list(params[params["Year"] == year]["b"])[0]
            data = None
            if week is None:
                data = np.array(game_logs_df[column]) if year == "Total" else np.array(game_logs_df[game_logs_df["Year"] == year][column])
            else:
                data = np.array(game_logs_df[(game_logs_df["Year"] == 2022) & (game_logs_df["Week"] == week)][column])
            a1 = a0 + np.sum(data)
            b1 = b0 + np.shape(data)[0]
            updated = pd.DataFrame({"Year": [year], "a": [a1], "b": [b1]})
            if new_params is None:
                new_params = updated
            else:
                new_params = pd.concat([updated, new_params], axis=0)

    return new_params

def get_initial_parameters(stat, position, years):
    if stat == "Passing yards":
        # M = list()
        # K = list()
        # A = list()
        # B = list()
        # for i in range(0, len(years)):
        #     K.append(0)
        #     A.append(0)
        #     B.append(0)
        #     if i == 0 or years[i] == "Total":
        #         M.append(233)
        #     else:
        #         prev_year_data = list(game_logs_df[game_logs_df["Year"] == years[i] - 1]["YDS"])
        #         if len(prev_year_data) == 0:
        #             M.append(233)
        #         else:
        #             M.append(np.mean(prev_year_data))
        return pd.DataFrame({"Year": years[::-1], "m": np.full(len(years), 233), "k": np.full(len(years), 1), "a": np.full(len(years), 0.5), "b": np.full(len(years), 0.5)})

    elif (stat == "Receiving yards" and (position == "WR" or position == "TE")) or (stat == "Rushing yards" and position == "RB"):
        return pd.DataFrame({"Year": years[::-1], "a": np.full(len(years), 1), "b": np.full(len(years), 1)})
        # A = list()
        # B = list()
        # for i in range(0, len(years)):
        #     if i == 0 or years[i] == "Total":
        #         A.append(0)
        #         B.append(0)
        #     else:
        #         prev_year_data = list(game_logs_df[game_logs_df["Year"] == years[i] - 1]["YDS"])
        #         if len(prev_year_data) == 0:
        #             A.append(0)
        #             B.append(0)
        #         else:

    elif (stat == "Receiving yards" and position == "RB") or (stat == "Rushing yards" and (position == "QB" or position == "WR")):
        return pd.DataFrame({"Year": years[::-1], "ahat": np.full(len(years), 1), "bhat": np.full(len(years), 1)})

    elif stat == "Passing completions":
        return pd.DataFrame({"Year": years[::-1], "m": np.full(len(years), 20), "k": np.full(len(years), 1), "a": np.full(len(years), 0.5), "b": np.full(len(years), 0.5)})
    
    elif stat == "Passing attempts":
        return pd.DataFrame({"Year": years[::-1], "m": np.full(len(years), 30), "k": np.full(len(years), 1), "a": np.full(len(years), 0.5), "b": np.full(len(years), 0.5)})

    else:
        return pd.DataFrame({"Year": years[::-1], "a": np.full(len(years), 1), "b": np.full(len(years), 1)})

def update_parameters(position, section, stats, initialize=False, week=None):
    for team in os.listdir("Teams"):
        for filename in os.listdir("Teams/" + team + "/" + section + "/" + position):
            full_path = "Teams/" + team + "/" + section + "/" + position + "/" + filename
            file = None
            try:
                file = pd.ExcelFile(full_path)
            except:
                clean_team(team)
                print(team + " cleaned")
                file = pd.ExcelFile(full_path)
            game_logs_df = file.parse("Game logs")
            try:
                game_logs_df.drop(columns="Unnamed: 0", inplace=True)
            except:
                None
            other_sheets = list()
            for sheet in file.sheet_names:
                if sheet != "Game logs" and sheet.replace(" parameters", "") not in stats:
                    other_sheets.append([file.parse(sheet).drop(columns="Unnamed: 0"), sheet])
            years = [] if game_logs_df.shape[0] == 0 else list(game_logs_df["Year"].value_counts().index)
            years.sort()
            years.append(2022)
            years.append("Total")

            if initialize is True:
                initial_params = list()
                for stat in stats:
                    initial_params.append([get_initial_parameters(stat, position, years), stat])
                with pd.ExcelWriter(full_path) as writer:
                    game_logs_df.to_excel(writer, sheet_name="Game logs")
                    for stat in initial_params:
                        stat[0].to_excel(writer, sheet_name=stat[1] + " parameters")
                    for sheet in other_sheets:
                        sheet[0].to_excel(writer, sheet_name=sheet[1])
                file = pd.ExcelFile(full_path)
            
            if game_logs_df.shape[0] != 0:
                new_params = list()
                for stat in stats:
                    params = file.parse(stat + " parameters")            
                    new_params.append([get_new_parameters(stat, params, position, years, game_logs_df, week=week), stat])
                with pd.ExcelWriter(full_path) as writer:
                    game_logs_df.to_excel(writer, sheet_name="Game logs")
                    for stat in new_params:
                        stat[0].to_excel(writer, sheet_name=stat[1] + " parameters")
                    for sheet in other_sheets:
                        sheet[0].to_excel(writer, sheet_name=sheet[1])

valid_stats = ["Passing yards", "Rushing yards", "Receiving yards", "Passing touchdowns", "Rushing touchdowns",
               "Receiving touchdowns", "Rushing touchdowns", "Interceptions", "Passing attempts", "Passing completions",
               "Fumbles lost"]

# update_parameters("QB", "Offense", ["Passing yards", "Passing attempts", "Passing completions", "Passing touchdowns", "Interceptions", 
#                           "Rushing yards", "Rushing touchdowns", "Fumbles lost"], initialize=True)
# # update_parameters("WR", "Offense", ["Receiving yards", "Rushing yards", "Receptions", "Receiving touchdowns", 
# #                           "Rushing touchdowns", "Fumbles lost"], initialize=True)
# # update_parameters("RB", "Offense", ["Receiving yards", "Rushing yards", "Receptions", "Receiving touchdowns", 
# #                           "Rushing touchdowns", "Fumbles lost"], initialize=True)
# update_parameters("TE", "Offense", ["Receiving yards", "Receptions", "Receiving touchdowns", "Fumbles lost"], initialize=True)