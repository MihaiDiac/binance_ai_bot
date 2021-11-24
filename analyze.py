import csv
from datetime import datetime
from pprint import pprint
from decimal import Decimal

summary = {};

row_count = 0

with open('trades_finished.csv') as csvfile:    
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
        row_count = row_count + 1

for item in summary:
    summary[item]['avg'] = summary[item]['sum'] / (summary[item]['pos_count'] + summary[item]['neg_count'])

pprint(summary)