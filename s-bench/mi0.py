import tensorflow as tf
from tensorflow import keras

if __name__ == '__main__':
    
    inputs = tf.keras.layers.Input(shape=(1,))
    predictions = tf.keras.layers.Dense(1)(inputs)
    model = tf.keras.models.Model(inputs=inputs, outputs=predictions)

    features = tf.data.Dataset.from_tensors([1.]).repeat(10000).batch(10)
    labels = tf.data.Dataset.from_tensors([1.]).repeat(10000).batch(10)
    train_dataset = tf.data.Dataset.zip((features, labels))

    features = tf.data.Dataset.from_tensors([1.]).repeat(1000).batch(10)
    labels = tf.data.Dataset.from_tensors([1.]).repeat(1000).batch(10)
    eval_dataset = tf.data.Dataset.zip((features, labels))

    features = tf.data.Dataset.from_tensors([1.]).repeat(1000).batch(10)
    labels = tf.data.Dataset.from_tensors([1.]).repeat(1000).batch(10)
    predict_dataset = tf.data.Dataset.zip((features, labels))

    distribution = tf.contrib.distribute.MirroredStrategy()
    
    tb = tf.keras.callbacks.TensorBoard(log_dir='./logs', histogram_freq=0, batch_size=10, write_graph=True, write_grads=False, write_images=False, embeddings_freq=0, embeddings_layer_names=None, embeddings_metadata=None, embeddings_data=None, update_freq='epoch')
    model.summary()
    model.compile(loss='mean_squared_error',
                  optimizer=tf.train.GradientDescentOptimizer(learning_rate=0.2),
                  distribute=distribution)

    model.fit(train_dataset, epochs=5, steps_per_epoch=10, callbacks=[tb])
    model.evaluate(eval_dataset, steps=1)
    model.predict(predict_dataset, steps=1)
