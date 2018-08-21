ps aux | grep scout | awk {'print $2'} | xargs kill -9
