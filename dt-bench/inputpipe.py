import tensorflow as tf
from keras.applications import Xception
from keras.applications import ResNet50
from keras.utils import multi_gpu_model
import keras
import keras.backend as K
import numpy as np


keras_inception_v3 = tf.keras.applications.inception_v3.InceptionV3(weights=None)

keras_inception_v3.compile(optimizer=tf.keras.optimizers.SGD(lr=0.0001, momentum=0.9),
                          loss='categorical_crossentropy',
                          metric='accuracy')

#distribution = tf.contrib.distribute.MirroredStrategy()
#config = tf.estimator.RunConfig(train_distribute=distribution)
#est_inception_v3 = tf.keras.estimator.model_to_estimator(keras_model=keras_inception_v3, config=config)
est_inception_v3 = tf.keras.estimator.model_to_estimator(keras_model=keras_inception_v3 )

train, test = tf.keras.datasets.mnist.load_data()
mnist_x, mnist_y = train

mnist_ds = tf.data.Dataset.from_tensor_slices(mnist_x)

features = mnist_x
labels = mnist_y

def train_input_fn(features, labels, batch_size):
    """An input function for training"""
    # Convert the inputs to a Dataset.
    dataset = tf.data.Dataset.from_tensor_slices((dict(features), labels))

    # Shuffle, repeat, and batch the examples.
    dataset = dataset.shuffle(1000).repeat().batch(batch_size)

    # Return the dataset.
    return dataset

est_inception_v3.train(input_fn=train_input_fn(features, labels, 32), steps=2000)
