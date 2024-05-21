import pandas as pd
import requests


# This is a function that returns a given managers fpl team in a dataframe, and their available budget
def get_my_players(my_id):
    event_data = pd.read_csv('../s1_access_api/event_data.csv')  # retrieving overall gameweek (event) data


    current_gameweek = event_data.is_current.ne(
        False).idxmax() + 1  # returning the current gw by finding the first occurrence where gw finished = False

    # To avoid returning a managers team on a week that they free hit, we return check for the free hit chip and if
    # active, we return the players from the gameweek prior.
    # This return's my_id's team from the current gameweek
    response = requests.get(f'https://fantasy.premierleague.com/api/entry/{my_id}/event/{current_gameweek}/picks/')
    my_data = pd.json_normalize(response.json())
    my_chip = my_data.iloc[0, 0]  # This returns the chip active the most recent gameweek, if there is one
    if my_chip == 'freehit':  # if free hit was active, then return players from the gameweek prior
        response = requests.get(
            f'https://fantasy.premierleague.com/api/entry/{my_id}/event/{current_gameweek - 1}/picks/')
        my_data = pd.json_normalize(response.json())
    else:
        pass

    my_players_df = pd.json_normalize(response.json(),
                                      record_path='picks')  # returns df of my 15 players from last non-free hit gw
    my_players_df.reset_index(drop=True, inplace=True)
    my_bank = my_data.iloc[0, 10]  # returns money left in the bank

    my_players_df.sort_values(by='element', inplace=True)  # sorting in the order they would appear in elements_data
    my_players_df['team'] = 0  # adding columns that will be useful later
    my_players_df['pp'] = 0
    return my_players_df, my_bank  # return useful elements
