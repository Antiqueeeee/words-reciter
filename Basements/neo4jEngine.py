from neo4j import GraphDatabase
import os, sys
current_path = os.path.abspath(os.path.join(__file__, os.pardir))
project_path = os.path.abspath(os.path.join(current_path, os.pardir))
sys.path.append(project_path)

from config import *
from Basements.ItemWord import *

class Neo4jHandler:
    def __init__(self):
        self.NEO4J_URI = NEO4J_URI
        self.NEO4J_USER = NEO4J_USER
        self.NEO4J_PASSWORD = NEO4J_PASSWORD

    # Basic function

    def close(self, driver):
        driver.close()

    def neo4j_connect(self):
        driver = GraphDatabase.driver(self.NEO4J_URI, auth=(self.NEO4J_USER, self.NEO4J_PASSWORD))
        return driver

    def findNodeByName(self, name, Label, attributes = dict()):
        driver = self.neo4j_connect()
        with driver.session() as session:
            result = session.run(f"MATCH (n:{Label}) WHERE n.name = $name RETURN n", name=name)
            res = result.data()
        self.close(driver)
        if len(res) > 0 :
            for i in res:
                i["n"]["节点类型"] = Label
        return res


    def createNode(self, name, Label, attributes=dict()):
        driver = self.neo4j_connect()
        with driver.session() as session:
            # Check if the node already exists
            check_query = f"MATCH (n:{Label} {{name: $name}}) RETURN n"
            result = session.run(check_query, name=name)
            
            if not result.single():
                # Node does not exist, create it
                attributes['name'] = name  # Ensure 'name' is included in attributes
                create_query = f"CREATE (n:{Label} {{"
                create_query += ", ".join([f"{key}: ${key}" for key in attributes.keys()])
                create_query += "})"
                session.run(create_query, **attributes)
        
        self.close(driver)


    def createRelationship(self, head_label, head_name, head_attributes, tail_label, tail_name, tail_attributes, rel_type, rel_attributes=dict()):
        driver = self.neo4j_connect()
        with driver.session() as session:
            # Construct the Cypher query
            query = (
                f"MERGE (a:{head_label} {{name: $head_name}}) "
            )
            if head_attributes:
                query += f"ON CREATE SET " + ", ".join([f"a.{key} = $head_{key}" for key in head_attributes.keys()]) + " "
            
            query += (
                f"MERGE (b:{tail_label} {{name: $tail_name}}) "
            )
            if tail_attributes:
                query += f"ON CREATE SET " + ", ".join([f"b.{key} = $tail_{key}" for key in tail_attributes.keys()]) + " "
            
            query += f"MERGE (a)-[r:{rel_type} {{"
            query += ", ".join([f"{key}: ${key}" for key in rel_attributes.keys()])
            query += "}]->(b)"
            
            # Prepare parameters
            parameters = {'head_name': head_name, 'tail_name': tail_name}
            parameters.update({f'head_{key}': value for key, value in head_attributes.items()})
            parameters.update({f'tail_{key}': value for key, value in tail_attributes.items()})
            parameters.update(rel_attributes)
            
            # Execute the query
            session.run(query, **parameters)
        self.close(driver)

    # Service function
    def create_word(self, wordItem:WordItem, wordSource:WordSource, relation_attributes = dict()):
        # 单词不在，创建单词
        result = self.findNodeByName(name = wordItem.name, Label = "Word", attributes = wordItem.__dict__)
        if len(result) == 0:
            print(f"节点不存在：{wordItem.name}, Word")
            self.createNode(name = wordItem.name, Label = "Word", attributes = wordItem.__dict__)
        # 单词出处不存在，创建该出处
        result = self.findNodeByName(name = wordSource.name, Label = "WordSource", attributes = wordSource.__dict__)
        if len(result) == 0:
            print(f"节点不存在：{wordSource.name}, WordSource")
            self.createNode(name = wordSource.name, Label = "WordSource", attributes = wordSource.__dict__)
        
        # 建立单词和出版社之间的联系
        self.createRelationship(
            head_label="WordSource", head_name = wordSource.name, head_attributes = wordSource.__dict__, 
            tail_label="Word", tail_name = wordItem.name, tail_attributes = wordItem.__dict__,
            rel_type="HAS_WORD", rel_attributes = relation_attributes
        )
        # # 建立单词和词性之间的关系, 待实现
        # has_part_of_speech = list()
        # for mean in wordItem.meaning:
        #     if "." in 



    
if __name__ == '__main__':
    # neo4j_handler = Neo4jHandler()
    # # res = neo4j_handler.findNodeByName("apple", "Word")
    # name = "hello world"
    # label = "word"
    # res = neo4j_handler.createNode(name, label)

    # name = "hello feynmind"
    # label = "word"
    # res = neo4j_handler.createNode(name, label)

    # head_name = "hello feynmind"
    # head_label = "word"
    # head_attributes = dict()
    # tail_name = "hello world"
    # tail_label = "word"
    # tail_attributes = dict()
    # rel_type = "sameMeaning"
    # rel_attributes = dict()
    # neo4j_handler.createRelationship(head_label, head_name, head_attributes, tail_label, tail_name, tail_attributes, rel_type, rel_attributes)

    neo4j_handler = Neo4jHandler()
    word = "Thrust"
    source_attribute = {
        "publisher" : "人民教育出版社",
        "grade" : "九年级",
        "edition" : "2013年",
        "volume" : "全一册",
        "name" : "人民教育出版社-2013年-九年级-全一册"
    }
    relation_attributes = {"Unit" : "Unit 1"}
    neo4j_handler.create_word(word, source_name=source_attribute["name"], source_attributes=source_attribute, relation_attributes=relation_attributes)