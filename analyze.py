import csv
from datetime import datetime
from pprint import pprint
import os

def get_summary(summary, branch, trades_file):
    with open(trades_file, mode='r') as csvfile:
        for row in csv.reader(csvfile):
            date = datetime.strptime(row[7], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
            if not date in summary:
                summary[date] = {}
                summary[date][branch] = {
                    'pos_count' : 1 if float(row[6]) > 0 else 0,
                    'neg_count' : 1 if float(row[6]) < 0 else 0,
                    'sum' : float(row[6]),
                }
            else:
                if not branch in summary[date]:
                    summary[date][branch] = {
                        'pos_count' : 1 if float(row[6]) > 0 else 0,
                        'neg_count' : 1 if float(row[6]) < 0 else 0,
                        'sum' : float(row[6]),
                    }
                else:
                    summary[date][branch] = {
                        'pos_count' : summary[date][branch]['pos_count'] + 1 if float(row[6]) > 0 else summary[date][branch]['pos_count'],
                        'neg_count' : summary[date][branch]['neg_count'] + 1 if float(row[6]) <= 0 else summary[date][branch]['neg_count'],
                        'sum' : summary[date][branch]['sum'] + float(row[6])
                    }

    for item in summary:
        if branch in summary[item]:
            summary[item][branch]['avg'] = summary[item][branch]['sum'] / (summary[item][branch]['pos_count'] + summary[item][branch]['neg_count'])
            summary[item][branch]['ratio'] = 100 * (summary[item][branch]['pos_count'] / summary[item][branch]['neg_count'] - 1)

    return summary

summary = {}

if os.path.exists('trades_finished.csv'):
    summary = get_summary(summary, 'predicted', 'trades_finished.csv')

if os.path.exists('trades_finished_all.csv'):
    summary = get_summary(summary, 'all', 'trades_finished_all.csv')

pprint(summary)