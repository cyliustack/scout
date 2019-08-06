import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import tensorflow as tf 

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import RandomizedSearchCV

from tensorflow.keras.models import Sequential
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.wrappers.scikit_learn import KerasClassifier

import os

filepath_dict = {'yelp':   'yelp_labelled.txt',
                 'amazon': 'amazon_cells_labelled.txt',
                 'imdb':   'imdb_labelled.txt'}

df_list = []
for source, filepath in filepath_dict.items():
    df = pd.read_csv(filepath, names=['sentence', 'label'], sep='\t')
    df['source'] = source  # Add another column filled with the source name
    df_list.append(df)

df = pd.concat(df_list)
print(df)

for source in df['source'].unique():
    df_source = df[df['source'] == source]
    sentences = df_source['sentence'].values
    y = df_source['label'].values

    sentences_train, sentences_test, y_train, y_test = train_test_split(
        sentences, y, test_size=0.25, random_state=1000)

    vectorizer = CountVectorizer()
    vectorizer.fit(sentences_train)
    X_train = vectorizer.transform(sentences_train)
    X_test  = vectorizer.transform(sentences_test)


input_dim = X_train.shape[1]  # Number of features
print('number of features is :', input_dim)


#tokenizer = Tokenizer(num_words=5000)
tokenizer = Tokenizer(num_words=20000)
tokenizer.fit_on_texts(sentences_train)

X_train = tokenizer.texts_to_sequences(sentences_train)
X_test = tokenizer.texts_to_sequences(sentences_test)

vocab_size = len(tokenizer.word_index) + 1  # Adding 1 because of reserved 0 index
print('vocab_size is :', vocab_size)
print(sentences_train[2])
print(X_train[2])

for word in ['the', 'all','fan']:
    print('{}: {}'.format(word, tokenizer.word_index[word]))

#maxlen = 100
maxlen = 200

X_train = pad_sequences(X_train, padding='post', maxlen=maxlen)
X_test = pad_sequences(X_test, padding='post', maxlen=maxlen)

print(X_train[0, :])

#embedding_dim = 50
embedding_dim = 100

'''
1.input_dim: This is the size of the vocabulary in the text data. For example, if your data is integer encoded to values between 0-10, then the size of the vocabulary would be 11 words.

2.output_dim: This is the size of the vector space in which words will be embedded. It defines the size of the output vectors from this layer for each word. For example, it could be 32 or 100 or even larger. Test different values for your problem.

3.input_length: This is the length of input sequences, as you would define for any input layer of a Keras model. For example, if all of your input documents are comprised of 1000 words, this would be 1000.

4.For example, below we define an Embedding layer with a vocabulary of 200 (e.g. integer encoded words from 0 to 199, inclusive), a vector space of 32 dimensions in which words will be embedded, and input documents that have 50 words each.
Embedding(200, 32, input_length=50)
'''

model = Sequential()
model.add(layers.Embedding(input_dim=vocab_size, 
                           output_dim=embedding_dim, 
                           input_length=maxlen,
                           trainable=True))
model.add(layers.Flatten())
model.add(layers.Dense(1000, activation='relu'))
model.add(layers.Dense(1, activation='sigmoid'))

model.compile(tf.train.AdamOptimizer(learning_rate=0.1),    #optimizer='adam',
              loss='binary_crossentropy',
              metrics=['accuracy'])

model.summary()

def nlp_input(X, Y):
    Y = Y.reshape((-1,1)) # Fix Error Tensorflow estimator ValueError:
                          # logits and labels must have the same shape ((?, 1) vs (?,))
    dataset = tf.data.Dataset.from_tensor_slices((X,Y))
    dataset = dataset.repeat(1000)
    dataset = dataset.batch(10)
    return dataset

distribution = tf.contrib.distribute.MirroredStrategy()
config = tf.estimator.RunConfig(train_distribute = distribution)
est = tf.keras.estimator.model_to_estimator(keras_model = model, config = config)

input_res = lambda : nlp_input(X_train, y_train)
est.train(input_fn=input_res, steps=200000000)
