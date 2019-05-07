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

distribution = tf.contrib.distribute.MirroredStrategy()
config = tf.estimator.RunConfig(train_distribute=distribution)
est_inception_v3 = tf.keras.estimator.model_to_estimator(keras_model=keras_inception_v3, config=config)

train_input_fn = tf.estimator.inputs.numpy_input_fn(
    x={"input_1": train_data},
    y=train_labels,
    num_epochs=1,
    shuffle=False)
    
est_inception_v3.train(input_fn=train_input_fn, steps=2000)
