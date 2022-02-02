from flask import Flask, render_template, request
import pandas as pd
import os
import requests
from bs4 import BeautifulSoup
from utils import get_top_100


app = Flask(__name__)


@app.route('/')
def index():
    top100 = get_top_100()
    return render_template(
        'basketball_stats.html',
        season_best_year=[top100[0].to_html(classes='data')],
        playoffs_best_year=[top100[1].to_html(classes='data')],
        season_avg_best4=[top100[2].to_html(classes='data')],
        playoffs_avg_best4=[top100[3].to_html(classes='data')],
        season_best_year_playoffs_avg=[top100[4].to_html(classes='data')],
        season_best_4_years_playoffs_avg=[top100[5].to_html(classes='data')],
    )