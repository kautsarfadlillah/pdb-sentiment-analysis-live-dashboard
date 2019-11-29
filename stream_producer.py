import time
import random
import socket

host = 'localhost'
port = 5678
address = (host, port)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(address)
server_socket.listen(5)

print("Listening for client...")
conn, address = server_socket.accept()
print("Connected to Client at " + str(address))

with open('./data/tweets.txt', 'r') as file:
    tweets = file.read().split(':::')
    number_of_tweets = len(tweets)
    while True:
        tweet = tweets[random.randint(0, number_of_tweets)]
        server_socket.send(tweet.encode('utf-8'))
        time.sleep(1)
