from kafka.admin import KafkaAdminClient, NewTopic
from kafka import KafkaProducer
from kafka import errors
from utils.project_config import project_config

def create_topic(topic_name):
    admin_client = KafkaAdminClient(bootstrap_servers=project_config.MESSAGE_QUEUE_URL)
    topic_list = [NewTopic(topic_name, num_partitions=1, replication_factor=1)]
    try:
        fs = admin_client.create_topics(topic_list)
    except errors.TopicAlreadyExistsError:
        pass

class ProducerWrapper:
    def __init__(self, topic_name):
        self._producer = KafkaProducer(bootstrap_servers=project_config.MESSAGE_QUEUE_URL, max_request_size=1500000)

        self._topic_name = topic_name
        create_topic(topic_name)

    def send(self, message):
        self._producer.send(self._topic_name, message)
        self._producer.flush()