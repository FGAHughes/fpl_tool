import requests
import pandas as pd

# Bootstrap-static contains every premier league player (element) and general data about them.
# We connect to the api and return the data we need
main_response = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/')
elements_data = pd.json_normalize(main_response.json(), record_path='elements')
elements_data = elements_data[['id',
                               'web_name',
                               'team',
                               'element_type',
                               'goals_scored',
                               'assists',
                               'goals_conceded',
                               'expected_goals',
                               'expected_assists',
                               'expected_goals_conceded',
                               'saves_per_90',
                               'starts',
                               'chance_of_playing_next_round',
                               'now_cost',
                               'minutes',
                               'status']]


# Next we fetch overall fixture data.
# This will be used much later, but it's better to do it at the same time.
main_response = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/')
event_data = pd.json_normalize(main_response.json(), record_path='events')
event_data.to_csv('event_data.csv', index=False)

# The elements are given IDs from 1 to 830, but some digits are skipped.
# So we create a key which will be used to translate the original IDs into the new IDs we will create later
elements_key = pd.DataFrame(columns=['new_id', 'old_id'])
new_id = 0

for index, row in elements_data.iterrows():
    id = row['id']
    # add old and new ID's to the key
    elements_key.loc[len(elements_key)] = new_id, id
    # replace old ID's with new ID's in elements_data
    elements_data.iloc[index, 0] = new_id

    # Next we access each elements' detailed data, which is organised by gameweek in 'history' (which we rename stats)
    # and by game in fixtures
    player_response = requests.get(f'https://fantasy.premierleague.com/api/element-summary/{id}/')
    player_fixtures_df = pd.json_normalize(player_response.json(), record_path='fixtures')
    player_stats_df = pd.json_normalize(player_response.json(), record_path='history')

    # The fixture dataframes we receive don't explicitly state which team they are against in each fixture. So we add
    # this by creating a column that contains a list of both teams in the fixture and then return the team that does not
    # equal the player's team, adding this to a 'vs' column
    players_team = elements_data.iloc[index, 2]
    player_fixtures_df.rename(columns={'code': 'teams'}, inplace=True)  # renaming a preexisting, unuseful column
    player_fixtures_df['teams'] = player_fixtures_df[['team_h', 'team_a']].values.tolist()
    player_fixtures_df['vs'] = [t[1] if t[0] == players_team else t[0] for t in player_fixtures_df['teams']]  # t = team

    player_fixtures_df.to_csv(f'csvs/player_fixtures_csvs/{new_id}_fix.csv', index=False)
    player_stats_df.to_csv(f'csvs/player_stats_csvs/{new_id}_stats.csv', index=False)
    new_id += 1

# Players unlikely to play the next round despite being fit have empty values,
# so we set these as 0% likelihood of playing
elements_data['chance_of_playing_next_round'] = elements_data['chance_of_playing_next_round'].fillna(0)
elements_data.to_csv('elements_data.csv', index=False)
elements_key.to_csv('elements_key.csv', index=False)
