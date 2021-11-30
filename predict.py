import numpy
import csv
from operator import itemgetter
from pprint import pprint
import requests
import random
from datetime import datetime
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import tensorflow as tf

def get_model():
    return tf.keras.models.load_model('model') if os.path.exists('model/saved_model.pb') else None

def predict(model, previous_stats, current_stats):
    if (not previous_stats):
        exit('Info: no data for previous stats')
    
    predict_data = numpy.empty(shape=[0, 2])
    if (model):
        for current_stat in current_stats:
            previous_stat = [d for d in previous_stats if d['symbol'] == current_stat['symbol']]
            if not previous_stat:
                break

            predict_data = numpy.append(predict_data, [[
                    get_delta_value(previous_stat[0]['price'], current_stat['price']),
                    get_delta_value(previous_stat[0]['volume'], current_stat['volume']),
                ]], axis = 0)
        predictions = model.predict(predict_data)
            
    else:
        predictions = numpy.empty(shape=[0, 1])
        print('Info: no model to load')

    predicted_data = []
    for i, current_stat in enumerate(current_stats):
        previous_stat = [d for d in previous_stats if d['symbol'] == current_stat['symbol']]
        if not previous_stat:
            break

        predicted_data.append({
            'symbol' : current_stat['symbol'], 
            'delta_price' : get_delta_value(previous_stat[0]['price'], current_stat['price']),
            'delta_volume' : get_delta_value(previous_stat[0]['volume'], current_stat['volume']),
            'confidence' : predictions[i][0] if predictions.any() else 0,
            'buy_price' : current_stat['price'],
            'buy_time' : datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    predicted_data = sorted(predicted_data, key = itemgetter('confidence'), reverse = True)

    return {
        'all': predicted_data, 
        'predicted_1': [predicted_data[0] if predictions.any() else random.choice(predicted_data)],
        'predicted_10': predicted_data[:10] if predictions.any() else [random.choice(predicted_data) for i in range(10)],
        'random_1': [random.choice(predicted_data)],
        'random_10': [random.choice(predicted_data) for i in range(10)]
    }

def get_stats():
    stats = []
    
    with open('stats.csv') as csvfile:
        for row in csv.reader(csvfile):
            stats.append({'symbol' : row[0], 'price' : float(row[1]), 'volume' : float(row[2])})
    
    return stats

def set_stats():
    stats = []
    new_stats = requests.get('https://api.binance.com/api/v3/ticker/24hr').json()
    
    with open('stats.csv', mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for item in new_stats:
            if (item['symbol'].endswith('USDT') == True and not float(item['lastPrice']) == 0):
                writer.writerow([item['symbol'], item['lastPrice'], item['quoteVolume']])
                stats.append({'symbol' : item['symbol'], 'price' : float(item['lastPrice']), 'volume' : float(item['quoteVolume'])})

    return stats


def buy(predicted_data):
    for category in predicted_data:
        for coin in predicted_data[category]:
            if (coin['delta_price'] != 0 and coin['delta_volume'] != 0):
                with open('trades_active_' + category + '.csv', mode='a', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow([coin['symbol'], coin['delta_price'], coin['delta_volume'], coin['confidence'], coin['buy_price'], coin['buy_time']])

def sell(current_stats):
    categories = ['all', 'predicted_10', 'random_10', 'predicted_1', 'random_1']

    for category in categories:
        if os.path.exists('trades_active_' + category + '.csv'):
            with open('trades_active_' + category + '.csv', 'r+') as active, open('trades_finished_' + category + '.csv', 'a', newline='') as finished:
                writer = csv.writer(finished)
                for row in csv.reader(active):
                    sell_price = [d for d in current_stats if d['symbol'] == row[0]][0]['price']
                    profit = get_delta_value(float(4), sell_price)
                    writer.writerow([row[0], row[1], row[2], row[3], row[4], sell_price, profit, row[5], datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
                active.truncate(0)

def get_delta_value(previous_value, current_value):
    return 100 * (100 * current_value - 100 * previous_value) / previous_value

def main():
    previous_stats = get_stats() if os.path.exists('stats.csv') else None
    current_stats = set_stats()

    sell(current_stats)
    buy(predict(get_model(), previous_stats, current_stats))

main()