# binance_ai_bot

## Purpose

This project is intended to train a tensorflow model able to predict which coin will increase in value in the following defined interval.

The bot does not automate transations (yet).

## Usage

### Installing prerequisites

This project requires python and the following modules: tensorflow, numpy, matplotlib and python-binance. 

### Training the model

Running train.py will create the model by retrieving historical information from Binance.

Running predict.py before a model is trained will throw an error('Error: no model to load').

### Automating the bot

Set up a scheduled task for running predict.py once per hour.

Set up a scheduled task for running train.py once per day.

## Support

If you like this project and want to support it or you just want to buy me a beer, you can send BTC, ETH, BNB etc. at this address: 0x20c1dd66380529c3ee232e2cc82f0ca0ddf5f7ce

## Disclaimer

This project is provided "as is" without any warranty of any kind.

By downloading this project you understand and agree that you are solely responsable for any financial loss caused by using this project.
