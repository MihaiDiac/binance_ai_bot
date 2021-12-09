import numpy
import csv
from operator import itemgetter
from pprint import pprint
from datetime import datetime
import os
from binance.client import Client
from configparser import ConfigParser

botConfig = ConfigParser()
botConfig.read('bot.ini')

os.environ['TF_CPP_MIN_LOG_LEVEL'] = botConfig['tensorflow']['log_level']

import tensorflow as tf

symbolConfig = ConfigParser()
symbolConfig.read('symbols.ini')

def get_model(symbol):
    if not os.path.exists('model-' + symbol + '/saved_model.pb'):
        print('No model for ' + symbol)
        return None
    
    return tf.keras.models.load_model('model-' + symbol)

def predict(symbol, model, klines):
    x_test = numpy.array([[
        float(klines[0][1]), # open price
        float(klines[0][2]), # high price
        float(klines[0][3]), # low price
        float(klines[0][4]), # close price
    ]])

    ath = float(symbolConfig[symbol]['ath'])

    return [
        float(klines[0][4]), # buy price
        model.predict(100 * x_test / ath) * ath / 100, # precited price
    ]

def buy(symbol, predicted):
    with open('trades_active.csv', mode='a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            symbol, # symbol
            predicted[0], # buy price
            predicted[1][0][0], # predicted price
            get_delta_value(predicted[0], predicted[1][0][0]), # predicted profit
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'), # buy time
        ])

def sell(klines):
    if os.path.exists('trades_active.csv'):
        with open('trades_active.csv', 'r+') as active, open('trades_finished.csv', 'a', newline='') as finished:
            writer = csv.writer(finished)
            for row in csv.reader(active):
                writer.writerow([
                    row[0], # symbol
                    row[1], # buy price
                    row[2], # predicted price
                    klines[0][4], # sell price
                    row[3], # predicted profit
                    get_delta_value(row[1], klines[0][4]), # real profit
                    row[4], # buy time
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'), # sell time
                ])
            active.truncate(0)

def get_klines(symbol):
    return Client().get_historical_klines(symbol.upper(), Client.KLINE_INTERVAL_1HOUR, '1 hour ago UTC')

def get_delta_value(previous_value, current_value):
    return 100 * (float(current_value) - float(previous_value)) / float(previous_value)

def main():
    for symbol in symbolConfig.sections():
        sell(get_klines(symbol))
        buy(symbol, predict(symbol, get_model(symbol), get_klines(symbol)))

main()