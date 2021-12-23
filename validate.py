from configparser import ConfigParser
from binance.client import Client
import matplotlib.pyplot as plt
import tensorflow as tf
import functions as f

symbolConfig = ConfigParser()
symbolConfig.read('symbols.ini')

def load(symbol):
    return tf.keras.models.load_model('model-' + symbol)

def validate(symbol, model, x_test, y_test):
    max_price = float(symbolConfig[symbol]['max_price'])
    max_volume = float(symbolConfig[symbol]['max_volume'])

    plt.plot(model.predict(f.normalize_x(x_test, max_price, max_volume)) * max_price, color = 'red', label = symbol + ': prediction')
    plt.plot(y_test, color = 'blue', label= symbol + ': real')
    plt.legend(loc = 'best')
    plt.show()

def main():
    for symbol in symbolConfig.sections():
        x_test, y_test = f.get_data(Client().get_historical_klines(symbol.upper(), Client.KLINE_INTERVAL_1HOUR, '7 days ago UTC'))
        validate(symbol, load(symbol), x_test, y_test)

main()