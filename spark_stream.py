from pyspark import SparkContext
from pyspark.streaming import StreamingContext

# run :
# spark-submit --master local[*] --name "Streaming Last Minute Word Count" --conf spark.streaming.receiver.writeAheadLog.enable=true spark_stream.py

CHECKPOINT_DIR = 'hdfs://localhost:9000/demo-checkpoint'

def createContext():
    ssc = StreamingContext(SparkContext(), 10)

    lines = ssc.socketTextStream("localhost", 5678)
    lines_window = lines.window(60, 10)
    words_count = lines_window \
                        .flatMap(lambda line: line.split(' ')) \
                        .filter(lambda word: len(word) > 0) \
                        .map(lambda word: (word, 1)) \
                        .reduceByKey(lambda a, b: a + b) \
                        .transform(
                            lambda rdd: rdd.sortBy(lambda x: x[1], ascending=False)
                        )

    words_count.pprint()

    ssc.checkpoint(CHECKPOINT_DIR)
    return ssc

ssc = StreamingContext.getOrCreate(CHECKPOINT_DIR, createContext)
ssc.sparkContext.setLogLevel("ERROR")

ssc.start()
ssc.awaitTermination()
