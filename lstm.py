import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Date     Open   High   Low    Close  Volume
# 1/3/2012 325.25 332.83 324.97 663.59 7,380,500
# 1/4/2012 331.27 333.87 329.08 666.45 5,749,400

dataset_train = pd.read_csv('SPY2.csv')
training_set = dataset_train.iloc[:, 1:2].values # Open value

from sklearn.preprocessing import MinMaxScaler
sc = MinMaxScaler(feature_range = (0, 1))
training_set_scaled = sc.fit_transform(training_set)

X_train = []
y_train = []
for i in range(60, 6346):
    X_train.append(training_set_scaled[i-60:i, 0])
    y_train.append(training_set_scaled[i, 0])
X_train, y_train = np.array(X_train), np.array(y_train)
print('\ninput_shape is first: ', X_train.shape[0], X_train.shape[1])

X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
print('\n input_shape is :', (X_train.shape[1], 1))

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM,CuDNNLSTM,InputLayer
from keras.layers import Dropout
from keras.layers import CuDNNLSTM

regressor = Sequential()

# Adding the first LSTM layer and some Dropout regularisation
regressor.add(InputLayer(input_shape=(60, 1), name='Open'))
regressor.add(CuDNNLSTM(units = 50, return_sequences = True))
#regressor.add(CuDNNLSTM(units = 50, return_sequences = True, input_shape = (X_train.shape[1], 1)))
regressor.add(Dropout(0.2))

# Adding a second LSTM layer and some Dropout regularisation
regressor.add(CuDNNLSTM(units = 50, return_sequences = True))
regressor.add(Dropout(0.2))

# Adding a third LSTM layer and some Dropout regularisation
regressor.add(CuDNNLSTM(units = 50, return_sequences = True))
regressor.add(Dropout(0.2))

# Adding a fourth LSTM layer and some Dropout regularisation
regressor.add(CuDNNLSTM(units = 50))
regressor.add(Dropout(0.2))

# Adding the output layer
regressor.add(Dense(units = 1))
regressor.summary()


# Compiling
regressor.compile(optimizer = 'adam', loss = 'mean_squared_error')


regressor.fit(X_train, y_train, epochs = 10, batch_size = 128)

# predict

dataset_test = pd.read_csv('SPY2.csv')
real_stock_price = dataset_test.iloc[:, 1:2].values

dataset_total = pd.concat((dataset_train['Open'], dataset_test['Open']), axis = 0)
inputs = dataset_total[len(dataset_total) - len(dataset_test) - 60:].values
inputs = inputs.reshape(-1,1)
inputs = sc.transform(inputs) # Feature Scaling

X_test = []
for i in range(60, 6346):  
    X_test.append(inputs[i-60:i, 0])
X_test = np.array(X_test)
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))


predicted_stock_price = regressor.predict(X_test)
predicted_stock_price = sc.inverse_transform(predicted_stock_price)  # to get the original scale


# Visualising the results
plt.plot(real_stock_price, color = 'red', label = 'Real Google Stock Price')  
plt.plot(predicted_stock_price, color = 'blue', label = 'Predicted Google Stock Price')  
plt.title('Google Stock Price Prediction')
plt.xlabel('Time')
plt.ylabel('Google Stock Price')
plt.legend()
plt.show()















