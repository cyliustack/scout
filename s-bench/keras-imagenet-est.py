import tensorflow as tf
from keras.applications import Xception
from keras.applications import ResNet50
from keras.utils import multi_gpu_model
import keras
import keras.backend as K
import numpy as np

def _tf_example_parser(record):
    feature = {"image/encoded": tf.FixedLenFeature([], tf.string),
               "image/class_id": tf.FixedLenFeature([], tf.int64)}
    features = tf.parse_single_example(record, features=feature)
    image = tf.decode_raw(features["image/encoded"], out_type=tf.uint8)   # 写入tfrecords的时候是misc/cv2读取的ndarray
    image = tf.cast(image, dtype=tf.float32)
    image = tf.reshape(image, shape=(224, 224, 3))    # 如果输入图片不做resize，那么不同大小的图片是无法输入到同一个batch中的
    label = tf.cast(features["image/class_id"], dtype=tf.int64)
    return image, label

def input_fn(data_path, batch_size=64, is_training=True):
    """
    Parse image and data in tfrecords file for training
    Args:
        data_path:  a list or single tf records path
        batch_size: size of images returned
        is_training: is training stage or not
    Returns:
        image and labels batches of randomly shuffling tensors
    """
    with K.name_scope("input_pipeline"):
        if not isinstance(data_path, (tuple, list)):
            data_path = [data_path]
        dataset = tf.data.TFRecordDataset(data_path)
        dataset = dataset.map(_tf_example_parser)
        dataset = dataset.repeat(25)              # num of epochs
        dataset = dataset.batch(64)               # batch size
        if is_training:
            dataset = dataset.shuffle(1000)     # 对输入进行shuffle，buffer_size越大，内存占用越大，shuffle的时间也越长，因此可以在写tfrecords的时候就实现用乱序写入，这样的话这里就不需要用shuffle
        iterator = dataset.make_one_shot_iterator()
        images, labels = iterator.get_next()
        # convert to onehot label
        labels = tf.one_hot(labels, 2)  # 二分类
        # preprocess image: scale pixel values from 0-255 to 0-1
        images = tf.image.convert_image_dtype(images, dtype=tf.float32)  # 将图片像素从0-255转换成0-1，tf提供的图像操作大多需要0-1之间的float32类型
        images /= 255.
        images -= 0.5
        images *= 2.
        return dict({"input_1": images}), labels


train_data, train_labels = input_fn('~/imagenet')

num_samples = 64*2*10 # bs * gpus * steps
height = 224
width = 224
num_classes = 1000


# Instantiate the base model (or "template" model).
# We recommend doing this with under a CPU device scope,
# so that the model's weights are hosted on CPU memory.
# Otherwise they may end up hosted on a GPU, which would
# complicate weight sharing.
#with tf.device('/cpu:0'):
#    model = ResNet50(weights=None, input_shape=(height, width, 3), classes=num_classes)
#    #model = Xception(weights=None, input_shape=(height, width, 3), classes=num_classes)


# Instantiate a Keras inception v3 model.
keras_inception_v3 = tf.keras.applications.inception_v3.InceptionV3(weights=None)

# Compile model with the optimizer, loss, and metrics you'd like to train with.
keras_inception_v3.compile(optimizer=tf.keras.optimizers.SGD(lr=0.0001, momentum=0.9),
                          loss='categorical_crossentropy',
                          metric='accuracy')
                          
#keras.utils.print_summary(model, line_length=None, positions=None, print_fn=None)
# Replicates the model on 8 GPUs.
# This assumes that your machine has 8 available GPUs.
#parallel_model = multi_gpu_model(model, gpus=2, cpu_merge=False)
#parallel_model.compile(loss='categorical_crossentropy',
#                       optimizer='rmsprop')



# Create an Estimator from the compiled Keras model. Note the initial model
# state of the keras model is preserved in the created Estimator.
est_inception_v3 = tf.keras.estimator.model_to_estimator(keras_model=keras_inception_v3)

# Treat the derived Estimator as you would with any other Estimator.
# First, recover the input name(s) of Keras model, so we can use them as the
# feature column name(s) of the Estimator input function:
keras_inception_v3.input_names  # print out: ['input_1']

# Once we have the input name(s), we can create the input function, for example,
# for input(s) in the format of numpy ndarray:
train_input_fn = tf.estimator.inputs.numpy_input_fn(
    x={"input_1": train_data},
    y=train_labels,
    num_epochs=1,
    shuffle=False)
    
# To train, we call Estimator's train function:
est_inception_v3.train(input_fn=train_input_fn, steps=2000)
