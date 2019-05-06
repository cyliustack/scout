import tensorflow as tf
from keras.applications import Xception
from keras.applications import ResNet50
from keras.utils import multi_gpu_model
import keras
import numpy as np
import sys
import argparse


if __name__ == "__main__":

    num_samples = 64*2*10 # bs * gpus * steps
    height = 224
    width = 224
    num_classes = 1000
 
    parser = argparse.ArgumentParser(description='Keras Built-in Multiple-GPU Training')
    parser.add_argument(
        '--model',
        metavar='ModelName',
        type=str,
        required=False,
        help='name of imagenet model.')
    
    args = parser.parse_args()
    if args.model is not None:
        if args.model == 'ResNet':
            model = ResNet50(weights=None, input_shape=(height, width, 3), classes=num_classes)
        elif args.model == 'InceptionV3':
            model = keras.applications.inception_v3.InceptionV3(include_top=True, weights='imagenet', input_tensor=None, input_shape=None, pooling=None, classes=num_classes)
        elif args.model == 'VGG16':
            keras.applications.vgg16.VGG16(include_top=True, weights='imagenet', input_tensor=None, input_shape=None, pooling=None, classes=num_classes) 
        elif args.model == 'InceptionResNetV2':
            model = keras.applications.inception_resnet_v2.InceptionResNetV2(include_top=True, weights='imagenet', input_tensor=None, input_shape=None, pooling=None, classes=num_classes)

        else:
            print('Unrecognized model.')
            sys.exit(-1)
    else:
        keras.applications.xception.Xception(include_top=True, weights='imagenet', input_tensor=None, input_shape=None, pooling=None, classes=num_classes)
   
    # Instantiate the base model (or "template" model).
    # We recommend doing this with under a CPU device scope,
    # so that the model's weights are hosted on CPU memory.
    # Otherwise they may end up hosted on a GPU, which would
    # complicate weight sharing.
    #with tf.device('/cpu:0'):
    #    model = ResNet50(weights=None, input_shape=(height, width, 3), classes=num_classes)
    #    #model = Xception(weights=None, input_shape=(height, width, 3), classes=num_classes)
    
    model = ResNet50(weights=None, input_shape=(height, width, 3), classes=num_classes)
    keras.utils.print_summary(model, line_length=None, positions=None, print_fn=None)
    
    # Replicates the model on 8 GPUs.
    # This assumes that your machine has 8 available GPUs.
    parallel_model = multi_gpu_model(model, gpus=2, cpu_merge=False)
    parallel_model.compile(loss='categorical_crossentropy',
                           optimizer='rmsprop')
    
    keras.utils.plot_model(model, to_file='model.png', show_shapes=False, show_layer_names=True, rankdir='TB' )
    # Generate dummy data.
    x = np.random.random((num_samples, height, width, 3))
    y = np.random.random((num_samples, num_classes))
    
    # This `fit` call will be distributed on 8 GPUs.
    # Since the batch size is 256, each GPU will process 32 samples.
    parallel_model.fit(x, y, epochs=1, batch_size=128)
    
    # Save model via the template model (which shares the same weights):
    #model.save('my_model.h5')
