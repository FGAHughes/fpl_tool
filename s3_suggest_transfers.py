import pandas as pd
from functions.pp_in_x_gws_func import pp_next_x_all
from functions.get_my_players_func import get_my_players
from functions.calc_xi_func import calc_xi_bench

pd.set_option('display.width', 400)
pd.set_option('display.max_columns', 100)

event_data = pd.read_csv('../s1_access_api/event_data.csv')  # retrieving overall gameweek (event) data
current_gameweek = event_data.is_current.ne(
    False).idxmax() + 1  # finding the first occurrence where gw finished = False to return the current gameweek

# input your ID below (inserted as a default is mine)
my_id = 759948

# This function returns the manager above's players with the player's unaltered ID's, and the manager's funds available
my_players_df, my_bank = get_my_players(my_id)

# Using the variable below, choose how many gameweeks you would like to return data from.
# I would recommend not bringing a player that you don't have an at least 3-5 gameweek plan for
game_weeks = 1
players_pp_for_x = pp_next_x_all(game_weeks)

# This sorts players by their predicted points over the next x gameweeks
pr_by_points = players_pp_for_x.copy()
pr_by_points.sort_values(by='predicted_points', ascending=False, inplace=True)
pr_by_points.reset_index(drop=True, inplace=True)

# because the players returned in my_players use the API's indexes, we must change them into our created IDs
elements_key = pd.read_csv('../s1_access_api/elements_key.csv')
elements_data = pd.read_csv('../s1_access_api/elements_data.csv')

# creating a dataframe that will store recommended players and their data
recommended_players = pd.DataFrame(columns=['outgoing_name',
                                            'outgoing_ID',
                                            'incoming_name',
                                            'incoming_ID',
                                            'predicted_points',
                                            'avg_points',
                                            'point_difference',
                                            'cost',
                                            'Notes'])

# We create a df that counts how many player's from each team we have as we can only have max 3 per team
team_data = {'team': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
             'count': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}
team_count = pd.DataFrame(team_data)  # a df that stores the number of players from each pl team

for index, row in my_players_df.iterrows():
    # converting each player in the team's ID from the original to our created ID
    old_id = row['element']
    old_id_idx = elements_key.index.get_loc(elements_key[elements_key['old_id'] == old_id].index[0])
    my_players_df.iloc[index, 0] = old_id_idx
    players_team = elements_data.iloc[old_id_idx, 2]
    my_players_df.iloc[index, 5] = players_team  # adding each player's team to the df
    team_count.iloc[players_team - 1, 1] += 1  # totalling how many players from each team there are
    player_pp = players_pp_for_x.iloc[old_id_idx, 2]
    my_players_df.iloc[index, 6] = player_pp  # adding each player's predicted points
    player_position = elements_data.iloc[old_id_idx, 3]
    my_players_df.iloc[index, 1] = player_position  # adding each player's position

# for each player, we add their data to the recommended_players dataframe. We make sure that only available and
# affordable players are recommended. The recommendations are then ranked by how many extra points they would give you
# over the next given number of gameweeks

# This loop iterates through each of the players in the managers teams and calculates whether it is worth transferring
# out the manager's player for another player for the next x gameweeks, given that they are 1. affordable, 2. predicted
# more points, 3. the same position, 4. not exceeding the limit of 3 players from a single team and 5. not already in
# managers team.
for index, row in my_players_df.iterrows():  # for each of the manager's players, return position, pp and name
    player_position = elements_data.iloc[row['element'], 3]
    player_pp = players_pp_for_x.iloc[row['element'], 2]
    player_name = players_pp_for_x.iloc[row['element'], 1]

    # we only make 3 recommendations per player and use this to ensure that
    recommendations = 1
    for index2, row2 in pr_by_points.iterrows():
        if recommendations <= 3:
            budget = elements_data.iloc[
                         row['element'], 13] + my_bank  # price of outgoing player + existing budget available
            cost = elements_data.iloc[(row2['id']), 13]  # price of incoming player
            players_team = elements_data.iloc[row2['id'], 2]
            # check that we don't already have 3 players from the current player being processed's team
            team_player_count = team_count.iloc[players_team - 1, 1]
            if team_player_count >= 3:
                continue
            else:
                # only recommending players for each player that play the same position, are affordable, are not already
                # owned and are predicted more points the player we own
                if row2['position'] == player_position and budget > cost and row2['predicted_points'] > player_pp and (
                        (row2['id'] not in my_players_df.values[:, 0])):
                    outgoing_name = player_name
                    outgoing_id = row['element']
                    outgoing_pp = player_pp
                    incoming_name = row2['player']
                    incoming_id = row2['id']
                    incoming_pp = row2['predicted_points']
                    incoming_ap = row2['avg_points']
                    point_difference = incoming_pp - outgoing_pp
                    recommendations += 1
                    recommended_players.loc[len(recommended_players)] = (
                        outgoing_name, outgoing_id, incoming_name, incoming_id,
                        incoming_pp, incoming_ap, point_difference, cost, 'None')

                else:
                    continue
        else:
            break
my_players = my_players_df.copy()
my_players.drop(['team', 'position', 'multiplier', 'is_captain', 'is_vice_captain', 'pp'], axis=1, inplace=True)
my_players.to_csv(f'id_players/{my_id}_players.csv', index=False)

# Finally we display the recommended players, ranked by how many extra points they would earn you over the next
# given number of gameweeks. It's worth noting that if your player is unavailable, their predicted points are 0 and as
# such this will skew the point difference, although these may not be the best transfers to make.
# print(team_count)
print('The best transfers you can afford this week are: ')
recommended_players.sort_values(by='point_difference', inplace=True, ascending=False)
print(recommended_players.head(100))
print(f'The best players to bring in for the next {game_weeks} gameweek(s) are: ')
best_players = pd.concat([pr_by_points.groupby('position').get_group(4).head(6).drop(['xA_avg', 'xG_avg'], axis=1),
                            pr_by_points.groupby('position').get_group(3).head(10).drop(['xA_avg', 'xG_avg'], axis=1),
                            pr_by_points.groupby('position').get_group(2).head(10).drop(['xA_avg', 'xG_avg'], axis=1),
                            pr_by_points.groupby('position').get_group(1).head(4).drop(['xA_avg', 'xG_avg'], axis=1)],
                         axis=0)

print(best_players)

# creating suggested xi
starting_xi, bench = calc_xi_bench(my_players_df, elements_data)

print("Your team should be: ")
print(starting_xi)
print('Your bench should be: ')
print(bench)
