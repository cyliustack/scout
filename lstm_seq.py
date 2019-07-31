import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense,Flatten,Dropout,LSTM,InputLayer
from tensorflow.keras.layers import Conv2D
from tensorflow.keras.layers import MaxPooling2D
 
# split a univariate sequence into samples
def split_sequence(sequence, n_steps):
	X, y = list(), list()
	for i in range(len(sequence)):
		# find the end of this pattern
		end_ix = i + n_steps
		# check if we are beyond the sequence
		if end_ix > len(sequence)-1:
			break
		# gather input and output parts of the pattern
		seq_x, seq_y = sequence[i:end_ix], sequence[end_ix]
		X.append(seq_x)
		y.append(seq_y)
	return np.array(X), np.array(y)
 
# define input sequence
#raw_seq = [10, 20, 30, 40, 50, 60, 70, 80, 90]
raw_ = [i for i in range(10, 100000, 10)]
# choose a number of time steps
n_steps = 3
# split into samples
X, Y = split_sequence(raw_, n_steps)

#reshape from [samples, timesteps] into [samples, timesteps, features]
n_features = 1
X = X.reshape(X.shape[0], X.shape[1], n_features)

#train_input_fn = tf.estimator.inputs.numpy_input_fn(
#    x={'lstm_input': X},
#    y=Y,
#    num_epochs=10000,
#    shuffle=False)


def lstm_input(X, Y):
    dataset = tf.data.Dataset.from_tensor_slices((X,Y))
    dataset = dataset.repeat(100)
    dataset = dataset.batch(100)
    return dataset

model = Sequential()
model.add(LSTM(50, activation='relu', input_shape=(n_steps, n_features)))
model.add(Dense(1))
model.summary()

model.compile(optimizer=tf.train.GradientDescentOptimizer(learning_rate=0.1),
                              loss='categorical_crossentropy',
                              metric='accuracy')

distribution = tf.contrib.distribute.MirroredStrategy()
config = tf.estimator.RunConfig( train_distribute = distribution)
est = tf.keras.estimator.model_to_estimator( keras_model = model, config = config)

lstm_input_res = lambda : lstm_input(X, Y)
est.train(input_fn=lstm_input_res, steps=200000)
