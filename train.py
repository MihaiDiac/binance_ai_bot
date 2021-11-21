import tensorflow as tf
import numpy

tf.config.set_visible_devices([], 'GPU')

def train():
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(input_shape = (3,), units = 20, activation = tf.nn.relu),
    	tf.keras.layers.Dense(units = 20, activation = tf.nn.relu),
        tf.keras.layers.Dense(units = 1)
    ])

    model.compile(optimizer='adam', loss='mse', metrics=['mae'])

    train_data = numpy.empty(shape=[0, 3]);
    train_targets = numpy.empty(shape=[0, 1]);

    with open('trades_finished.csv') as csvfile:    
        for row in csv.reader(csvfile):
            train_data = numpy.append(train_data, [[float(row[1]), float(row[2]), float(row[3])]], axis = 0)
            train_targets = numpy.append(train_targets, [float(row[5])])

    model.fit(train_data, train_targets, epochs=100, batch_size=1)

    return model

def save(model):
    model.save('crypto_model')

model = train()
save(model)