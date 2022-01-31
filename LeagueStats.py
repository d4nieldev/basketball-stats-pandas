class LeagueStats:
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

    stl_turnovers = avg_steals / avg_turnovers  # STOV%

    good_shooter_minimum_3p = 0  # 1.2
    good_shooter_minimum_ratio = 0  # 0.401
    good_shooter_3p_multiplier = 3  # 3.2

    ast_min_val = 0.5

    p3_league_attack_from_assist_ratio = 0.37
    p2_league_attack_from_assist_ratio = 1 - p3_league_attack_from_assist_ratio