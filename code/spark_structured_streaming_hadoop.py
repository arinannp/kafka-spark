from pyspark.sql import SparkSession
from pyspark.sql import functions as f
from datetime import datetime



BOOTSTRAP_SERVER = "kafka:9092"
TOPIC_NAME = "user_access"

spark = SparkSession \
    .builder \
    .appName("Structured Streaming Apps") \
    .getOrCreate()

spark.sparkContext.setLogLevel('WARN')

df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", BOOTSTRAP_SERVER) \
    .option("subscribe", TOPIC_NAME) \
    .option("startingOffsets", "earliest") \
    .load()

partition_date = datetime.today().strftime("%Y%m%d")

def write_hdfs(stream_df, stream_id):
    stream_df.show(truncate=False)
    stream_df.write.json(f"hdfs://hadoop:9000/output/user-access_{partition_date}", mode="append")
    stream_df.write.json(f"/opt/bitnami/spark/output/user-access_{partition_date}", mode="append")

df \
    .withColumn("value", f.col("value").cast("STRING")) \
    .withColumn("nama", f.get_json_object(f.col("value"), "$.nama")) \
    .withColumn("ipV4", f.get_json_object(f.col("value"), "$.ipV4")) \
    .withColumn("timestamp", f.get_json_object(f.col("value"), "$.timestamp")) \
    .withColumn("tanggal_lahir", f.get_json_object(f.col("value"), "$.tanggal_lahir").cast("date")) \
    .withColumn("alamat", f.regexp_replace(f.get_json_object(f.col("value"), "$.alamat"), "[\n\r]", " ")) \
    .select(f.to_timestamp(f.col("timestamp"), "yyyy-MM-dd HH:mm:ss").alias("timestamp"), "ipV4", "nama", "tanggal_lahir", "alamat") \
    .withWatermark("timestamp", "5 minutes") \
    .writeStream \
    .foreachBatch(write_hdfs) \
    .trigger(processingTime="10 minutes") \
    .start() \
    .awaitTermination()