class LeagueStats:
    """
    This class provides constants which will are used for calculating the final score
    """

    p3_league_attack_ratio = 34 / 119  # OL3P%
    p2_league_attack_ratio = 54 / 119  # OL2P%
    ft_league_attack_ratio = 11 / 119  # OLFT%
    p3_league_ratio = 0.37  # L3P%
    p2_league_ratio = 0.52  # L2P%
    ft_league_ratio = 0.78  # LFT%

    stl_p3 = 0.02
    stl_p2 = 0.06

    tov_p3 = 0.015
    tov_p2 = 0.05

    orb_p3 = 0.01
    orb_p2 = 0.03

    avg_blocks = 5
    avg_turnovers = 15
    avg_steals = 7.8
    avg_p3a = 34
    avg_p2a = 54
    avg_fta = 11
    total = avg_blocks + avg_turnovers + avg_p3a + avg_p2a + avg_fta

    block_chance = avg_blocks / total  # BLKC%
    tov_chance = avg_turnovers / total  # TOVC%
    stl_chance = avg_steals / total  # STLC%

    ast_tov_ratio = 0.77825770735

    good_shooter_minimum_3p = 0  # 1.2
    good_shooter_minimum_ratio = 0  # 0.401
    good_shooter_3p_multiplier = 3  # 3.2

    ast_min_val = 0.5

    p3_league_attack_from_assist_ratio = 0.37
    p2_league_attack_from_assist_ratio = 1 - p3_league_attack_from_assist_ratio


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
            turnovers - LeagueStats.ast_tov_ratio * assists) - (
                    3 * p3_on_me * p3_ratio_on_me + 2 * p2_on_me * p2_ratio_on_me + 1 * ft_on_me * ft_ratio_on_me)

    return total
