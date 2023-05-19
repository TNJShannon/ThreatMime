import json
import config
from neo4j import GraphDatabase
import time

URI = config.NEO4J_URI
USER = config.NEO4J_USER
PASS = config.NEO4J_PASSWORD

source = "stix-test-data/mandient_apt_1.json"

class Neo4jConnection:
    def __init__(self, URI, USER, PASS):
        self.__uri = URI
        self.__user = USER
        self.__pass = PASS
        self.__driver = None

        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth = (self.__user, self.__pass))
        except Exception as e:
            print("Failed to create the driver:", e)
    
    def close(self):
        if self.__driver is not None:
            self.__driver.close()
    
    def query(self, query, parameters=None, db=None):
        assert self.__driver is not None, "Driver is not initialized!"
        session = None
        response = None
        try:
            session = self.__driver.session(database=db) if db is not None else self.__driver.session()
            response = list(session.run(query, parameters))
        except Exception as e:
            print("Query failed", e)
        
        finally:
            if session is not None:
                session.close()
        return response

connection = Neo4jConnection(URI, USER, PASS)
query = ('MATCH (n) WHERE n.name = "APT1"'
         'RETURN n')
print(connection.query(query))
connection.close()