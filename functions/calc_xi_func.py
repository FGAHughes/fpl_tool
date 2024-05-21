import pandas as pd
from pp_in_x_gws_func import pp_next_x_all

# a function to calculate your optimal starting XI based on the players you owned last non free-hit gameweek
def calc_xi_bench(my_players_df, elements_data):
    available_players = my_players_df.copy()
    available_players.reset_index(drop=True, inplace=True)
    players_pp = pp_next_x_all(1)  # returning points for next gameweek
    available_players['name'] = 'None'
    # a loop that adds predicted points, new IDs and players' names to your available players
    for index, row in available_players.iterrows():
        available_players.iloc[index, 6] = players_pp.iloc[row['element'], 2]  # adds predicted points
        available_players.iloc[index, [0, 7]] = elements_data.iloc[row['element'], [0, 1]]  # adds new ID and web name as it doesn't include the latter
    
    # sorting which of your players will perform the best in each position
    available_players.sort_values(by=['position', 'pp'], ascending=False, inplace=True)
    available_players.reset_index(drop=True, inplace=True)
    # creating dataframes to hold your starting XI and bench
    starting_xi = pd.DataFrame(columns=['element', 'position', 'multiplier', 'is_captain', 'is_vice_captain',
                                        'team', 'pp', 'name'])
    bench = pd.DataFrame(columns=['element', 'position', 'multiplier', 'is_captain', 'is_vice_captain', 'team',
                                  'pp', 'name'])

    # Because we have a set number of each position and require a set number of players of each position to start we can add players with the highest
    # predicted points by index to the starting XI
    starting_xi.loc[len(starting_xi)] = available_players.iloc[0, :]
    starting_xi.loc[len(starting_xi)] = available_players.iloc[3, :]
    starting_xi.loc[len(starting_xi)] = available_players.iloc[4, :]
    starting_xi.loc[len(starting_xi)] = available_players.iloc[8, :]
    starting_xi.loc[len(starting_xi)] = available_players.iloc[9, :]
    starting_xi.loc[len(starting_xi)] = available_players.iloc[10, :]
    starting_xi.loc[len(starting_xi)] = available_players.iloc[13, :]

    # and the same applies for the lower scoring goalkeeper
    bench.loc[len(bench)] = available_players.iloc[14, :]

    # removing players already added
    available_players.drop([0, 3, 4, 8, 9, 10, 13, 14], axis=0, inplace=True)

    # sorting the remaing players purely by predicted points
    available_players.sort_values(by='pp', ascending=False, inplace=True)

    # add the 4 best remaining players to the starting XI in order of highest predicted points
    for i in range(4):
        starting_xi.loc[len(starting_xi)] = available_players.iloc[i, :]
    # add the rest to the bench also in order of predicted points
    for j in range(4, 7):
        bench.loc[len(bench)] = available_players.iloc[j, :]
        
    # sort starting XI by position then points
    starting_xi.sort_values(by=['position', 'pp'], ascending=False, inplace=True)

    # remove unnecessary columns
    starting_xi.drop(columns=['is_captain', 'is_vice_captain', 'multiplier'], inplace=True)
    bench.drop(columns=['is_captain', 'is_vice_captain', 'multiplier'], inplace=True)
    starting_xi = starting_xi[['element', 'name', 'position', 'team', 'pp']]
    bench = bench[['element', 'name', 'position', 'team', 'pp']]
    return starting_xi, bench
