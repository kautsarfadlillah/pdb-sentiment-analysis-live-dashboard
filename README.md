### Tech Stack

- Hadoop HDFS

- Spark

- MongoDB

- Dash
---
### Script
**dashboard.py**        : frontend

**mongo_checker.py**    : mongodb viewer and deleter option

**spark_stream.py**     : spark streaming (kalkulasi sentimen dan kata positif/negatif)

**stream_producer.py**  : membaca file data/tweets.txt untuk melakukan stream buatan

**tweet_fetcher.py**    : script untuk mengisi file data/tweets.txt

**tweet_stream.py**     : script untuk stream data dari Twitter API

---
### Data
**key_norm.csv**        : file kumpulan mapping kata singkatan ke kata asli

**negations.txt**       : file kumpulan kata negasi

**negatives.tsv**       : file kumpulan mapping kata negatif dengan besaran sentimen

**positives.tsv**       : file kumpulan mapping kata positif dengan besaran sentimen

**stopwords.txt**       : file kumpulan stopwords

**tweets.txt**          : file kumpulan tweet yang digunakan untuk membuat stream buatan
