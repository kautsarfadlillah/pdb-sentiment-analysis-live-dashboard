import datetime
import random
import time
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
database = client['pdb']
table = database['sentiment']
pos_word = database['positive_words']
neg_word = database['negative_words']

WORDS = ['abcd', 'spark', 'streaming', 'test']
while True:
    # sentiment table
    t = datetime.datetime.now()
    table.insert_one(
        {
            'date': t, 
            'tweet': 'pdb pdb pdb', 
            'sentiment': random.choice([1, -1]) * random.random()
        }
    )
    time.sleep(2)
    
    # positive word
    word = WORDS[random.randint(0, len(WORDS) - 1)]
    data = pos_word.find_one({'word': word})
    if data is None:
        pos_word.insert_one(
            {
                'word': word,
                'count': 1
            }
        )
    else:
        pos_word.update_one(
            {
                'word': word, 
            },
            {
                '$set': {
                    'count': data['count'] + 1
                }
            }
        )
    
    # negative word
    data = neg_word.find_one({'word': word})
    if data is None:
        neg_word.insert_one(
            {
                'word': word,
                'count': 1
            }
        )
    else:
        neg_word.update_one(
            {
                'word': word, 
            },
            {
                '$set': {
                    'count': data['count'] + 1
                }
            }
        )
    
    #time.sleep(2)
    


