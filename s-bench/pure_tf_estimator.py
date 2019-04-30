import tensorflow as tf

from tensorflow.python.keras import metrics as metrics_module


def model_fn(features, labels, mode):  # pylint: disable=unused-argument
    """model_fn which uses a single unit Dense layer."""
    # You can also use the Flatten layer if you want to test a model without any
    # weights.
    layer = tf.layers.Dense(1, use_bias=True)
    logits = layer(features)
    
    if mode == tf.estimator.ModeKeys.PREDICT:
      predictions = {"logits": logits}
      return tf.estimator.EstimatorSpec(mode, predictions=predictions)
    
    def loss_fn():
      y = tf.reshape(logits, []) - tf.constant(1.)
      return y * y
    
    if mode == tf.estimator.ModeKeys.EVAL:
      acc_obj = metrics_module.BinaryAccuracy()
      acc_obj.update_state(labels, labels)
      return tf.estimator.EstimatorSpec(
          mode, loss=loss_fn(), eval_metric_ops={"Accuracy": acc_obj})
    
    assert mode == tf.estimator.ModeKeys.TRAIN
    
    optimizer = tf.train.GradientDescentOptimizer(0.2)
    global_step = tf.train.get_global_step()
    train_op = optimizer.minimize(loss_fn(), global_step=global_step)
    return tf.estimator.EstimatorSpec(mode, loss=loss_fn(), train_op=train_op)

def train_input_fn():
    features = tf.data.Dataset.from_tensors([[1.]]).repeat(10)
    labels = tf.data.Dataset.from_tensors([1.]).repeat(10)
    return tf.data.Dataset.zip((features, labels))

def eval_input_fn():
    features = tf.data.Dataset.from_tensors([[1.]]).repeat(10)
    labels = tf.data.Dataset.from_tensors([1.]).repeat(10)
    return tf.data.Dataset.zip((features, labels))

def predict_input_fn():
    predict_features = tf.data.Dataset.from_tensors([[1.]]).repeat(10)
    return predict_features

def main(_):
    steps = 5
    distribution = tf.contrib.distribute.CollectiveAllReduceStrategy(num_gpus_per_worker=2)
    config = tf.estimator.RunConfig(train_distribute=distribution)
    estimator = tf.estimator.Estimator(model_fn=model_fn, config=config, model_dir='model')
    train_spec = tf.estimator.TrainSpec(input_fn=train_input_fn)
    eval_spec = tf.estimator.EvalSpec(input_fn=eval_input_fn)
    tf.estimator.train_and_evaluate(estimator, train_spec, eval_spec)
    
    
    eval_result = estimator.evaluate(input_fn=eval_input_fn, steps=steps)
    print("Eval result: {}".format(eval_result))
    assert eval_result["Accuracy"] == 1.0
    
    predictions = estimator.predict(input_fn=predict_input_fn)
    # TODO(anjalsridhar): This returns a generator object, figure out how to get
    # meaningful results here.
    print("Prediction results: {}".format(predictions))

if __name__ == "__main__":
  tf.app.run()
