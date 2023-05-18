import json
import config
from neo4j import GraphDatabase

URI = config.NEO4J_URI
AUTH = (config.NEO4J_USER,config.NEO4J_PASSWORD)

source = "stix-test-data/mandient_apt_1.json"

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
