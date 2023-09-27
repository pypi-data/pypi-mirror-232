import requests
import apimoex
from pandas_datareader import data
import quandl
import aiohttp

from config_reader import config

from dotenv import load_dotenv

import yfinance as yf

import sys
import os
from datetime import date

import matplotlib
import matplotlib.pyplot as plt
import statsmodels.api as sm
import pandas as pd
import numpy as np

from prophet import Prophet
from prophet.diagnostics import cross_validation
from prophet.diagnostics import performance_metrics
from prophet.plot import plot_cross_validation_metric

from keras.models import Sequential
from keras.layers import Dense, LSTM, Dropout, GRU
from keras.layers import *
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split
from keras.callbacks import EarlyStopping


class Cinvestor:

    def __init__(self, ticker : str, exchange : str="WIKI", analyze_column : str = None):
        
        ticker = ticker.upper()
        quandl.ApiConfig.api_key = config.quandle_token.get_secret_value()
        quandl.ApiConfig.verify_ssl = False

        try:
            stock = quandl.get(f"{exchange}/{ticker}")
        except Exception as e:
            print("Ошибка получения данных.")
            print(e)
            return
        
        # Выбор колонки для анализа

        default_analyze_column = 'Close'
        
        if analyze_column and analyze_column in stock.columns:
            stock_analyze = stock[[analyze_column]]
        else:
            analyze_column = default_analyze_column
            stock_analyze = stock[[analyze_column]]

        self.analyze_column = analyze_column

        self.stock_analyze = stock_analyze.reset_index(level=0)

        # Работа с датами

        self.date_column_name = "Date"

        if 'Date' in self.stock_analyze.columns:
            date_column_name = 'Date'
        else:
            print("Ошибка в колонке Дата.")
            return

        # Data assigned as class attribute

        self.stock = stock.copy()
        self.stock = self.stock.reset_index(level=0)

        # Временной период анализа для анализируемой колонки
        
        self.min_date = min(self.stock_analyze[date_column_name])
        self.max_date = max(self.stock_analyze[date_column_name])

        # Daily Change - определять как разность каких колонок?
#         stock["Daily Change"] = stock["Adj. Close"] - stock["Adj. Open"]

        # Границы цены

        self.max_price = np.max(self.stock_analyze[analyze_column])
        self.min_price = np.min(self.stock_analyze[analyze_column])

        # Границы цен по датам для анализируемой колонки

        self.min_price_date = self.stock_analyze[self.stock_analyze[analyze_column] == self.min_price][date_column_name]
        self.min_price_date = self.min_price_date[self.min_price_date.index[0]]
        self.max_price_date = self.stock_analyze[self.stock_analyze[analyze_column] == self.max_price][date_column_name]
        self.max_price_date = self.max_price_date[self.max_price_date.index[0]]

        # Стартовая цена для анализируемой колонки

        self.starting_price = float(self.stock_analyze.loc[0, analyze_column]) # Тут скорее всего надо использовать Adj Open или Open

        # Последняя цена для анализируемой колонки
        self.most_recent_price = float(self.stock_analyze.loc[self.stock_analyze.index[-1], analyze_column])


        # Number of years of data to train on
        self.training_years = 3

        # Prophet parameters
        # Default prior from library
        self.changepoint_prior_scale = 0.05
        self.weekly_seasonality = False
        self.daily_seasonality = False
        self.monthly_seasonality = True
        self.yearly_seasonality = True
        self.changepoints = None
