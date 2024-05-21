import pandas as pd
from pp_in_x_gws_func import pp_next_x_all


def calc_xi_bench(my_players_df, elements_data):
    available_players = my_players_df.copy()
    available_players.reset_index(drop=True, inplace=True)
    # available_players.sort_values(by=['position', 'pp'], ascending=False, inplace=True)
    players_pp = pp_next_x_all(1)
    available_players['name'] = 'None'
    for index, row in available_players.iterrows():
        available_players.iloc[index, 6] = players_pp.iloc[row['element'], 2]
        available_players.iloc[index, [0, 7]] = elements_data.iloc[row['element'], [0, 1]]

    available_players.sort_values(by=['position', 'pp'], ascending=False, inplace=True)
    available_players.reset_index(drop=True, inplace=True)
    starting_xi = pd.DataFrame(columns=['element', 'position', 'multiplier', 'is_captain', 'is_vice_captain',
                                        'team', 'pp', 'name'])
    bench = pd.DataFrame(columns=['element', 'position', 'multiplier', 'is_captain', 'is_vice_captain', 'team',
                                  'pp', 'name'])

    starting_xi.loc[len(starting_xi)] = available_players.iloc[0, :]
    starting_xi.loc[len(starting_xi)] = available_players.iloc[3, :]
    starting_xi.loc[len(starting_xi)] = available_players.iloc[4, :]
    starting_xi.loc[len(starting_xi)] = available_players.iloc[8, :]
    starting_xi.loc[len(starting_xi)] = available_players.iloc[9, :]
    starting_xi.loc[len(starting_xi)] = available_players.iloc[10, :]
    starting_xi.loc[len(starting_xi)] = available_players.iloc[13, :]

    bench.loc[len(bench)] = available_players.iloc[14, :]

    available_players.drop([0, 3, 4, 8, 9, 10, 13, 14], axis=0, inplace=True)

    available_players.sort_values(by='pp', ascending=False, inplace=True)

    for i in range(4):
        starting_xi.loc[len(starting_xi)] = available_players.iloc[i, :]
    for j in range(4, 7):
        bench.loc[len(bench)] = available_players.iloc[j, :]

    starting_xi.sort_values(by=['position', 'pp'], ascending=False, inplace=True)
    starting_xi.drop(columns=['is_captain', 'is_vice_captain', 'multiplier'], inplace=True)
    bench.drop(columns=['is_captain', 'is_vice_captain', 'multiplier'], inplace=True)
    starting_xi = starting_xi[['element', 'name', 'position', 'team', 'pp']]
    bench = bench[['element', 'name', 'position', 'team', 'pp']]
    return starting_xi, bench
