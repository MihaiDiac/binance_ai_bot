import numpy
import csv
import os
from pprint import pprint
from binance.client import Client
from configparser import ConfigParser

botConfig = ConfigParser()
botConfig.read('bot.ini')

os.environ['TF_CPP_MIN_LOG_LEVEL'] = botConfig.get('tensorflow', 'log_level')

import tensorflow as tf

symbolConfig = ConfigParser()
symbolConfig.read('symbols.ini')

def train(symbol):
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(input_shape = (4,), units = 64, activation = tf.nn.relu),
    	tf.keras.layers.Dense(units = 64, activation = tf.nn.relu),
        tf.keras.layers.Dense(units = 1)
    ])

    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate = float(botConfig.get('train', 'learning_rate'))), loss='mse', metrics=['mae'])

    klines = Client().get_historical_klines(symbol.upper(), Client.KLINE_INTERVAL_1HOUR, '3 year ago UTC')

    x_train = numpy.empty(shape=[0, 4])
    y_train = numpy.empty(shape=[0, 1])

    ath = float(symbolConfig.get(symbol, 'ath'))
    
    for i, kline in enumerate(klines):
        if (i == 0):
            x_train = numpy.append(x_train, [[float(kline[1]), float(kline[2]), float(kline[3]), float(kline[4])]], axis = 0)
        elif (i == len(klines) - 1):
            y_train = numpy.append(y_train, [[float(klines[i][4])]], axis = 0)
        else:
            x_train = numpy.append(x_train, [[float(kline[1]), float(kline[2]), float(kline[3]), float(kline[4])]], axis = 0)
            y_train = numpy.append(y_train, [[float(klines[i][4])]], axis = 0)
        ath = float(klines[i][2]) if float(klines[i][2]) > ath else ath

    if (ath > float(symbolConfig.get(symbol, 'ath'))):
        symbolConfig.set(symbol, 'ath', str(ath))
        with open('symbols.ini', 'w') as configFile:
            symbolConfig.write(configFile)

    model.fit(100 * x_train / ath, 100 * y_train / ath, epochs = int(botConfig.get('train', 'epochs')), batch_size = int(botConfig.get('train', 'batch_size')))

    return model

def save(symbol, model):
    model.save('model-' + symbol)

def main():
    for symbol in symbolConfig.sections():
        save(symbol, train(symbol))

main()
