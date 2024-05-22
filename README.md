# fpl_tool
This is a fantasy premier league tool that suggests transfers, predicts the highest scoring players and recommends the best starting XI for your team each week.

Required Python Libraries include:
* Pandas
* Requests

To use this tool, run 's1_access_fpl_api.py', 's2_add_pp_data.py' and then 's3_suggest_transfers.py' in that order. Within 'suggest_transfers.py' you should enter your unique manager ID - found in the URL of the fpl.com points page when you log in. Depending on your strategy, you can alter the number of gameweeks that points will be predicted for within 'access_fpl_api.py'. I would recommend 5 for a regular transfer but you may consider less if it is for a free-hit or wildcard.

The output of the final step will be your best starting XI based on the players you had last week (excluding free hits), the best players to bring in this week (ranked by points and position) and the best affordable transfers you can make.

From my experience, step 1, running 'access_fpl_api.py', should not be conducted between the hours of 11pm and 6am GMT as it results in incorrect data being fetched from fantasy.premier-league.com.

It is worth considering that there are a number of limitations to the algorithm, most notably that it:
* does not attempt to calculate or factor in bonus points
* does to consider a player or team's form, instead using stats from across the whole season
* only uses the current seasons statistics, meaning that the predicted points will lack accuracy and not reflect a player's true ability in the opening few gameweeks
* does not factor in a plethora of other factors, such as competition for starting places, new managers and other changes in personnel, styles of play of competing teams, and a number of other factors too complex to include

