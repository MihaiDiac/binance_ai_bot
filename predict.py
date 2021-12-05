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

def get_model():
    if not os.path.exists('model/saved_model.pb'):
        error('Error: no model to load')
    
    return tf.keras.models.load_model('model')

def predict(model, klines):
    athConfig = ConfigParser()
    athConfig.read('ath.ini')

    x_test = numpy.array([[float(klines[0][1]), float(klines[0][2]), float(klines[0][3]), float(klines[0][4])]])
    return [
        float(klines[0][4]), # buy price
        model.predict(x_test / float(athConfig['symbols']['BTCUSDT'])) * float(athConfig['symbols']['BTCUSDT']) # precited price
    ]

def buy(predicted):
    with open('trades_active.csv', mode='a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'BTCUSDT', # symbol
            predicted[0], # buy price
            predicted[1][0][0], # predicted price
            datetime.now().strftime('%Y-%m-%d %H:%M:%S') # buy time
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
                    get_delta_value(row[2], klines[0][4]), # predicted profit
                    get_delta_value(row[1], klines[0][4]), # real profit
                    row[3], # buy time
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S') # sell time
                ])
            active.truncate(0)

def get_klines():
    return Client().get_historical_klines('BTCUSDT', Client.KLINE_INTERVAL_1HOUR, '1 hour ago UTC')

def get_delta_value(previous_value, current_value):
    return 100 * (float(current_value) - float(previous_value)) / float(previous_value)

def main():
    sell(get_klines())
    buy(predict(get_model(), get_klines()))

main()