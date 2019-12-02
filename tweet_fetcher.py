import json
from tweepy import OAuthHandler, API, Stream, Cursor

consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = API(auth)

max_tweets = 2000
tweets = []
for tweet in Cursor(api.search, q='gojek', tweet_mode='extended', lang='id').items(max_tweets):
    try:
        tweets.append(tweet.retweeted_status.full_text)
    except:
        tweets.append(tweet.full_text)

with open('./data/tweets.txt', 'w') as file:
    for i in range(len(tweets)):
        tweet = tweets[i]
        if i == len(tweets) - 1:
            print(tweet, file=file)
        else:
            print(tweet + '|||||', file=file)