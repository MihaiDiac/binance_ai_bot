import csv
from datetime import datetime
from pprint import pprint

def get_summary(trades_file):
    summary = {};

    with open(trades_file, mode='r') as csvfile:
        for row in csv.reader(csvfile):
            date = datetime.strptime(row[7], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
            if date in summary:
            	summary[date] = {
                    'pos_count' : summary[date]['pos_count'] + 1 if float(row[6]) > 0 else summary[date]['pos_count'],
                    'neg_count' : summary[date]['neg_count'] + 1 if float(row[6]) <= 0 else summary[date]['neg_count'],
                    'sum' : summary[date]['sum'] + float(row[6]),
                }
            else:
            	summary[date] = {
                    'pos_count' : 1 if float(row[6]) > 0 else 0,
                    'neg_count' : 1 if float(row[6]) < 0 else 0,
                    'sum' : float(row[6]),
                }

    for item in summary:
        summary[item]['avg'] = summary[item]['sum'] / (summary[item]['pos_count'] + summary[item]['neg_count'])
        summary[item]['ratio'] = 100 * (summary[item]['pos_count'] / summary[item]['neg_count'] - 1)

    return summary

if os.path.exists('trades_finished.csv'):
    summary = get_summary('trades_finished.csv')
    pprint(summary)

if os.path.exists('trades_finished_all.csv'):
    summary = get_summary('trades_finished_all.csv')
    pprint(summary)