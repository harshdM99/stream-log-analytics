from pyspark.sql import SparkSession
from pyspark.sql.functions import expr,col, from_json, explode, date_format, from_utc_timestamp
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, IntegerType
import configparser

config = configparser.ConfigParser()
config.read('config.py')

# SOURCE - Kafka CONFIG
KAFKA_BROKER = config['KAFKA']['broker']
TOPIC_NAME = config['KAFKA']['topic']

# TARGET - KeySpaces CONFIG
DESTINATION_KEYSPACE = config['KEYSPACES']['Keyspace']
DESTINATION_TABLE = config['KEYSPACES']['Table'] 

app_conf_path = "/home/ec2-user/code/application.conf"

spark = SparkSession.builder \
    .appName("KafkaSparkStreaming") \
    .config("spark.files", app_conf_path) \
    .config("spark.cassandra.connection.config.profile.path", "application.conf") \
    .config("spark.jars", "/home/ec2-user/spark/jars/spark-cassandra-connector-assembly_2.12-3.5.1.jar") \
    .config("spark.sql.extensions", "com.datastax.spark.connector.CassandraSparkExtensions") \
    .master("local[*]") \
    .getOrCreate()

spark.conf.set("spark.cassandra.input.consistency.level", "LOCAL_QUORUM")
spark.conf.set("spark.cassandra.output.consistency.level", "LOCAL_QUORUM")
spark.conf.set("spark.cassandra.output.concurrent.writes", "1")  # Limit concurrent writes
spark.conf.set("spark.cassandra.query.retry.count", "0")  # Increase retries to avoid failures
spark.conf.set("spark.cassandra.output.batch.size.rows", "1")  # Disable batching
spark.conf.set("spark.cassandra.output.batch.grouping.key", "none")  # Avoid grouping by partition

df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", TOPIC_NAME) \
    .option("startingOffsets", "latest") \
    .load()

json_schema = StructType([
    StructField("host", StringType(), True),
    StructField("time", StringType(), True),
    StructField("method", StringType(), True),
    StructField("url", StringType(), True),
    StructField("response", StringType(), True),
    StructField("bytes", StringType(), True),
    StructField("referer", StringType(), True),
    StructField("useragent", StringType(), True),
    StructField("latency", IntegerType(), True)
])

kafka_df = df.withColumn("value", expr("CAST(value as string)"))
streaming_df = kafka_df.withColumn("values_json", from_json(col("value"), json_schema))
streaming_df = streaming_df.select("values_json")

flattened_df = (
    streaming_df.withColumn("host", col("values_json.host"))
                .withColumn("time", from_utc_timestamp(col("values_json.time"), "UTC"))
                .withColumn("time_bucket", date_format("time", "yyyy-MM-dd-HH-mm"))
                .withColumn("method", col("values_json.method"))
                .withColumn("url", col("values_json.url"))
                .withColumn("response", col("values_json.response"))
                .withColumn("bytes", col("values_json.bytes").cast("int"))
                .withColumn("referer", col("values_json.referer"))
                .withColumn("useragent", col("values_json.useragent"))
                .withColumn("latency", col("values_json.latency"))
                .drop("values_json")
)

flattened_df \
    .writeStream \
    .trigger(processingTime='10 seconds') \
    .format("org.apache.spark.sql.cassandra") \
    .outputMode("append") \
    .option("checkpointLocation", "kafka-check-point-dir") \
    .options(table=DESTINATION_TABLE, keyspace=DESTINATION_KEYSPACE) \
    .start() \
    .awaitTermination()
