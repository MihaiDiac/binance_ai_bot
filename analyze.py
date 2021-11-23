import csv
from datetime import datetime

summary = {};

with open('trades_finished.csv') as csvfile:    
    for row in csv.reader(csvfile):
        date = datetime.strptime(row[7], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
        if date in summary:
        	summary[date] = summary[date] + float(row[6])
        else:
        	summary[date] = float(row[6])

print(summary)