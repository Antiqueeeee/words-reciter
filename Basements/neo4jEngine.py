from neo4j import GraphDatabase
import os, sys
current_path = os.path.abspath(os.path.join(__file__, os.pardir))
project_path = os.path.abspath(os.path.join(current_path, os.pardir))
sys.path.append(project_path)

from config import *

class Neo4jHandler:
    def __init__(self):
        self.NEO4J_URI = NEO4J_URI
        self.NEO4J_USER = NEO4J_USER
        self.NEO4J_PASSWORD = NEO4J_PASSWORD

    def close(self, driver):
        driver.close()

    def neo4j_connect(self):
        driver = GraphDatabase.driver(self.NEO4J_URI, auth=(self.NEO4J_USER, self.NEO4J_PASSWORD))
        return driver

    def whether_create_node(self, name, Label, attributes = dict()):
        driver = self.neo4j_connect()
        with driver.session() as session:
            result = session.run(f"MATCH (n:{Label}) WHERE n.name = $name RETURN n", name=name)
            res = result.data()
        
            if len(res) == 0:
                return True
            self.close(driver)

    def findNodeByName(self, name, Label):
        driver = self.neo4j_connect()
        with driver.session() as session:
            result = session.run(f"MATCH (n:{Label}) WHERE n.name = $name RETURN n", name=name)
            res = result.data()
        self.close(driver)
        if len(res) > 0 :
            for i in res:
                i["n"]["节点类型"] = Label
        return res


if __name__ == '__main__':
    neo4j_handler = Neo4jHandler()
    res = neo4j_handler.findNodeByName("apple", "Word")
    print(res)