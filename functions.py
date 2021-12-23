import numpy

def get_data(klines):
    x_data = numpy.empty(shape=[0, 5])
    y_data = numpy.empty(shape=[0, 1])

    for i, kline in enumerate(klines):
        if (i == 0):
            x_data = numpy.append(x_data, [[float(kline[1]), float(kline[2]), float(kline[3]), float(kline[4]), float(kline[5])]], axis = 0)
        elif (i == len(klines) - 1):
            y_data = numpy.append(y_data, [[float(klines[i][4])]], axis = 0)
        else:
            x_data = numpy.append(x_data, [[float(kline[1]), float(kline[2]), float(kline[3]), float(kline[4]), float(kline[5])]], axis = 0)
            y_data = numpy.append(y_data, [[float(klines[i][4])]], axis = 0)

    return x_data, y_data

def normalize_x(x, max_price, max_volume):
    normalized_x = numpy.empty(shape=[0, 5])
    
    for item in x:
        normalized_x = numpy.append(normalized_x, [[item[0] / max_price, item[1] / max_price, item[2] / max_price, item[3] / max_price, item[4] / max_volume]], axis = 0)

    return normalized_x

def normalize_y(y, max_price):
    return y / max_price