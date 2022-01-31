from flask import Flask, render_template, request
import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
from utils import get_top_100


app = Flask(__name__)


@app.route('/')
def index():
    players_data = pd.read_csv("static/data/NBA_season.csv")

    players = []

    for idx, row in players_data.iterrows():
        player_string = f'{row["Name"]} ({row["From"]}-{row["To"]})'
        player_data = [player_string, row['id']]
        players.append(player_data)

    top100 = get_top_100()
    return render_template(
        'basketball_stats.html',
        season_best_year=[top100[0].to_html(classes='data')],
        playoffs_best_year=[top100[1].to_html(classes='data')],
        season_avg_best4=[top100[2].to_html(classes='data')],
        playoffs_avg_best4=[top100[3].to_html(classes='data')]
    )