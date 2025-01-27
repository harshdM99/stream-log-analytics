from kafka import KafkaProducer, KafkaConsumer
import json
import random
import time
import faker
from datetime import datetime, timezone
import os
os.environ['TZ'] = 'America/New_York'
fak = faker.Faker()

KAFKA_BROKER = 'localhost:9092'
TOPIC = 'logs'

dictionary = {
    'request': ['GET', 'POST', 'PUT', 'DELETE'], 
    'endpoint': ['/usr', '/usr/admin', '/usr/admin/developer', '/usr/login', '/usr/register'], 
    'statuscode': ['303', '404', '500', '403', '502', '304','200'], 
    'username': ['james', 'adam', 'eve', 'alex', 'smith', 'isabella', 'david', 'angela', 'donald', 'hilary'],
    'ua' : [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0',
    'Mozilla/5.0 (Android 10; Mobile; rv:84.0) Gecko/84.0 Firefox/84.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
    'Mozilla/5.0 (Linux; Android 10; ONEPLUS A6000) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4380.0 Safari/537.36 Edg/89.0.759.0',
    'Mozilla/5.0 (Linux; Android 10; ONEPLUS A6000) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.116 Mobile Safari/537.36 EdgA/45.12.4.5121',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 OPR/73.0.3856.329',
    'Mozilla/5.0 (Linux; Android 10; ONEPLUS A6000) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Mobile Safari/537.36 OPR/61.2.3076.56749',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 12_4_9 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Mobile/15E148 Safari/604.1'],
    'referrer' : ['-',fak.uri()]
}

for _ in range(1,40000):
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')  #Serialize messages as JSON
    )
    
    log_entry = {
        "host": fak.ipv4(),
        "time": datetime.now(timezone.utc).isoformat(),
        "method": random.choice(dictionary["request"]),
        "url": random.choice(dictionary["endpoint"]),
        "response": random.choice(dictionary["statuscode"]),
        "bytes": str(int(random.gauss(5000, 50))),
        "referrer": random.choice(dictionary["referrer"]),
        "useragent": random.choice(dictionary["ua"]),
        "latency": random.randint(1, 5000)
    }
    
    producer.send(TOPIC, log_entry)
    print(f"Produced: {log_entry}")
    
    time.sleep(0.5)
    
    producer.flush()