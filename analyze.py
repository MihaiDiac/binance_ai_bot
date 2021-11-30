import csv
from datetime import datetime
from pprint import pprint
import os
from operator import itemgetter
from tabulate import tabulate

def get_summary(summary, branch, trades_file):
    with open(trades_file, mode='r') as csvfile:
        for row in csv.reader(csvfile):
            date = datetime.strptime(row[7], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
            if not date in summary:
                summary[date] = {}
                summary[date][branch] = {
                    'pos_count' : 1 if float(row[6]) > 0 else 0,
                    'neg_count' : 1 if float(row[6]) <= 0 else 0,
                    'sum' : float(row[6]),
                }
            else:
                if not branch in summary[date]:
                    summary[date][branch] = {
                        'pos_count' : 1 if float(row[6]) > 0 else 0,
                        'neg_count' : 1 if float(row[6]) <= 0 else 0,
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
            summary[item][branch]['ratio'] = 100 * (summary[item][branch]['pos_count'] / summary[item][branch]['neg_count'] - 1) if summary[item][branch]['neg_count'] > 0 else 'max'

    return summary

summary = {}

if os.path.exists('trades_finished_predicted_1.csv'):
    summary = get_summary(summary, 'predicted_1', 'trades_finished_predicted_1.csv')

if os.path.exists('trades_finished_random_1.csv'):
    summary = get_summary(summary, 'random_1', 'trades_finished_random_1.csv')

if os.path.exists('trades_finished_predicted_10.csv'):
    summary = get_summary(summary, 'predicted_10', 'trades_finished_predicted_10.csv')

if os.path.exists('trades_finished_random_10.csv'):
    summary = get_summary(summary, 'random_10', 'trades_finished_random_10.csv')

if os.path.exists('trades_finished_all.csv'):
    summary = get_summary(summary, 'all', 'trades_finished_all.csv')

average = []
ratio = []

for item in summary:
    average.append([
        item, 
        summary[item]['predicted_1']['avg'] / 100 if 'predicted_1' in summary[item] else '-',
        summary[item]['random_1']['avg'] / 100 if 'random_1' in summary[item] else '-',
        summary[item]['predicted_10']['avg'] / 100 if 'predicted_10' in summary[item] else '-',
        summary[item]['random_10']['avg'] / 100 if 'random_10' in summary[item] else '-',
        summary[item]['all']['avg'] / 100 if 'all' in summary[item] else '-'
    ])
    ratio.append([
        item, 
        summary[item]['predicted_1']['ratio'] / 100 if 'predicted_1' in summary[item] else '-',
        summary[item]['random_1']['ratio'] / 100 if 'random_1' in summary[item] else '-',
        summary[item]['predicted_10']['ratio'] / 100 if 'predicted_10' in summary[item] else '-',
        summary[item]['random_10']['ratio'] / 100 if 'random_10' in summary[item] else '-',
        summary[item]['all']['ratio'] / 100 if 'all' in summary[item] else '-'
    ])

if (average and ratio):
    print(
        os.linesep + 
        tabulate(
            sorted(average, key = itemgetter(0)), 
            headers = ['Average', 'Predicted-1', 'Random-1', 'Predicted-10', 'Random-10', 'All'], 
            tablefmt="presto"
        ) + 
        os.linesep
    )
    print(
        os.linesep + 
        tabulate(
            sorted(ratio, key = itemgetter(0)), 
            headers = ['Ratio', 'Predicted-1', 'Random-1', 'Predicted-10', 'Random-10', 'All'], 
            tablefmt="presto"
        ) + 
        os.linesep
    )
else:
    print("Warning: no data to analyze")
