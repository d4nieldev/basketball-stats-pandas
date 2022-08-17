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
from datetime import datetime
from formula import calc_score


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

    # print the time string nicely to correspond with the progressbar
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


def update_progress_bar(completed, total, t0, eta, check_eta_every=2, progressbar_length=150):
    """
    Prints out a progressbar to the screen and updates it according to completed tasks
    :param completed: amount of completed tasks
    :param total: amount of total tasks
    :param t0: start time of loading
    :param eta: time left
    :param check_eta_every: update the eta every x second(s)
    :param progressbar_length: how large the bar is
    :return: eta for next update
    """
    # calculate how much time passed from the start of collecting the data
    delta_time = time.perf_counter() - t0

    # calculate eta about every x second(s)
    if round(delta_time) % check_eta_every == 0:
        eta = get_eta(delta_time, completed, total - completed)

    if completed == total:
        eta = "finished"

    # computes the amount of '=' needed to represent completed out of total in terms of progressbar_length
    tick_count = (completed * progressbar_length) // total

    # show progress bar
    sys.stdout.write('\r')
    sys.stdout.write(f"[%-{progressbar_length}s] %d%% %s" % ('=' * tick_count, completed / total * 100, eta))
    sys.stdout.flush()

    return eta


def get_players_names():
    """
    :return: dictionary with general information about every single NBA player (all times)
    """
    players = {}
    print('\ngetting players names...')
    start = time.perf_counter()
    eta = ""
    completed_count = 0
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

        completed_count += 1
        eta = update_progress_bar(completed_count, 26, start, eta)

    return players


def extract_player_data(years_rows):
    """
    :param years_rows: Beautifulsoup iterable of table rows each row represents a year and stats for this year
    :return: dict containing the stats from each row labeled by the year
    """
    data = {}

    for row in years_rows:
        # get the year referring this row
        _, year = row["id"].split(".")

        # get all stats columns for this year
        stats_cols = row.findAll("td")
        year_stats = []

        all_td_stats = ["age", "team_id", "lg_id", "pos", "g", "gs", "mp_per_g", "fg_per_g", "fga_per_g", "fg_pct",
                        "fg3_per_g", "fg3a_per_g", "fg3_pct", "fg2_per_g", "fg2a_per_g", "fg2_pct", "efg_pct",
                        "ft_per_g", "fta_per_g", "ft_pct", "orb_per_g", "drb_per_g", "trb_per_g", "ast_per_g",
                        "stl_per_g", "blk_per_g", "tov_per_g", "pf_per_g", "pts_per_g"]
        for stat in all_td_stats:
            try:
                year_stats.append(row.find('td', attrs={'data-stat': stat}).get_text())
            except AttributeError:
                year_stats.append(None)

        # add all year stats to all players` years stats
        data[year] = year_stats

    return data


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

    return key, extract_player_data(years_rows_season), extract_player_data(years_rows_playoffs)


def prepare_players(df, team_win, df_teams):
    """
    * Splits Unnamed column to Name and Year columns
    * Deletes all players that didn't play in the NBA
    * Deletes all years below 1978
    * For season - keeps only players with Games >= 40
    * For season - keeps only players with TmWin% >= 48%
    * For playoffs - keeps only players with Games >= 3
    * Converts weight to kg
    * Converts height to cm
    * Converts all numeric columns to numeric
    * Fills up nulls in 2P stats with FG stats
    * Fills up the rest of the nulls with zeros
    * Creating the score2 column and calculates for each row

    :param df: players dataframe
    :param team_win: boolean value represents if there is a need including TmWin% or not
    :return: prepared dataframe
    """
    def lbs_to_kg(weight):
        if weight is not None and weight != "":
            return 0.45359237 * weight

    def feet_to_cm(height):
        if height is not None and height != "":
            feet, inches = height.split("-")
            return 30.48 * float(feet) + 2.54 * float(inches)

    def get_win_rate(data):
        flag = data['Tm']
        year = data['Year']
        win_rate = df_teams[(df_teams['Tm'] == flag) & (df_teams['Year'] == year)].iloc[0]['WR']
        return win_rate

    # get name and year from Unnamed column
    df[['id', 'Year']] = df['Unnamed: 0'].str.split(" ", n=2, expand=True)

    # move id and year to start of table
    cols = df.columns.tolist()
    cols = [cols[-2]] + cols[0:6] + [cols[-1]] + cols[6:-2]
    df = df[cols]

    # delete everyone that is not in the NBA
    df = df[df['Lg'] == 'NBA']

    # keep only years above 1978
    df['Year'] = df['Year'].apply(pd.to_numeric)
    df = df[df['Year'] >= 1978]

    df['G'] = df['G'].apply(pd.to_numeric)

    if team_win:  # season
        df['TmWin%'] = df[["Tm", "Year"]].apply(get_win_rate, axis=1)

        # keep only win rate above 48
        df = df[df['TmWin%'] >= 48]

        # keep only years with 40 or more games
        df = df[df['G'] >= 40]
    else:  # playoffs
        # keep only years with 3 or more games
        df = df[df['G'] >= 3]

    # convert height and weight to cm and kg (respectively)
    df['Height'] = df['Height'].apply(feet_to_cm)
    df['Weight'] = df['Weight'].apply(lbs_to_kg)

    # convert all cols to floats
    cols_to_convert = [
        "From", "To", "Age", "GS", "MP", "FG", "FGA", "FG%", "3P", "3PA", "3P%", "2P",
        "2PA", "2P%", "eFG%", "FT", "FTA", "FT%", "ORB", "DRB", "TRB", "AST", "STL", "BLK", "TOV", "PF", "PTS"
    ]
    df[cols_to_convert] = df[cols_to_convert].apply(pd.to_numeric)

    # fill 2P nulls with FG
    df['2P'].fillna(df['FG'], inplace=True)
    df['2PA'].fillna(df['FGA'], inplace=True)
    df['2P%'].fillna(df['FG%'], inplace=True)

    # fill other nulls with 0
    df.fillna(0, inplace=True)

    # add score according to the formula
    df['score2'] = df.apply(calc_score, axis=1)
    return df


def salvage_players():
    # get all player names
    players = get_players_names()
    print("\ncollecting players data...")
    max_players = len(players)

    players_data_season = {}
    players_data_playoffs = {}

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

            eta = update_progress_bar(completed_count, max_players, start, eta)

    table_map = [
        "Name", "From", "To", "Height", "Weight", "Age", "Tm", "Lg", "Pos", "G", "GS", "MP", "FG", "FGA", "FG%", "3P", "3PA", "3P%", "2P",
        "2PA", "2P%", "eFG%", "FT", "FTA", "FT%", "ORB", "DRB", "TRB", "AST", "STL", "BLK", "TOV", "PF", "PTS"
    ]
    df_season = pd.DataFrame.from_dict(players_data_season, orient="index", columns=table_map)
    df_playoffs = pd.DataFrame.from_dict(players_data_playoffs, orient="index", columns=table_map)

    # prepare export to csv
    df_season.to_csv("players_season.csv")
    df_playoffs.to_csv("players_playoffs.csv")
    df_teams = pd.read_csv('ready/Teams_prep.csv')
    prepare_players(pd.read_csv('players_season.csv'), True, df_teams).to_csv("ready/players_season_prep.csv", index=False)
    prepare_players(pd.read_csv('players_playoffs.csv'), False, df_teams).to_csv("ready/players_playoffs_prep.csv", index=False)


def get_team_win_rates(flag):
    """
    :param flag: a team flag
    :return: flag called with, dictionary containing team win rates by year
    """
    url = f"https://www.basketball-reference.com/teams/{flag}/"
    content = requests.get(url).content
    soup = BeautifulSoup(content, "html.parser")
    win_rates = {}

    if flag == "TOT":  # played for multiple teams
        for year in range(1946, datetime.now().year+1):
            win_rates[year] = 0.48
    else:
        try:
            rows = soup.find("table", attrs={'id': flag}).find("tbody").findAll("tr", attrs={'class': None})
            for row in rows:
                year = re.findall(r'\d+', row.find("th").find("a")['href'])[0]
                win_rates[year] = row.find("td", attrs={"data-stat": "win_loss_pct"}).get_text()
        except AttributeError:
            # need a reference to another team flag
            new_flag = re.findall(r'window.location.href = "\/teams\/(\w+)\/"', str(soup))[0]
            _, win_rates = get_team_win_rates(new_flag)

    return flag, win_rates


def prepare_teams(df):
    """
    * Splits Unnamed column to Team and Year
    :param df: teams dataframe
    :return: prepared dataframe
    """
    print("\npreparing teams...")
    # split index column
    df[['Tm', 'Year']] = df['Unnamed: 0'].str.split(" ", n=2, expand=True)

    # rearrange cols
    cols = df.columns.tolist()
    cols = cols[1:] + [cols[0]]
    df = df[cols]

    return df


def salvage_teams():
    df = pd.read_csv("players_season.csv")
    teams = df['Tm'].unique()

    teams_data = {}

    completed_count = 0

    start = time.perf_counter()
    eta = ""
    print("\ncollecting teams data...")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = [executor.submit(get_team_win_rates, team) for team in teams]

        for f in concurrent.futures.as_completed(results):
            flag, win_rates = f.result()
            for year in win_rates:
                val = 0 if win_rates[year] == '' else float(win_rates[year]) * 100
                teams_data[f"{flag} {year}"] = val

            completed_count += 1

            eta = update_progress_bar(completed_count, len(teams), start, eta)

    df = pd.DataFrame.from_dict(teams_data, orient="index", columns=['WR'])
    df.to_csv('Teams.csv')
    prepare_teams(pd.read_csv('Teams.csv')).to_csv("ready/Teams_prep.csv", index=False)


# execute the script
if __name__ == "__main__":
    program_start = time.perf_counter()

    salvage_teams()
    salvage_players()

    print(f"program finished in {seconds_to_str(time.perf_counter() - program_start)}")

