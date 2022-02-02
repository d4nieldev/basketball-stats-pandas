import pandas as pd

df_season = pd.read_csv("static/data/players_season_prep.csv")
df_playoffs = pd.read_csv("static/data/players_playoffs_prep.csv")


def get_best_year(df):
    ser = df.groupby(['id'])['score2'].max()
    d = {}
    for key, value in ser.iteritems():
        entry = df[(df['id'] == key) & (df['score2'] == value)].iloc[0]
        d[key] = [entry['Name'], entry['Year'], entry['score2']]

    return pd.DataFrame.from_dict(d, orient="index", columns=['Name', 'Year', 'score2']).sort_values(by="score2", ascending=False)


def get_best_4_years(df):
    rows = {}

    for player in df['id'].unique():
        df_player = df[df['id'] == player].sort_values(by='score2', ascending=False).head(4)
        avg = df_player['score2'].mean()

        rows[player] = [df_player.iloc[0]['Name'], list(df_player['Year'].sort_values()), avg]

    best4 = pd.DataFrame().from_dict(rows, orient='index', columns=['Name', 'Years', 'score2']).sort_values(by='score2', ascending=False)
    best4.index.name = 'id'
    return best4


def concat_avg_to_4years_playoff(row, df):
    if row.name in df.index:
        avg = (df.loc[row.name]['score2'] + row['score2']) / 2
    else:
        avg = row['score2'] / 2
    return avg


def get_avg(df1, df2):
    df1['score2'] = df1.apply(concat_avg_to_4years_playoff, args=(df2,), axis=1)
    return df1[['Name', 'score2']].sort_values(by='score2', ascending=False)


def get_top_100():
    """
    :return: season best year, playoffs best year, season avg best 4, playoffs avg best 4
    """
    df_best_year_season = get_best_year(df_season)
    df_best_4_years_season = get_best_4_years(df_season)
    df_best_4_years_playoffs = get_best_4_years(df_playoffs)

    return (
        # season best year
        df_best_year_season.head(100),
        #  playoffs best year
        get_best_year(df_playoffs).head(100),
        # season avg best 4
        df_best_4_years_season.head(100),
        # playoffs avg best 4
        df_best_4_years_playoffs.head(100),
        # avg season best year and playoffs best 4 years
        get_avg(df_best_year_season, df_best_4_years_playoffs).head(100),
        # avg season best 4 years and playoffs best 4 years
        get_avg(df_best_4_years_season, df_best_4_years_playoffs).head(100),
    )
