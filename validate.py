import numpy
import os
from binance.client import Client
from configparser import ConfigParser
import matplotlib.pyplot as plt

botConfig = ConfigParser()
botConfig.read('bot.ini')

os.environ['TF_CPP_MIN_LOG_LEVEL'] = botConfig.get('tensorflow', 'log_level')

import tensorflow as tf

symbolConfig = ConfigParser()
symbolConfig.read('symbols.ini')

def get_validation_data(symbol):
    klines = Client().get_historical_klines(symbol.upper(), Client.KLINE_INTERVAL_1HOUR, '7 days ago UTC')

    x_test = numpy.empty(shape=[0, 4])
    y_test = numpy.empty(shape=[0, 1])

    ath = float(symbolConfig.get(symbol, 'ath'))

    for i, kline in enumerate(klines):
        if (i == 0):
            x_test = numpy.append(x_test, [[float(kline[1]), float(kline[2]), float(kline[3]), float(kline[4])]], axis = 0)
        elif (i == len(klines) - 1):
            y_test = numpy.append(y_test, [[float(klines[i][4])]], axis = 0)
        else:
            x_test = numpy.append(x_test, [[float(kline[1]), float(kline[2]), float(kline[3]), float(kline[4])]], axis = 0)
            y_test = numpy.append(y_test, [[float(klines[i][4])]], axis = 0)

    return 100 * x_test / ath, 100 * y_test / ath

def load(symbol):
    return tf.keras.models.load_model('model-' + symbol)

def validate(symbol, model, x_test, y_test):
    plt.plot(model.predict(x_test), color = 'red', label = symbol + ': prediction')
    plt.plot(y_test, color = 'blue', label= symbol + ': real')
    plt.legend(loc = 'upper left')
    plt.show()

def main():
    for symbol in symbolConfig.sections():
        x_test, y_test = get_validation_data(symbol)
        validate(symbol, load(symbol), x_test, y_test)

main()