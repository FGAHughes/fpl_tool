import pandas as pd
import warnings
from functions.predict_points_func import retrieve_team_data, retrieve_opp_data, retrieve_player_data, predict_points

# This is optional but the program is still fully functional as long as you are using Pandas 3.2.2 or prior
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=RuntimeWarning)

pd.set_option('display.width', 400)
pd.set_option('display.max_columns', 100)

# We fetch data from each team which is not available through the fpl api
tables = pd.read_html('https://fbref.com/en/comps/9/Premier-League-Stats', header=1)
team_data = tables[2]  # data of each team
vs_team_data = tables[3]  # the data of all teams against a specific team
goalkeeper_data = tables[4]  # gk relevant defensive data for each team
vs_goalkeeper_data = tables[5]  # gk relevant defensive data of all teams against a specific team
shooting_data = tables[8]  # the shooting/attacking data of each team
team_data.sort_values(by='Squad', ascending=True)
vs_team_data.sort_values(by='Squad', ascending=True)
# We sort alphabetically so that the indexes are the same as the team numbers

elements_data = pd.read_csv('../s1_access_api/elements_data.csv')
# # create csvs for team data
# team_data.to_csv('team_data/team_data.csv', index=False)
# vs_team_data.to_csv('team_data/against_team_data.csv', index=False)
# goalkeeper_data.to_csv('team_data/goalkeeper_data.csv', index=False)
# vs_goalkeeper_data.to_csv('team_data/vs_goalkeeper_data.csv', index=False)

# This loop iterates through each player and predicts their points
total_players = len(elements_data)
for i in range(total_players):
    # returning player's team
    team_id = elements_data.iloc[i, 2] - 1

    # accessing player's fixture and previous statistics data
    player_fixtures_data = pd.read_csv(f'../s1_access_api/player_fixtures_csvs/{i}_fix.csv')
    player_stats_data = pd.read_csv(f'../s1_access_api/player_stats_csvs/{i}_stats.csv')
    name = elements_data.iloc[i, 1]

    # We calculate average minutes played in the last 3 game_weeks
    # This is used in place of average minutes across the season for some things
    # as it is more representative of recent fixtures
    minutes_in_last_3 = player_stats_data.iloc[len(player_stats_data)-3: len(player_stats_data), 9].sum()/3


    df_list_for_func = [team_data, vs_team_data, goalkeeper_data, player_fixtures_data, shooting_data, elements_data]
    # This list contains all the dataframes that we need for later functions.
    # We keep them in a list so that we can enter it as a single parameter in the function.
    # I chose to set it in the loop because player_fixture_data changes per iteration

    # The below calculates the player's average minutes a game by dividing minutes by total games played.
    # Total games played is calculated by returning how many fixtures the played 0 minutes and subtracting from total
    # games they were available for.
    # This returns an error if they played every game, so we add a try except
    try:
        games_played = len(player_stats_data) - player_stats_data['minutes'].value_counts()[0]

    except:
        games_played = len(player_stats_data)
    avg_minutes = float(elements_data.iloc[i, 14]) / games_played  # total minutes / games played

    # adding columns to hold useful data in each player's fixture data
    player_fixtures_data['team_xG'] = 0  # their team's expected goals
    player_fixtures_data['team_xGC'] = 0  # their team's expected goals conceded
    player_fixtures_data['opp_xG'] = 0  # opponent team's xG
    player_fixtures_data['opp_xGC'] = 0
    player_fixtures_data['fix_xGC'] = 0  # player's team's expected goals conceded in the fixture
    player_fixtures_data['P(G=0)'] = 0  # probability GC = 0
    player_fixtures_data['predicted_points'] = 0  # each player's predicted points for each fixture
    player_fixtures_data['xG'] = 0  # each player's predicted points for each fixture
    player_fixtures_data['xA'] = 0  # each player's predicted points for each fixture

    # Making another list that we will use in the function
    team_stats_ls = retrieve_team_data(team_id, df_list_for_func)

    # In this loop iterate through each player's fixtures, adding data to the dataframes and calculating predicted points
    for index, row in player_fixtures_data.iterrows():
        player_fixtures_data.iloc[index, 15] = team_stats_ls[2]
        # adding their team's expected goals to column team_xG
        player_fixtures_data.iloc[index, 16] = team_stats_ls[3]
        # adding their team's expected goals against to column team_xGA

        # for each fixture we return the relevant opponent data
        opp_idx = player_fixtures_data.iloc[index, 14] - 1  # opponent team's index
        opp_stats_ls = retrieve_opp_data(opp_idx, df_list_for_func, team_stats_ls)  # list containing useful opp data

        # We predict expected goals conceded (xGC) for each team in the fixture by averaging team xGC and opp xG
        fix_xgc = (team_stats_ls[3] + opp_stats_ls[1]) / 2

        # Calculate clean sheet (CS) chance for player's team in each fixture using Poisson distribution,
        # aka the probability goals conceded = 0 (P(G=0))
        cs_chance = 2.718281828459045 ** (-(fix_xgc))

        # We create a list of useful stats and dataframes to pass into a later function
        player_stats_ls = retrieve_player_data(df_list_for_func, i, games_played)
        player_stats_ls.append(minutes_in_last_3)
        player_stats_ls.append(avg_minutes)
        player_stats_ls.append(cs_chance)
        player_stats_ls.append(fix_xgc)
        data_lists = [team_stats_ls, opp_stats_ls, player_stats_ls, elements_data]  # and add it to the data lists

        # using the point predictor function, we predict the player's expected points for each gameweek
        predicted_points, pxgim, pxaim = predict_points(i, data_lists)
        # pxgim = player's expected goals in match, pxaim = player's expected assists in match

        player_fixtures_data.iloc[index, 17] = opp_stats_ls[1]  # add opponent's average xG to column opp_xG
        player_fixtures_data.iloc[index, 18] = opp_stats_ls[2]  # add opponent's average xGC to column opp_xGC
        player_fixtures_data.iloc[index, 19] = fix_xgc  # add opponent's xGC in the fixture to column fix_xGC
        player_fixtures_data.iloc[index, 20] = cs_chance  # add team's clean sheet chance column P(G=0)
        player_fixtures_data.iloc[index, 21] = predicted_points  # add pp to predicted_points column
        player_fixtures_data.iloc[index, 22] = pxgim  # add pxgim to pxgim column
        player_fixtures_data.iloc[index, 23] = pxaim  # add pxaim to pxaim column

        # adding a running total of predicted points gameweek on gameweek
        player_fixtures_data['pp_cumsum'] = player_fixtures_data['predicted_points'].cumsum()

    player_fixtures_data.to_csv(f'../s1_access_api/player_fixtures_csvs/{i}_fix.csv', index=False)

