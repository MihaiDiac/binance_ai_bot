import tensorflow as tf
import numpy
import csv
from operator import itemgetter
from pprint import pprint
import requests
import random
from datetime import datetime
import os

tf.config.set_visible_devices([], 'GPU')

def load():
    return tf.keras.models.load_model('crypto_model')

def predict(model):
    previous_stats = get_stats() if os.path.exists('stats.csv') else None
    set_stats()
    current_stats = get_stats()
    
    if (not previous_stats):
        exit()
    
    predict_data = numpy.empty(shape=[0, 3])

    for current_stat in current_stats:
        previous_stat = [d for d in previous_stats if d['symbol'] == current_stat['symbol']]
        
        if not previous_stat:
            break

        delta_price = 100 * (current_stat['price'] - previous_stat[0]['price']) / previous_stat[0]['price']
        delta_volume = 100 * (current_stat['volume'] - previous_stat[0]['volume']) / previous_stat[0]['volume']
        predict_data = numpy.append(predict_data, [[delta_price, delta_volume, current_stat['price']]], axis = 0)

    predictions = model.predict(predict_data)

    predicted_data = []
    for i, current_stat in enumerate(current_stats):
        previous_stat = [d for d in previous_stats if d['symbol'] == current_stat['symbol']]
        if not previous_stat:
            break

        delta_price = 100 * (current_stat['price'] - previous_stat[0]['price']) / previous_stat[0]['price']
        delta_volume = 100 * (current_stat['volume'] - previous_stat[0]['volume']) / previous_stat[0]['volume']

        predicted_data.append({
            'symbol' : current_stat['symbol'], 
            'delta_price' : delta_price,
            'delta_volume' : delta_volume,
            'prediction' : predictions[i][0],
            'buy_price' : current_stat['price'],
            'buy_time' : datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    sorted(predicted_data, key = itemgetter('prediction'), reverse = True)
    return predicted_data[:15]
    # random.shuffle(predicted_data)
    # return predicted_data[:15]

def get_stats():
    stats = []
    
    with open('stats.csv') as csvfile:
        for row in csv.reader(csvfile):
            stats.append({'symbol' : row[0], 'price' : float(row[1]), 'volume' : float(row[2])})
    
    return stats

def set_stats():
    stats = requests.get('https://api.binance.com/api/v3/ticker/24hr').json()
    with open('stats.csv', mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for item in stats:
            if (item['symbol'].endswith('USDT') == True and not float(item['lastPrice']) == 0):
                writer.writerow([item['symbol'], item['lastPrice'], item['quoteVolume']])

def buy(item):
    if (item['delta_price'] != 0 and item['delta_volume'] != 0):
        with open('trades_active.csv', mode='a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([item['symbol'], item['delta_price'], item['delta_volume'], item['prediction'], item['buy_price'], item['buy_time']])

def sell():
    with open('trades_active.csv', 'r+') as active, open('trades_finished.csv', 'a', newline='') as finished:
        writer = csv.writer(finished)
        for row in csv.reader(active):
            sell_price = [d for d in get_stats() if d['symbol'] == row[0]][0]['price']
            profit = 100 * (sell_price / float(row[4]) - 1)
            writer.writerow([row[0], row[1], row[2], row[3], row[4], sell_price, profit, row[5], datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        active.truncate(0)

sell()
model = load()
items = predict(model)
for item in items:
    buy(item)