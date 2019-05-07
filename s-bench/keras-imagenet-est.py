#*- coding: UTF-8 -*-
import tensorflow as tf
from keras.applications import Xception
from keras.applications import ResNet50
from keras.utils import multi_gpu_model
import keras
import keras.backend as K
import numpy as np
import glob

input_name = tf.keras.applications.inception_v3.InceptionV3(weights=None).input_names[0]

def imgs_input_fn(filenames, labels=None, perform_shuffle=False, repeat_count=25, batch_size=64):
    def _parse_function(filename, label):
        image_string = tf.read_file(filename)
        image = tf.image.decode_image(image_string, channels=3)
        image.set_shape([None, None, None])
        image = tf.image.resize_images(image, [224, 224])
        image.set_shape([224, 224, 3])
        image = tf.reverse(image, axis=[2]) # 'RGB'->'BGR'
#        d = dict(zip([input_name], [image])), label
        d = dict(zip(["input_2"], [image])), label
        return d 
    if labels is None:
        labels = [0]*len(filenames)
    labels=np.array(labels)
    if len(labels.shape) == 1:
        labels = np.expand_dims(labels, axis=1)
    filenames = tf.constant(filenames)
    labels = tf.constant(labels)
    labels = tf.cast(labels, tf.float32)
    dataset = tf.data.Dataset.from_tensor_slices((filenames, labels))
    dataset = dataset.map(_parse_function)
    if perform_shuffle:
        # Randomizes input using a window of 256 elements (read into memory)
        dataset = dataset.shuffle(buffer_size=256)
    dataset = dataset.repeat(repeat_count)  # Repeats dataset this # times
    dataset = dataset.batch(batch_size)  # Batch size to use
    iterator = dataset.make_one_shot_iterator()
    batch_features, batch_labels = iterator.get_next()
    return batch_features, batch_labels

filename = glob.glob("/mnt/dataset/imagenet/raw-data/train/n02808440/*.JPEG")
keras_inception_v3 = tf.keras.applications.inception_v3.InceptionV3(weights=None)
keras_inception_v3.compile(optimizer=tf.keras.optimizers.SGD(lr=0.0001, momentum=0.9),
                          loss='categorical_crossentropy',
                          metric='accuracy')
est_inception_v3 = tf.keras.estimator.model_to_estimator(keras_model=keras_inception_v3)
est_inception_v3.train(input_fn=lambda: imgs_input_fn(filename, None, False, 25, 64), steps=2000)
