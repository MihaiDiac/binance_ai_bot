import csv
from datetime import datetime
import os

with open('trades_finished.csv', mode='r') as csv_in, open('trades_finished_temp.csv', mode='w', newline='') as csv_out:
    writer = csv.writer(csv_out)

    for row in csv.reader(csv_in):
        symbol = row[0]
        delta_price = float(row[1])
        delta_volume = float(row[2])
        prediction = float(row[3])
        buy_price = float(row[4])
        sell_price = float(row[5])
        profit = float(row[6])
        buy_date = datetime.strptime(row[7], '%Y-%m-%d %H:%M:%S')
        sell_date = datetime.strptime(row[8], '%Y-%m-%d %H:%M:%S')

        if ((profit != 0) and ((sell_date - buy_date).total_seconds() / 60.0 < 20)):
            writer.writerow(row)

os.remove('trades_finished.csv')
os.rename('trades_finished_temp.csv', 'trades_finished.csv')