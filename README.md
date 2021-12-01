# binance_ai_bot

## Purpose

This project is intended to gather data and train a tensorflow model able to predict which coin will increase in value in the following defined interval.

This is done by calculating the diference of price and volume in a defined interval for all coins and comparing with the profit obtained by purchasing each coin.

This project does not automate transations (yet).

## Usage

### Installing prerequisites

This project requires python and the following modules: tensorflow, numpy, requests and tabulate. 

### Gathering data

Running predict.py the first time will create the file stats.csv (which holds the symbol of the coin, current price and current volume). Additionally a message will be shown ("Info: no data for previous stats").

Running predict.py the second time will update the file stats.csv and will create the files trades_active_all.csv, trades_active_predicted.csv and trades_active_random.csv (which hold the symbol of the coin, the difference in price from the previous interval, the difference in volume from the previous interval, the confidence of the prediction, the buy price and the buy time).

Running predict.py the third time will update the files stats.csv, trades_active_all.csv, trades_active_predicted.csv and trades_active_random.csv and will create the files trades_finished_all.csv, trades_finished_predicted.csv and trades_finished_random.csv (which hold the symbol of the coin, the difference in price from the previous interval, the difference in volume from the previous interval, the confidence of the prediction, the buy price, the sell price, the profit, the buy time and the sell time).

Running predict.py the fourth time and after will update all previously created files.

### Training the model

Running train.py will create the model. This requires the file trades_finished_all.csv. If the file is not present an error will be shown ("Error: no data for model training!").

Running predict.py before a model is trained will cause the script random values instead of predicted values for trades_active_predicted.csv. Additionally the confidence predicted will be 0 and a message will be shown ("Info: no model to load").

### Automating the bot

To get the most consitent data, it is recommended to set up a scheduled task for running predict.py every defined interval (e.g. 15 minutes, 1 hour, 4 hours etc.).

To train the model continuously it is recommended to set up a daily scheduled task for running train.py

## Disclaimer

This project is provided "as is" without any warranty of any kind.

By downloading this project you understand and agree that you are solely responsable for any financial loss caused by using this project.
