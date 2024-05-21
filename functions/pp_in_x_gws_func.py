import pandas as pd


pd.set_option('display.width', 400)
pd.set_option('display.max_columns', 100)
pd.set_option('display.max_rows', 400)


# A function that return each player and their predicted points for a given number of gameweeks
def pp_next_x_all(x_gws):
    elements_data = pd.read_csv('../s1_access_api/elements_data.csv')
    total_players = len(elements_data)
    # creating a new df to hold the data
    players_pp_for_x = pd.DataFrame(columns=['id', 'player', 'predicted_points', 'position', 'xG_avg', 'xA_avg',
                                             'avg_points', 'cost'])

    # retrieving overall gameweek (event) data
    event_data = pd.read_csv('../s1_access_api/event_data.csv')
    injured_players = []  # this is to check if unavailable players are being correctly processed
    for i in range(total_players):
        player_fix = pd.read_csv(f'../s1_access_api/player_fixtures_csvs/{i}_fix.csv')

        # create variables that will store the sum of xg, xa and predicted points
        xg = 0
        xa = 0
        pp = 0
        current_gameweek = event_data.is_current.ne(False).idxmax() + 1
        starting_gameweek = event_data.is_current.ne(False).idxmax() + 1
        # The difference between these two is that the value stored in starting_gameweek will not be altered, whereas
        # the value of current_gameweek will always equal the gameweek of the fixture we are processing
        max_gameweek = current_gameweek + x_gws  # the gameweeks we would like to return data up to

        # This loop iterates through each player's fixtures and sums the xg, xa and pp in the given numbers of gameweeks
        for index, row in player_fix.iterrows():
            # if the player's next fixture is the natural next gameweek within the gameweek range we want data from
            if starting_gameweek == row['event']:
                current_gameweek += 1
            elif row['event'] == current_gameweek + 1 and row['event'] <= max_gameweek:
                xg += row['xG']
                xa += row['xA']
                pp += row['predicted_points']
                current_gameweek += 1
            # if the player's next fixture is the second game in a double gameweek
            elif row['event'] == current_gameweek and row['event'] <= max_gameweek:
                xg += row['xG']
                xa += row['xA']
                pp += row['predicted_points']
            # blank fixtures don't show up on the fixtures data, so we check that there wasn't at least one blank
            # gameweek between the current gameweek and the next fixture
            elif row['event'] != current_gameweek and row['event'] != current_gameweek + 1 and row['event'] <= max_gameweek:
                gw_difference = row['event'] - current_gameweek
                current_gameweek += gw_difference
                if row['event'] <= max_gameweek:
                    xg += row['xG']
                    xa += row['xA']
                    pp += row['predicted_points']
                else:
                    break
            else:
                break

        id = elements_data.iloc[i, 0]  # player's ID
        name = elements_data.iloc[i, 1]  # player's displayed name
        position = elements_data.iloc[i, 3]  # player's position

        xg = xg / x_gws  # predicted average xG over the next given number of gameweeks
        xa = xa / x_gws  # same for assists and then points
        avg_points = pp / x_gws

        # if player is not available, pp = 0
        player_stats_data = pd.read_csv(f'../s1_access_api/player_stats_csvs/{i}_stats.csv')
        minutes_in_last_3 = player_stats_data.iloc[len(player_stats_data) - 3: len(player_stats_data), 9].sum() / 3
        if 1 < elements_data.iloc[i, 12] < 75 or (
                minutes_in_last_3 < 60 and elements_data.iloc[i, 12] == 0) or (
                elements_data.iloc[i, 12] == 0 and elements_data.iloc[i, 15] != 'a'):
            pp = 0
            xg = 0
            xa = 0
            avg_points = 0
            injured_players.append(elements_data.iloc[i, 1])
        else:
            pass
        price = elements_data.iloc[i, 13]  # the price of the player

        # add the data to a single row dataframe that we will later append to the whole dataframe
        players_pp_for_x.loc[len(players_pp_for_x)] = id, name, pp, position, xg, xa, avg_points, price

    return players_pp_for_x

# import numpy as np
# players_ranked, fwd_players, mid_players, def_players, gk_players = pp_next_x_all(1)
# # print(fwd_players.head(5))
# # # print(mid_players.head(10))
# # print(def_players.head(50))
# print(gk_players.head(500))
# print(players_ranked.head(300))
#
# def pp_next_x_indv(x, id):
#     global avg_points, position, team, name, cost
#     elements_data = pd.read_csv('../s1_access_api/elements_data.csv')
#     total_players = len(elements_data)
#     # creating a new df to hold the data
#     players_ranked = pd.DataFrame(columns=['id', 'player', 'predicted_points', 'position', 'xG_avg', 'xA_avg',
#                                            'avg_points', 'cost'])
#
#     # retrieving overall gameweek (event) data
#     event_data = pd.read_csv('../s1_access_api/event_data.csv')
#     injured_players = []  # this is to check if unavailable players are being correctly processed
#
#     player_fix = pd.read_csv(f'../s1_access_api/player_fixtures_csvs/{id}_fix.csv')
#     xg = 0
#     xa = 0
#     pp = 0  # predicted points
#     gameweeks_used = []  # this is to check that the correct gameweeks are being processed
#     current_gameweek = event_data.is_current.ne(False).idxmax() + 1  # returns the current gameweek
#     starting_gameweek = event_data.is_current.ne(False).idxmax() + 1
#     max_gameweek = current_gameweek + x  # the gameweeks we would like to return data up to
#     for index, row in player_fix.iterrows():
#         # if the player's next fixture is the natural next gameweek within the gameweek range we want data from
#         if starting_gameweek == row['event']:
#             current_gameweek += 1
#         elif row['event'] == current_gameweek + 1 and row['event'] <= max_gameweek:
#             xg += row['xG']
#             xa += row['xA']
#             pp += row['predicted_points']
#             current_gameweek += 1
#             gameweeks_used.append(row['event'])
#         # if the player's next fixture is the second game in a double gameweek
#         elif row['event'] == current_gameweek and row['event'] <= max_gameweek:
#             xg += row['xG']
#             xa += row['xA']
#             pp += row['predicted_points']
#             gameweeks_used.append(row['event'])
#         # blank fixtures don't show up on the fixtures data, so we check that there wasn't at least one blank
#         # gameweek between the current gameweek and the next fixture
#         elif row['event'] != current_gameweek and row['event'] != current_gameweek + 1 and row[
#             'event'] <= max_gameweek:
#             gw_difference = row['event'] - current_gameweek
#             current_gameweek += gw_difference
#             if row['event'] <= max_gameweek:
#                 xg += row['xG']
#                 xa += row['xA']
#                 pp += row['predicted_points']
#                 gameweeks_used.append(row['event'])
#             else:
#                 break
#         else:
#             break
#
#         name = elements_data.iloc[id, 1]  # player's displayed name
#         position = elements_data.iloc[id, 3]  # player's position
#         team = elements_data.iloc[id, 2]
#
#         xg = xg / x  # predicted average xG over the next given number of gameweeks
#         xa = xa / x  # same for assists and then points
#         avg_points = pp / x
#         # if player is not available, pp = 0
#         if elements_data.iloc[id, 12] < 75:
#             pp = 0
#             xg = 0
#             xa = 0
#             avg_points = 0
#             injured_players.append(elements_data.iloc[id, 1])
#         else:
#             pass
#         cost = elements_data.iloc[id, 13]
#
#     player_data = np.array([id, name, position, team, pp, cost])
#     return player_data

