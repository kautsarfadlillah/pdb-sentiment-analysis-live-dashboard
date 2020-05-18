### How to Run
- Run HDFS and Mongo

- Run tweet_stream.py and stream_producer.py

- Run spark_stream.py

```spark-submit --master local[*] --name "Live Sentiment Analysis" --conf spark.streaming.receiver.writeAheadLog.enable=true spark_stream.py```

### Tech Stacks

- Hadoop HDFS

- Spark

- MongoDB

- Dash
---
### Script
**dashboard.py**        : frontend

**mongo_checker.py**    : mongodb viewer and deleter option

**spark_stream.py**     : spark streaming (calculate sentiments and positive/negative words)

**stream_producer.py**  : read data/tweets.txt file to produce fake stream

**tweet_fetcher.py**    : script to get some tweets and store to data/tweets.txt

**tweet_stream.py**     : script to stream data from Twitter API

---
### Data
**key_norm.csv**        : contains mapping from brief words to its real words

**negations.txt**       : contains negation words

**negatives.tsv**       : contains negative words with its weight

**positives.tsv**       : contains positive words with its weight

**stopwords.txt**       : contains stopwords

**tweets.txt**          : contains tweets to produce fake stream
