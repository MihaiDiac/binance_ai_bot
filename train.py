import numpy
import csv
import os
from binance.client import Client
from configparser import ConfigParser

botConfig = ConfigParser()
botConfig.read('bot.ini')

os.environ['TF_CPP_MIN_LOG_LEVEL'] = botConfig['tensorflow']['log_level']

import tensorflow as tf

def train():
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(input_shape = (4,), units = 20, activation = tf.nn.relu),
    	tf.keras.layers.Dense(units = 20, activation = tf.nn.relu),
        tf.keras.layers.Dense(units = 1)
    ])

    model.compile(optimizer='adam', loss='mse', metrics=['mae'])

    klines = Client().get_historical_klines('BTCUSDT', Client.KLINE_INTERVAL_1HOUR, '5 year ago UTC')

    x_train = numpy.empty(shape=[0, 4]);
    y_train = numpy.empty(shape=[0, 1]);
    
    athConfig = ConfigParser()
    athConfig.read('ath.ini')

    for i, kline in enumerate(klines):
        if (i == 0):
            x_train = numpy.append(x_train, [[float(kline[1]), float(kline[2]), float(kline[3]), float(kline[4])]], axis = 0)
        elif (i == len(klines) - 1):
            y_train = numpy.append(y_train, [[float(klines[i][4])]], axis = 0)
        else:
            x_train = numpy.append(x_train, [[float(kline[1]), float(kline[2]), float(kline[3]), float(kline[4])]], axis = 0)
            y_train = numpy.append(y_train, [[float(klines[i][4])]], axis = 0)
        ath = float(klines[i][2]) if float(klines[i][2]) > float(athConfig['symbols']['BTCUSDT']) else float(athConfig['symbols']['BTCUSDT'])

    model.fit(x_train / ath, y_train / ath, epochs = 100, batch_size = 64)

    return model

def save(model):
    model.save('model')

save(train())
