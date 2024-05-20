# This file contains functions that are essential for predicting a player's points

# This is a function that returns each team's useful data in a list
def retrieve_team_data(team_id, df_list_for_func):
    # adding useful data from fbref into each player's fixture dfs
    team_g = df_list_for_func[0].iloc[team_id, 8]  # player's team's total goals
    team_xg = df_list_for_func[0].iloc[team_id, 16]  # player's team's total expected goals
    team_ga = df_list_for_func[1].iloc[team_id, 8]  # player's team's total goals conceded (against)
    team_xga = df_list_for_func[1].iloc[team_id, 16]  # player's team's total expected goals conceded
    team_mp = df_list_for_func[0].iloc[team_id, 4]  # player's team's total matches played
    team_a = df_list_for_func[0].iloc[team_id, 9]  # player's team's total assists
    team_xa = df_list_for_func[0].iloc[team_id, 18]  # player's team's total expected assists
    team_sp = df_list_for_func[2].iloc[team_id, 10] / 100  # player's team's goalkeeper's save percentage
    team_sf = df_list_for_func[2].iloc[team_id, 8] / team_mp  # player's team's shots faced

    tgv = ((team_g + team_xg) / (2 * team_mp))  # team's goal value (a goal metric by average xG and G)
    tgav = (team_ga + team_xga) / (2 * team_mp)  # team's goals against value
    tav = (team_a + team_xa) / (2 * team_mp)  # team's assist value
    team_stats_ls = [team_sp, team_sf, tgv, tgav, tav, team_mp, team_id]
    return team_stats_ls


# This is a function that returns each player's useful data in a list
def retrieve_player_data(df_list_for_func, i, games_played):
    pxg = df_list_for_func[5].iloc[i, 7] / games_played  # player expected goals
    pg = df_list_for_func[5].iloc[i, 4] / games_played  # player goals
    pxav = df_list_for_func[5].iloc[i, 5] / games_played  # player expected assist value
    pxgv = (pxg + pg) / 2  # player expected assist value
    player_stats_ls = [pxav, pxgv]
    return player_stats_ls


# This is a function that returns each player's opponent's useful data in a list
def retrieve_opp_data(opp_idx, df_list_for_func, team_stats_ls):
    # for each fixture we return the relevant opponent data
    opp_g = df_list_for_func[0].iloc[opp_idx, 8]
    opp_xg = df_list_for_func[0].iloc[opp_idx, 16]
    opp_ga = df_list_for_func[1].iloc[opp_idx, 8]
    opp_xga = df_list_for_func[1].iloc[opp_idx, 16]
    opp_aa = df_list_for_func[1].iloc[opp_idx, 9]  # opponent's total assists conceded
    opp_xaa = df_list_for_func[1].iloc[opp_idx, 18]  # opponent's total expected assists conceded
    opp_mp = df_list_for_func[0].iloc[opp_idx, 4]

    # opponent's total shots per match = (team's total shots faced + opponent's total shots) / 2*mp
    opp_spm = (df_list_for_func[2].iloc[team_stats_ls[6], 8] / team_stats_ls[5] + df_list_for_func[4].iloc[opp_idx, 5] / opp_mp) / 2

    # determining an xG and xGC metric by averaging G and xG, and GC and xGC for each opponent
    ogv = (opp_g + opp_xg) / (2 * opp_mp)
    ogav = (opp_ga + opp_xga) / (2 * opp_mp)
    oaav = (opp_aa + opp_xaa) / (2 * opp_mp)
    opp_stats_ls = [opp_spm, ogv, ogav, oaav]
    return opp_stats_ls


# This is a function that calculates and returns a player's predicted points, goals and assists in a given fixture
def predict_points(i, data_lists):
    # Different actions (e.g. goals, clean sheets, etc) return different points depending on the player's position.
    # So we set multipliers so that we can process the same data for each player and then multiply the data (e.g. goals)
    # by the points that each player will gain

    # if a player is forward
    if data_lists[3].iloc[i, 3] == 4:
        gm = 4  # goal multiplier
        csm = 0  # clean sheet multiplier
        spm = 0  # save points multiplier
        gam = 0  # goals against multiplier
    # if a player is a midfielder
    elif data_lists[3].iloc[i, 3] == 3:
        gm = 5
        csm = 1
        spm = 0
        gam = 0
    #if a player is a defender
    elif data_lists[3].iloc[i, 3] == 2:
        gm = 5
        csm = 4
        spm = 0
        gam = 0.5
    # if a player is a goalkeeper
    else:
        gm = 0
        csm = 4
        spm = 1
        gam = 0.5

    # This calculates expected saves for each goalkeeper with the following equation:
    # ((opponent avg shots in match + team avg shots faced in match)/2)(save percentage)
    saves = ((data_lists[1][0] + data_lists[0][1]) / 2)*(data_lists[0][0])

    # If a player has averaged more than 60 in the last 3 games or throughout the whole season
    # (incase they have been injured recently) then they are predicted 2 points for minutes
    if data_lists[2][2] >= 60 or data_lists[2][3] >= 60:
        minutes_points = 2
    else:
        minutes_points = 1

    # We calculate the save points you would expect the player to yield based on the number of saves they are predicted
    save_points = saves/3

    # We return the number of goals you expect the player's team to concede in the fixture
    fix_xgc = data_lists[2][5]

    # If they player has not played a fixture in the last 3 games then all data is set to 0 as chances are they are
    # likely injured, never play, been transferred or coming back from injury. In each case we don't want to select them
    if data_lists[2][2] != 0:
        pxgim = (data_lists[2][1]/data_lists[0][2]) * ((data_lists[0][2]+data_lists[0][2])/2)  # player expected goals in match
        pxaim = (data_lists[2][0]/data_lists[0][3]) * ((data_lists[0][4]+data_lists[1][3])/2)  # player expected assists in match
        # we then multiply their predicted stats by the multiplier for each position
        predicted_points = ((pxgim * gm) + (pxaim * 3) + (data_lists[2][4] * csm) + (save_points * spm) + minutes_points
                            - fix_xgc * gam)
        return predicted_points, pxgim, pxaim
    else:
        predicted_points = 0
        pxgim = 0
        pxaim = 0
        return predicted_points, pxgim, pxaim
