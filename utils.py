import pandas as pd




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
    d = {}
    for v in ["", "_0.05", "_0.04", "_0.03", "_0.02", "_0.01", "_0.005", "_0.001"]:
        df_season = pd.read_csv(f"static/data/players_season_prep{v}.csv")
        df_playoffs = pd.read_csv(f"static/data/players_playoffs_prep{v}.csv")

        df_best_year_season = get_best_year(df_season).head(100)
        df_best_4_years_season = get_best_4_years(df_season).head(100)
        df_best_4_years_playoffs = get_best_4_years(df_playoffs).head(100)
        df_best_year_playoffs = get_best_year(df_playoffs).head(100)

        d[f"best year season {v}"] = df_best_year_season.to_html(classes='data')
        d[f"best year playoffs {v}"] = df_best_year_playoffs.to_html(classes='data')
        d[f"best 4 years season {v}"] = df_best_4_years_season.to_html(classes='data')
        d[f"best 4 years playoffs {v}"] = df_best_4_years_playoffs.to_html(classes='data')
        d[f"best year season + best 4 years playoffs {v}"] = get_avg(df_best_year_season, df_best_4_years_playoffs
                                                                     ).head(100).to_html(classes='data')
        d[f"best 4 years season + best 4 years playoffs {v}"] = get_avg(df_best_4_years_season, df_best_4_years_playoffs
                                                                        ).head(100).to_html(classes='data')

    return d
