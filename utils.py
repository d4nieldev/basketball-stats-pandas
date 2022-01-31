import pandas as pd
from LeagueStats import LeagueStats


df_season = pd.read_csv("static/data/NBA_season.csv")
df_playoffs = pd.read_csv("static/data/NBA_playoffs.csv")


def calc_score(player_stats):
    p3_in = player_stats['3P']
    p3_ratio = player_stats['3P%']

    p2_in = player_stats['2P']
    p2_ratio = player_stats['2P%']

    ft_in = player_stats['FT']
    ft_ratio = player_stats['FT%']

    p3_on_me = 0
    p3_ratio_on_me = 0

    p2_on_me = 0
    p2_ratio_on_me = 0

    ft_on_me = 0
    ft_ratio_on_me = 0

    assists = player_stats['AST']
    d_rebounds = player_stats['DRB']
    off_rebound = player_stats['ORB']
    steals = player_stats['STL']
    blocks = player_stats['BLK']
    turnovers = player_stats['TOV']

    p3_league_attack_ratio = LeagueStats.p3_league_attack_ratio
    p2_league_attack_ratio = LeagueStats.p2_league_attack_ratio
    ft_league_attack_ratio = LeagueStats.ft_league_attack_ratio

    p3_league_ratio = LeagueStats.p3_league_ratio
    p2_league_ratio = LeagueStats.p2_league_ratio
    ft_league_ratio = LeagueStats.ft_league_ratio

    if assists <= LeagueStats.ast_min_val:
        assists = LeagueStats.ast_min_val

    if p3_ratio >= LeagueStats.good_shooter_minimum_ratio and p3_in >= LeagueStats.good_shooter_minimum_3p:
        p3_multiplier = LeagueStats.good_shooter_3p_multiplier
    else:
        p3_multiplier = 3

    z1 = 3 * p3_league_attack_ratio * ((p3_league_ratio + LeagueStats.stl_p3) ** 2) + 2 * p2_league_attack_ratio * (
            (p2_league_ratio + LeagueStats.stl_p2) ** 2) + 2 * (
                 ft_league_ratio ** 2) * ft_league_attack_ratio - LeagueStats.block_chance * (
                 3 * LeagueStats.p3_league_attack_ratio * (
                 LeagueStats.p3_league_ratio ** 2) + 2 * LeagueStats.p2_league_attack_ratio * (
                         p2_league_ratio ** 2))
    z2 = 3 * p3_league_attack_ratio * ((p3_league_ratio + LeagueStats.tov_p3) ** 2) + 2 * p2_league_attack_ratio * (
            (p2_league_ratio + LeagueStats.tov_p2) ** 2) + 2 * (
                 ft_league_ratio ** 2) * ft_league_attack_ratio - LeagueStats.block_chance * (
                 3 * LeagueStats.p3_league_attack_ratio * (
                 LeagueStats.p3_league_ratio ** 2) + 2 * LeagueStats.p2_league_attack_ratio * (
                         p2_league_ratio ** 2))

    tov_value = (z2 - LeagueStats.stl_chance * z1) / (1 + LeagueStats.tov_chance * LeagueStats.stl_chance)
    stl_value = z1 - LeagueStats.tov_chance * tov_value
    assist_val = 0.66 * (
            3 * LeagueStats.p3_league_ratio * LeagueStats.p3_league_attack_from_assist_ratio + 2 * LeagueStats.p2_league_ratio * LeagueStats.p2_league_attack_from_assist_ratio)
    d_rebound_val = 3 * p3_league_attack_ratio * (p3_league_ratio ** 2) + 2 * p2_league_attack_ratio * (
            p2_league_ratio ** 2) + 2 * ft_league_ratio * (
                            ft_league_attack_ratio ** 2) - LeagueStats.block_chance * (
                            3 * LeagueStats.p3_league_attack_ratio * (
                            LeagueStats.p3_league_ratio ** 2) + 2 * LeagueStats.p2_league_attack_ratio * (
                                    LeagueStats.p2_league_ratio ** 2)) - LeagueStats.tov_chance * tov_value
    off_rebound_val = 3 * p3_league_attack_ratio * (
            (p3_league_ratio + LeagueStats.orb_p3) ** 2) + 2 * p2_league_attack_ratio * (
                              (p2_league_ratio + LeagueStats.orb_p2) ** 2) + 2 * (
                              ft_league_ratio ** 2) * ft_league_attack_ratio - LeagueStats.block_chance * (
                              3 * LeagueStats.p3_league_attack_ratio * (
                              LeagueStats.p3_league_ratio ** 2) + 2 * LeagueStats.p2_league_attack_ratio * (
                                      LeagueStats.p2_league_ratio ** 2)) - LeagueStats.tov_chance * tov_value
    block_val = 0.57 * d_rebound_val

    total = p3_multiplier * p3_in * p3_ratio + 2 * p2_in * p2_ratio + 1 * ft_in * ft_ratio + assist_val * assists + d_rebound_val * d_rebounds + off_rebound_val * off_rebound + stl_value * steals + block_val * blocks - tov_value * (
            (turnovers * LeagueStats.stl_turnovers) / assists) - (
                    3 * p3_on_me * p3_ratio_on_me + 2 * p2_on_me * p2_ratio_on_me + 1 * ft_on_me * ft_ratio_on_me)

    return total


def get_top_100():
    """
    :return: season best year, playoffs best year, season avg best 4, playoffs avg best 4
    """

    rows_season = {}
    rows_playoffs = {}

    for player in df_season['id'].unique():
        df_player_season = df_season[df_season['id'] == player].sort_values(by='score2', ascending=False).head(4)
        df_player_playoffs = df_season[df_season['id'] == player].sort_values(by='score2', ascending=False).head(4)
        avg_season = df_player_season['score2'].mean()
        avg_playoffs = df_player_playoffs['score2'].mean()

        rows_season[player] = [df_player_season.iloc[0]['Name'], list(df_player_season['Year'].sort_values()),
                               avg_season]
        rows_playoffs[player] = [df_player_playoffs.iloc[0]['Name'], list(df_player_playoffs['Year'].sort_values()),
                                 avg_playoffs]

    return (
        # season best year
        df_season[['id', 'Name', 'Year', 'score2']].groupby('id').agg(
            {'Name': 'first', 'Year': 'first', 'score2': 'max'}).sort_values(by='score2', ascending=False).head(100),
        #  playoffs best year
        df_playoffs[['id', 'Name', 'Year', 'score2']].groupby('id').agg(
            {'Name': 'first', 'Year': 'first', 'score2': 'max'}).sort_values(by='score2', ascending=False).head(100),
        # season avg best 4
        pd.DataFrame().from_dict(rows_season, orient='index', columns=['Name', 'Years', 'score2']).sort_values(
            by='score2', ascending=False).head(100),
        # playoffs avg best 4
        pd.DataFrame().from_dict(rows_playoffs, orient='index', columns=['Name', 'Years', 'score2']).sort_values(
            by='score2', ascending=False).head(100)
    )
