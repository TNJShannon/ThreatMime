import json
import config
import util
from neo4j import GraphDatabase

URI = config.NEO4J_URI
USER = config.NEO4J_USER
PASS = config.NEO4J_PASSWORD


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


def create_SDO_node(SDO_object,db_connection):
    #Check if SDO_node exists
    result = db_connection.query(f'MATCH (n) WHERE n.id = "{object["id"]}" RETURN (n)')
    if len(result):
        print(f'{SDO_object["id"]} already exists in database')
        return
    
    query_command = [f'CREATE ({util.sanitize(SDO_object["type"])}:{util.sanitize(SDO_object["type"])}:SDO)']
    for key,value in SDO_object.items():
        query_command.append(f'SET {util.sanitize(SDO_object["type"])}.{key}="{value}"')
    query_command = "\n".join(query_command)
    db_connection.query(query_command)


def create_SRO_connection(SRO_object,db_connection):
    #Check if SRO_connection already exists
    result = connection.query(f'MATCH ()-[r]->() WHERE r.id = "{SRO_object["id"]}" RETURN r')
    if len(result):
        print("Link already exists")
        return
    query_command = [f'MATCH (x) WHERE x.id = "{SRO_object["source_ref"]}" MATCH (y) WHERE y.id = "{SRO_object["target_ref"]}"']
    SRO_properties = "{"
    for key,value in SRO_object.items():
        SRO_properties += f'{key}:"{value}",'
    SRO_properties = SRO_properties[:-1] + "}"
    query_command.append(f'CREATE (x)-[:{util.sanitize(SRO_object["relationship_type"])} {SRO_properties}]->(y)')
    query_command = "\n".join(query_command)
    db_connection.query(query_command)

def attribute_report_references(SDO_report,db_connection):
    for SDO_id in SDO_report["object_refs"]:
        #check if id is already referenced
        result = db_connection.query(f'MATCH (x) WHERE x.id = "{SDO_report["id"]}" MATCH (y) WHERE y.id = "{SDO_id}" MATCH (x)-[r]->(y) RETURN r')
        if len(result):
            print(f'Report already links to {SDO_id}')
            return
        else:
            db_connection.query(f'MATCH (x) WHERE x.id = "{SDO_report["id"]}" MATCH (y) WHERE y.id = "{SDO_id}" CREATE (x)-[:OBJECT_REFS]->(y)')
        

#Try create connection to database
connection = Neo4jConnection(URI, USER, PASS)

source = json.load(open("stix-test-data\poisonivy.json",'r',encoding="utf-8"))
#convert Stix Bundle into querys
bundle_id = source["id"]

#create node for every object in bundle
for object in source["objects"]:
    match object["type"]:
        case "relationship":
            create_SRO_connection(object,connection)
        case "sighting":
            "Sighting SRO's not currently implemented"
        case _:
            create_SDO_node(object,connection)
    if object["type"] == "report":
        attribute_report_references(object,connection)








#upload stix data



#close database
connection.close()