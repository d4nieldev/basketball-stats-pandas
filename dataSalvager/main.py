"""
Writes all NBA players` data from basketball reference website to players.csv file for further research.
"""

import requests
from bs4 import BeautifulSoup
from string import ascii_lowercase
import concurrent.futures
import pandas as pd
from itertools import islice
import time
import sys
import re


def get_players_names():
    """
    :return: dictionary with general information about every single NBA player (all times)
    """
    players = {}

    for letter in ascii_lowercase:
        # get the html page of the current letter and store it in a BeautifulSoup object
        url = f"https://www.basketball-reference.com/players/{letter}/"
        content = requests.get(url).content
        soup = BeautifulSoup(content, "html.parser")

        # get each player row from the players table
        players_rows = soup.find("table", {'id': 'players'}).find("tbody").findAll('tr', attrs={'class': None})

        # get relevant general information for each NBA player and store in players dict
        for row in players_rows:
            key = row.find("th")['data-append-csv']
            player_data = [
                row.find("th").find("a").get_text(),
                row.find("td", attrs={"data-stat": "year_min"}).get_text(),
                row.find("td", attrs={"data-stat": "year_max"}).get_text(),
                row.find("td", attrs={"data-stat": "height"}).get_text(),
                row.find("td", attrs={"data-stat": "weight"}).get_text()
            ]
            players[key] = player_data

    return players


def get_player_stats(key):
    """
    :param key: player key
    :return: the key called with and dict with all the years the player played and the stats
    for this year season and playoff
    """
    # get the html page of the current player and store it in a BeautifulSoup object
    url = f"https://www.basketball-reference.com/players/{key[0]}/{key}.html"
    content = requests.get(url).content
    soup = BeautifulSoup(content, "html.parser")

    # get each years` row from the player stats table
    years_rows_season = soup.find("table", attrs={'id': 'per_game'}).find("tbody").findAll("tr", attrs={"class": 'full_table'})
    # some players don't play at playoffs
    try:
        years_rows_playoffs = soup.find("table", attrs={'id': 'playoffs_per_game'}).find("tbody").findAll("tr", attrs={"class": 'full_table'})
    except AttributeError:
        # construct empty iterable
        years_rows_playoffs = []

    years_data_season = {}
    years_data_playoffs = {}

    for i in range(2):
        years_rows = [years_rows_season, years_rows_playoffs][i]
        for row in years_rows:
            # get the year referring this row
            _, year = row["id"].split(".")

            # get all stats columns for this year
            stats_cols = row.findAll("td")
            year_stats = []

            all_td_stats = ["age", "team_id", "lg_id", "pos", "g", "gs", "mp_per_g", "fg_per_g", "fga_per_g", "fg_pct",
                            "fg3_per_g", "fg3a_per_g", "fg3_pct", "fg2_per_g", "fg2a_per_g", "fg2_pct", "efg_pct",
                            "ft_per_g", "fta_per_g", "ft_pct", "orb_per_g", "drb_per_g", "trb_per_g", "ast_per_g", "stl_per_g",
                            "blk_per_g", "tov_per_g", "pf_per_g", "pts_per_g"]
            for stat in all_td_stats:
                try:
                    year_stats.append(row.find('td', attrs={'data-stat': stat}).get_text())
                except AttributeError:
                    year_stats.append(None)

            # add all year stats to all players` years stats
            if i == 0:
                years_data_season[year] = year_stats
            else:
                years_data_playoffs[year] = year_stats

    return key, years_data_season, years_data_playoffs


def seconds_to_str(time_in_seconds):
    """
    121 => "2:01 minute(s)"
    :param time_in_seconds: amount of seconds
    :return: formatted string as minutes or seconds
    """
    time_in_seconds = round(time_in_seconds)
    if time_in_seconds < 60:
        time_string = f"{time_in_seconds} second(s)"
    else:
        secs = f"{time_in_seconds % 60}" if time_in_seconds % 60 >= 10 else f"0{time_in_seconds % 60}"
        time_string = f"{time_in_seconds // 60}:{secs} minute(s)"

    while len(time_string) < 16:
        time_string = " " + time_string

    return time_string


def get_eta(delta_time, finished, left):
    """
    :param delta_time: how much time passed
    :param finished: amount of players finished
    :param left: amount of players left
    :return: Estimated time to finish what's left
    """
    pace = finished / delta_time
    return seconds_to_str(left / pace)


def salvage_players():
    # get all player names
    sys.stdout.write('getting players names...\n')
    players = get_players_names()
    sys.stdout.write("collecting data:\n")
    max_players = len(players)

    players_data_season = {}
    players_data_playoffs = {}

    check_eta_every = 2
    progressbar_length = 150

    completed_count = 0

    start = time.perf_counter()
    eta = ""
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # TODO: in production, delete islice
        results = [executor.submit(get_player_stats, key) for key in islice(players, max_players)]

        for f in concurrent.futures.as_completed(results):
            key, stats_season, stats_playoffs = f.result()
            # add each year of the player as an entry in players data
            for year in stats_season:
                players_data_season[f"{key} {year}"] = players[key] + stats_season[year]
            for year in stats_playoffs:
                players_data_playoffs[f"{key} {year}"] = players[key] + stats_playoffs[year]

            completed_count += 1

            # calculate how much time passed from the start of collecting the data
            delta_time = time.perf_counter() - start
            # calculate eta about every 2 seconds
            if round(delta_time) % check_eta_every == 0:
                eta = get_eta(delta_time, completed_count, max_players - completed_count)

            # amount of completed players needed to insert '=' in the progress bar
            tick_count = (completed_count * progressbar_length) // max_players

            # show progress bar
            sys.stdout.write('\r')
            sys.stdout.write(
                f"[%-{progressbar_length}s] %d%% %s" % ('=' * tick_count, completed_count / max_players * 100, eta))
            sys.stdout.flush()

    table_map = [
        "Name", "From", "To", "Height", "Weight", "Age", "Tm", "Lg", "Pos", "G", "GS", "MP", "FG", "FGA", "FG%", "3P", "3PA", "3P%", "2P",
        "2PA", "2P%", "eFG%", "FT", "FTA", "FT%", "ORB", "DRB", "TRB", "AST", "STL", "BLK", "TOV", "PF", "PTS"
    ]
    df_season = pd.DataFrame.from_dict(players_data_season, orient="index", columns=table_map)
    df_playoffs = pd.DataFrame.from_dict(players_data_playoffs, orient="index", columns=table_map)

    # export to csv
    df_season.to_csv("players_season.csv")
    df_playoffs.to_csv("players_playoffs.csv")

    print(f"\nfinished in approximately {seconds_to_str(time.perf_counter() - start)}")


def get_team_win_rate(flag):
    url = f"https://www.basketball-reference.com/teams/{flag}/"
    content = requests.get(url).content
    soup = BeautifulSoup(content, "html.parser")
    pat = r'.(\d+) W-L%'

    try:
        win_rate = re.findall(pat, str(soup))[0]
    except IndexError:
        # didn't find win rate - probably referencing another flag
        try:
            new_flag = re.findall(r'window.location.href = "\/teams\/(\w+)\/"', str(soup))[0]
            _, win_rate = get_team_win_rate(new_flag)
        except IndexError:
            # no team page
            win_rate = -1

    return flag, win_rate


def salvage_teams():
    df = pd.read_csv("players_season.csv")
    teams = df['Tm'].unique()

    teams_data = {}

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = [executor.submit(get_team_win_rate, team) for team in teams]

        for f in concurrent.futures.as_completed(results):
            flag, win_rate = f.result()
            teams_data[flag] = int(win_rate)

    df = pd.DataFrame.from_dict(teams_data, orient="index", columns=['WR'])
    df['WR'] = df['WR'] / 10
    df.to_csv('Teams.csv')


salvage_teams()

