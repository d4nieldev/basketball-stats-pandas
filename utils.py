import pandas as pd

df_season = pd.read_csv("static/data/NBA_season.csv")
df_playoffs = pd.read_csv("static/data/NBA_playoffs.csv")


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


def get_top_100():
    """
    :return: season best year, playoffs best year, season avg best 4, playoffs avg best 4
    """
    return (
        # season best year
        get_best_year(df_season).head(100),
        #  playoffs best year
        get_best_year(df_playoffs).head(100),
        # season avg best 4
        get_best_4_years(df_season).head(100),
        # playoffs avg best 4
        get_best_4_years(df_playoffs).head(100)
    )
