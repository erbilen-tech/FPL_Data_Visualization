"""
Authors: Kyle Holmberg and Zoe Olson
Maintainer: Kyle Holmberg
Email: kylemh@protonmail.com

Database System and Data Visualization Project
CIS407 and CIS451 at the University of Oregon

Dynamic JSON to CSV conversion of data on fantasy.premierleague.com
"""

import requests
import sys
import csv
import time
import os
import pandas as pd
from unidecode import unidecode

PLAYER_NAMES = []
TOTAL_PAST_STATS = {}
CURR_SEASON_STATS = {}
PLAYERS = {}


# Use FPL API bootstrap endpoint to get player names and current season stats.
# Also used to define number of players in catalogued in FPL (to avoid unnecessary HTTP requests)
def get_curr_stats():
    r = requests.get('https://fantasy.premierleague.com/drf/bootstrap-static')
    bootstrap_data = r.json()
    global NUM_PLAYERS
    NUM_PLAYERS = len(bootstrap_data['elements'])

    for i in range(NUM_PLAYERS):
        # Get Player Names - unidecode replaces accented letters in player names with ascii characters
        PLAYER_NAMES.append(unidecode(bootstrap_data['elements'][i]['first_name'])
                            + ' '
                            + unidecode(bootstrap_data['elements'][i]['second_name']))

        # Get Player's Current Season Stats
        curr_season_data = {'pid':  bootstrap_data['elements'][i]['id'],
                            'minutes': bootstrap_data['elements'][i]['minutes'],
                            'goals_scored': bootstrap_data['elements'][i]['goals_scored'],
                            'assists': bootstrap_data['elements'][i]['assists'],
                            'clean_sheets': bootstrap_data['elements'][i]['clean_sheets'],
                            'goals_conceded': bootstrap_data['elements'][i]['goals_conceded'],
                            'own_goals': bootstrap_data['elements'][i]['own_goals'],
                            'penalties_saved': bootstrap_data['elements'][i]['penalties_saved'],
                            'penalties_missed': bootstrap_data['elements'][i]['penalties_missed'],
                            'yellow_cards': bootstrap_data['elements'][i]['yellow_cards'],
                            'red_cards': bootstrap_data['elements'][i]['red_cards'],
                            'saves': bootstrap_data['elements'][i]['saves'],
                            'ea_index': bootstrap_data['elements'][i]['ea_index'],
                            'influence': float(bootstrap_data['elements'][i]['influence']),
                            'creativity': float(bootstrap_data['elements'][i]['creativity']),
                            'threat': float(bootstrap_data['elements'][i]['threat']),
                            'ict_index': float(bootstrap_data['elements'][i]['ict_index']),
                            'selected_by_percent': float(bootstrap_data['elements'][i]['selected_by_percent'])}
        # Create CurrentSeasonStats Table
        CURR_SEASON_STATS[PLAYER_NAMES[i]] = curr_season_data

        # Create Player Table
        PLAYERS[PLAYER_NAMES[i]] = {'name': PLAYER_NAMES[i], 'pid':  bootstrap_data['elements'][i]['id']}


# If a player has data for past seasons in the API endpoint, call this function
# psc = past season count
def get_past_data(pid, data, psc):
    previous_pl_seasons = psc

    # Variable declarations for summed past statistic headers
    minutes, goals_scored, assists, clean_sheets, goals_conceded, own_goals = 0, 0, 0, 0, 0, 0
    penalties_saved, penalties_missed, yellow_cards, red_cards, saves, ea_index = 0, 0, 0, 0, 0, 0

    # For all previous PL seasons...
    for s in range(psc):
        minutes += data['history_past'][s]['minutes']
        goals_scored += data['history_past'][s]['goals_scored']
        assists += data['history_past'][s]['assists']
        clean_sheets += data['history_past'][s]['clean_sheets']
        goals_conceded += data['history_past'][s]['goals_conceded']
        own_goals += data['history_past'][s]['own_goals']
        penalties_saved += data['history_past'][s]['penalties_saved']
        penalties_missed += data['history_past'][s]['penalties_missed']
        yellow_cards += data['history_past'][s]['yellow_cards']
        red_cards += data['history_past'][s]['red_cards']
        saves += data['history_past'][s]['saves']
        ea_index += data['history_past'][s]['ea_index']

    # Create JSON of overall past season stats
    past_season_data = {'pid': pid,
                        'minutes': minutes,
                        'goals_scored': goals_scored,
                        'assists': assists,
                        'clean_sheets': clean_sheets,
                        'goals_conceded': goals_conceded,
                        'own_goals': own_goals,
                        'penalties_saved': penalties_saved,
                        'penalties_missed': penalties_missed,
                        'yellow_cards': yellow_cards,
                        'red_cards': red_cards,
                        'saves': saves,
                        'ea_index': ea_index,
                        'previous_pl_seasons': previous_pl_seasons}

    return past_season_data


# Grab a player's current season's statistics from the API static bootstrap JSON
# Cycle through FPL API endpoint (also in JSON) for individual players' past season's stats
# Combine all the data to create a singular dictionary file
def get_past_stats():
    misses = 0
    player_url = 'https://fantasy.premierleague.com/drf/element-summary/{}'

    for pid in range(595, NUM_PLAYERS + 1):
        r = requests.get(player_url.format(pid))
        print('Grabbing Player #' + str(pid))

        # Skip broken URLs
        if r.status_code != 200:
            misses += 1
            print('BROKEN URL @ PLAYER #: ' + str(pid) + '\n')
            # More than one miss in a row - end of requests!
            if misses > 1:
                print('Two broken URls in a row... Something is wrong with your connection or the API.\n')
                sys.exit()
            continue

        # Reset 'missing' counter to continue loop through entire API endpoint.
        misses = 0

        player_past_json = r.json()
        past_season_count = len(player_past_json['history_past'])

        # If player has played in PL before...
        if past_season_count > 0:
            TOTAL_PAST_STATS[PLAYER_NAMES[pid - 1]] = get_past_data(pid, player_past_json, past_season_count)

        # Next player...
        pid += 1


# Get Match Data for Matches Table
# def get_match_data():


# Convert PLAYERS into CSV file with headers
# fn = file name | jd = JSON or dictionary data
def player_dict_to_csv(jd, fn):
    with open(fn, 'w') as csvfile:
        headers = ['name', 'pid']
        try:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            for i in jd:
                writer.writerow(jd[i])
        finally:
            print('PLAYERS written to CSV successfully.')


# Convert CURR_SEASON_STATS into CSV file with headers
# fn = file name | jd = JSON or dictionary data
def curr_dict_to_csv(jd, fn):
    with open(fn, 'w') as csvfile:
        headers = ['pid', 'minutes', 'goals_scored', 'assists', 'clean_sheets', 'goals_conceded', 'own_goals',
                   'penalties_saved', 'penalties_missed', 'yellow_cards', 'red_cards', 'saves', 'ea_index',
                   'influence', 'creativity', 'threat', 'ict_index', 'selected_by_percent']
        try:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            for i in jd:
                writer.writerow(jd[i])
        finally:
            print('CURR_SEASON_STATS written to CSV successfully.')


# Convert TOTAL_PAST_STATS into CSV file with headers
# fn = file name | jd = JSON or dictionary
def past_dict_to_csv(jd, fn):
    with open(fn, 'w') as csvfile:
        headers = ['pid', 'minutes', 'goals_scored', 'assists', 'clean_sheets', 'goals_conceded', 'own_goals',
                   'penalties_saved', 'penalties_missed', 'yellow_cards', 'red_cards', 'saves', 'ea_index',
                   'previous_pl_seasons']
        try:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            for i in jd:
                writer.writerow(jd[i])
        finally:
            print('TOTAL_PAST_STATS written to CSV successfully.')


# Use pandas to sort CSVs and delete unsorted arg CSVs
def sort_csv(csv_filename, sorting_key):
    df = pd.read_csv(csv_filename)
    df = df.sort_values(by=sorting_key)
    os.remove(csv_filename)
    df.to_csv(csv_filename, index=False)


# Collection function for relevant data acquisition functions
def get_data():
    print('...Getting player names and current season stats...\n')
    get_curr_stats()
    print('...Getting players past season stats (if any)...\n')
    get_past_stats()


# Collection function for relevant exporting functions
def export_data():
    print('...Writing CSV Files...\n')
    player_dict_to_csv(PLAYERS, 'Players.csv')
    curr_dict_to_csv(CURR_SEASON_STATS, 'CurrentSeasonStats.csv')
    past_dict_to_csv(TOTAL_PAST_STATS, 'TotalPastStats.csv')
    time.sleep(1)
    print('...Sorting CSV Files...\n')
    sort_csv('Players.csv', 'pid')
    sort_csv('CurrentSeasonStats.csv', 'pid')
    sort_csv('TotalPastStats.csv', 'pid')


# Main
get_data()
export_data()


# print('\n...Printing sample data...\n')
# Test Print - CURR_SEASON_STATS
# print("\nTHE TOP GOAL SCORERS THIS SEASON!\n")
# for player in CURR_SEASON_STATS:
#     if CURR_SEASON_STATS[player]['goals_scored'] >= 10:
#         print(player, ' scored ', CURR_SEASON_STATS[player]['goals_scored'], ' goals.')
#
# # Test Print - TOTAL_PAST_STATS
# print("\nTHE OVERALL TOP GOAL SCORERS STILL PLAYING!\n")
# for player in TOTAL_PAST_STATS:
#     if TOTAL_PAST_STATS[player]['goals_scored'] > 100:
#         print(player, ' scored ', TOTAL_PAST_STATS[player]['goals_scored'], ' goals.')
