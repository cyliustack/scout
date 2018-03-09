ps aux | grep tf_cnn | awk {'print $2'} | xargs kill -9
