from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pymongo import MongoClient
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import datetime
import regex as re
import string

##########################################################
# run command :
# spark-submit --master local[*] --name "Live Sentiment Analysis" --conf spark.streaming.receiver.writeAheadLog.enable=true spark_stream.py

##################### Constants ##########################
CHECKPOINT_DIR = 'hdfs://localhost:9000/checkpoint'
DATABASE_NAME = 'pdb'
DATABASE_HOST = 'localhost'
DATABASE_PORT = 27017
SENTIMENT_TABLE = 'sentiment'
POSITIVE_WORDS_TABLE = 'positive_words'
NEGATIVE_WORDS_TABLE = 'negative_words'

# max value in positives.tsv and negatives.tsv
SENTIMENT_MAX_MAGNITUDE = 5 

STEMMER = StemmerFactory().create_stemmer()

NEGATION_WORDS = set()
STOPWORDS = set()
POSITIVE_WORDS = {}
NEGATIVE_WORDS = {}
KEY_NORM = {}

with open('./data/negations.txt', 'r') as file:
    words = file.read().split('\n')
    for word in words:
        NEGATION_WORDS.add(word)

with open('./data/stopwords.txt', 'r') as file:
    words = file.read().split('\n')
    for word in words:
        STOPWORDS.add(word)

with open('./data/positives.tsv', 'r') as file:
    lines = file.read().split('\n')
    for line in lines:
        line_split = line.split('\t')
        word = line_split[0]
        weight = int(line_split[1])
        POSITIVE_WORDS[word] = weight

with open('./data/negatives.tsv', 'r') as file:
    lines = file.read().split('\n')
    for line in lines:
        line_split = line.split('\t')
        word = line_split[0]
        weight = int(line_split[1])
        NEGATIVE_WORDS[word] = weight

with open('./data/key_norm.csv', 'r') as file:
    lines = file.read().split('\n')
    for line in lines:
        line_split = line.split(',')
        abbr = line_split[1]
        full_word = line_split[2]
        KEY_NORM[abbr] = full_word

##################### Utility Functions ##########################
def get_word_score(word):
    if word in set(POSITIVE_WORDS.keys()):
        return POSITIVE_WORDS[word]
    if word in set(NEGATIVE_WORDS.keys()):
        return NEGATIVE_WORDS[word]
    return 0

def upsert_wordcount_table(table, word):
    data = table.find_one({'word': word})
    if data is None:
        table.insert_one(
            {
                'word': word,
                'count': 1
            }
        )
    else:
        table.update_one(
            {
                'word': word
            },
            {
                '$set': {
                    'count': data['count'] + 1
                }
            }
        )

def calculate_sentiment_and_save(iter):
    with MongoClient(DATABASE_HOST, DATABASE_PORT) as client:
        database = client[DATABASE_NAME]
        sentiment_table = database[SENTIMENT_TABLE]
        positive_words_table = database[POSITIVE_WORDS_TABLE]
        negative_words_table = database[NEGATIVE_WORDS_TABLE]

        for data in iter:
            date = data[0]
            tweet = data[1]
            clean_tweet = data[2]

            # empty tweet handler (cleaning tweet may cause empty tweet)
            if len(clean_tweet.split()) > 0:
                words = clean_tweet.split()

                sentiment_score = 0
                i = 0
                while i < len(words):
                    negation = ''
                    word = words[i]
                    sign = 1
                    if word in NEGATION_WORDS:
                        negation = word + ' '
                        next_word = words[i + 1] if (i + 1) < len(words) else None
                        if next_word is not None:
                            word = next_word
                            sign = -1
                            i += 1
                    
                    word_score = sign * get_word_score(word)
                    if word_score > 0:
                        upsert_wordcount_table(positive_words_table, negation + word)
                    elif word_score < 0:
                        upsert_wordcount_table(negative_words_table, negation + word)

                    sentiment_score += word_score
                    i += 1

                # normalize sentiment score
                sentiment_score = sentiment_score / (SENTIMENT_MAX_MAGNITUDE * len(words))
            else:
                sentiment_score = 0
            
            # save to sentiment db
            sentiment_table.insert_one(
                {
                    'date': date,
                    'tweet': tweet,
                    'sentiment': sentiment_score
                }
            )
            print((date, tweet, clean_tweet, sentiment_score))

def clean_tweets(data):
    date = data[0]
    tweet = data[1]

    # lowercase
    tweet = str.lower(tweet)
    words = tweet.split()

    # remove url
    words = [word for word in words if len(re.sub(r'^https?:\/\/.*[\r\n]*', '', word)) > 0]
    
    # remove symbol
    words = [word.translate(str.maketrans('', '', string.punctuation)) for word in words if len(word.translate(str.maketrans('', '', string.punctuation))) > 0]

    # change abbreviated word to its original word
    words = [str.lower(KEY_NORM[word]) if word in set(KEY_NORM.keys()) else word for word in words]
    
    # stemming
    words = [STEMMER.stem(word) for word in words]

    # remove stopwords and space
    words = [word for word in words if word not in STOPWORDS]

    clean_tweet = ' '.join(words)  
    return (date, tweet, clean_tweet)

##################### Spark Streaming ##########################
def createContext():
    sc = SparkContext()
    ssc = StreamingContext(sc, 5)

    tweets = ssc.socketTextStream('localhost', 5678)
    tweets_with_date = tweets.map(lambda tweet: (datetime.datetime.now(), tweet))
    cleaned_tweets = tweets_with_date.map(clean_tweets)
    cleaned_tweets.foreachRDD(lambda rdd: rdd.foreachPartition(calculate_sentiment_and_save))

    ssc.checkpoint(CHECKPOINT_DIR)
    return ssc

if __name__ == '__main__':
    ssc = StreamingContext.getOrCreate(CHECKPOINT_DIR, createContext)
    ssc.sparkContext.setLogLevel("ERROR")

    ssc.start()
    ssc.awaitTermination()
