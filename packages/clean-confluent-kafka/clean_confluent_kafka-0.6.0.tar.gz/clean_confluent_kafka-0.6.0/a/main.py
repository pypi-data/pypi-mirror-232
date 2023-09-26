import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
from pprint import pprint

from clean_confluent_kafka import KafkaConnection, utils

conn = KafkaConnection()

# pprint(utils.unflatten_dict(conn.export_configs()))

message = conn.consume()
# print(message)
#
message = conn.consume()

conn.produce(message)