from pymongo import MongoClient

DATABASE_NAME = 'pdb'
DATABASE_HOST = 'localhost'
DATABASE_PORT = 27017
SENTIMENT_TABLE = 'sentiment'
POSITIVE_WORDS_TABLE = 'positive_words'
NEGATIVE_WORDS_TABLE = 'negative_words'

client = MongoClient(DATABASE_HOST, DATABASE_PORT)
database = client[DATABASE_NAME]
sentiment_table = database[SENTIMENT_TABLE]
positive_words_table = database[POSITIVE_WORDS_TABLE]
negative_words_table = database[NEGATIVE_WORDS_TABLE]

print('========================')
for obj in sentiment_table.find():
	print(obj)

print('========================')
for obj in positive_words_table.find():
	print(obj)

print('========================')
for obj in negative_words_table.find():
	print(obj)

print(sentiment_table.count_documents({}))
print(positive_words_table.count_documents({}))
print(negative_words_table.count_documents({}))

op = input('Are you want to delete current db? (y/N)')
if str.lower(op) == 'y':
	sentiment_table.drop()
	positive_words_table.drop()
	negative_words_table.drop()
