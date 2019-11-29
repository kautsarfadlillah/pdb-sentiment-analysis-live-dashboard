import socket
import json
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener

consumer_key = '4LVrLVmrktqYR3yNoIVd4DdqN'
consumer_secret = 'GXX1cZW5RdSnwKnPhz7i41SV71tPBiNfBOi6RTTbaWH6TgxA9r'
access_token = '1193096049214156800-1dnhWNqyVKNoB8KAiQK1VQWB3dfS8G'
access_token_secret = '2d9XWPriBITlRZ79e0jZmQbFnr9jgR7SSj5fIppBozkKk'

class TweetsListener(StreamListener):
    def __init__(self, socket):
        self.client_socket = socket

    def on_data(self, data):
        try:
            msg = json.loads(data)

            if ('retweeted_status' in msg):
                if ('extended_tweet' in msg['retweeted_status']):
                    self.print_tweet(msg['retweeted_status']['extended_tweet']['full_text'])
                    self.client_socket.send((str(msg['retweeted_status']['extended_tweet']['full_text']) + "\n").encode('utf-8'))

            elif ('extended_status' in msg):
                self.print_tweet(msg['extended_status']['full_text'])
                self.client_socket.send((str(msg['extended_status']['full_text']) + "\n").encode('utf-8'))
                
            else:
                self.print_tweet(msg['text'])
                self.client_socket.send((str(msg['text']) + "\n").encode('utf-8'))

        except BaseException as e:
            print("Error on_data: %s" % str(e))

        return True

    def on_error(self, status):
        print(status)
        return True

    def print_tweet(self, tweet):
        print("============================")
        print(tweet)

host = 'localhost'
port = 5678
address = (host, port)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(address)
server_socket.listen(5)

print("Listening for client...")
conn, address = server_socket.accept()
print("Connected to Client at " + str(address))

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

twitter_stream = Stream(auth, TweetsListener(conn), tweet_mode="extended_tweet")
twitter_stream.filter(track=['youtube'])
