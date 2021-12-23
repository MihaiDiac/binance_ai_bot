from binance.client import Client
from configparser import ConfigParser
import tensorflow as tf
import functions as f

botConfig = ConfigParser()
botConfig.read('bot.ini')

symbolConfig = ConfigParser()
symbolConfig.read('symbols.ini')

def train(symbol):
    model = tf.keras.Sequential([
        tf.keras.layers.LSTM(input_shape = (5, 1), units = 64, return_sequences = True),
        tf.keras.layers.LSTM(units = 32, return_sequences = False),
        tf.keras.layers.Dense(units = 1, activation = 'linear')
    ])

    model.compile(optimizer = tf.keras.optimizers.Nadam(learning_rate = float(botConfig.get('train', 'learning_rate'))), loss = botConfig.get('train', 'loss'))

    x_train, y_train = f.get_data(Client().get_historical_klines(symbol.upper(), Client.KLINE_INTERVAL_1HOUR, '3 years ago UTC', '7 days ago UTC'))

    max_price = float(symbolConfig.get(symbol, 'max_price'))
    max_volume = float(symbolConfig.get(symbol, 'max_volume'))

    if (x_train.max(0)[1] > max_price):
        max_price = x_train.max(0)[1]
        symbolConfig.set(symbol, 'max_price', str(x_train.max(0)[1]))
        with open('symbols.ini', 'w') as configFile:
            symbolConfig.write(configFile)

    if (x_train.max(0)[4] > max_volume):
        max_volume = x_train.max(0)[4]
        symbolConfig.set(symbol, 'max_volume', str(x_train.max(0)[4]))
        with open('symbols.ini', 'w') as configFile:
            symbolConfig.write(configFile)

    x_test, y_test = f.get_data(Client().get_historical_klines(symbol.upper(), Client.KLINE_INTERVAL_1HOUR, '7 days ago UTC'))

    model.fit(
        f.normalize_x(x_train, max_price, max_volume), 
        f.normalize_y(y_train, max_price), 
        epochs = int(botConfig.get('train', 'epochs')), 
        batch_size = int(botConfig.get('train', 'batch_size')),
        validation_data = (f.normalize_x(x_test, max_price, max_volume), f.normalize_y(y_test, max_price)),
    )

    return model

def save(symbol, model):
    model.save('model-' + symbol)

def load(symbol):
    return tf.keras.models.load_model('model-' + symbol)

def main():
    for symbol in symbolConfig.sections():
        save(symbol, train(symbol))

main()