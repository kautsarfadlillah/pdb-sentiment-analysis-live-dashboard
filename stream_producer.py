import time
import random
import socket

host = 'localhost'
port = 5678
address = (host, port)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(address)
server_socket.listen(5)

while True:
    print("Listening for client...")
    conn, address = server_socket.accept()
    print("Connected to Client at " + str(address))

    try:
        with open('./data/tweets.txt', 'r') as file:
            tweets = file.read().split(':::')
            number_of_tweets = len(tweets)
            while True:
                tweet = tweets[random.randint(0, number_of_tweets - 1)]
                print(tweet)
                conn.send(tweet.encode('utf-8'))
                time.sleep(1)
    except:
        pass
