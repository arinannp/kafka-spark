import os
import json
import time
from faker import Faker
from bson import json_util
from kafka import KafkaProducer
from datetime import datetime



# BOOTSTRAP_SERVER = "localhost:29092"
# TOPIC_NAME = "user_access"

BOOTSTRAP_SERVER = os.getenv('BOOTSTRAP_SERVER')
TOPIC_NAME = os.getenv('TOPIC_NAME')

producer = KafkaProducer(bootstrap_servers=BOOTSTRAP_SERVER)
fake = Faker('id_ID')

while True:
    timestamp_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    my_dict = {"timestamp": timestamp_now, "nama": fake.name(), "ipV4": fake.ipv4_public(), "tanggal_lahir": fake.date("%Y-%m-%d"), "alamat": fake.address()}

    producer.send(TOPIC_NAME, json.dumps(my_dict, default=json_util.default).encode("utf-8"))
    print(my_dict)
    time.sleep(5)