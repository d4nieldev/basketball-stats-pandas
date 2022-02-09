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
        tables=top100
    )
