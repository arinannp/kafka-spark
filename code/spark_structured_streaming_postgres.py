import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as f


project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BOOTSTRAP_SERVER = "kafka:9092"
TOPIC_NAME = "user_access"

spark = SparkSession \
    .builder \
    .config('spark.driver.extraClassPath', os.path.join(project_dir, 'connectors/postgresql-9.4.1207.jar')) \
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


# String connection to postgres-db
conn: str = "jdbc:postgresql://postgres:5432/postgres"
properties: dict = {
    "user": "postgres",
    "password": "postgres",
    "driver": "org.postgresql.Driver"
}

def write_postgres(stream_df, stream_id):
    user_df = stream_df \
            .withColumn("date", f.to_date(f.col("timestamp"), "yyy-MM-dd")) \
            .select("date", "nama", "ipv4", "tanggal_lahir", "alamat")
    user_df.write.mode("append").jdbc(conn, table="public.users", properties=properties)
    user_df.show(truncate=False)


df \
    .withColumn("value", f.col("value").cast("STRING")) \
    .withColumn("nama", f.get_json_object(f.col("value"), "$.nama")) \
    .withColumn("ipv4", f.get_json_object(f.col("value"), "$.ipV4")) \
    .withColumn("timestamp", f.get_json_object(f.col("value"), "$.timestamp")) \
    .withColumn("tanggal_lahir", f.get_json_object(f.col("value"), "$.tanggal_lahir").cast("date")) \
    .withColumn("alamat", f.regexp_replace(f.get_json_object(f.col("value"), "$.alamat"), "[\n\r]", " ")) \
    .select(f.to_timestamp(f.col("timestamp"), "yyyy-MM-dd HH:mm:ss").alias("timestamp"), "ipv4", "nama", "tanggal_lahir", "alamat") \
    .withWatermark("timestamp", "5 minutes") \
    .writeStream \
    .foreachBatch(write_postgres) \
    .start() \
    .awaitTermination()