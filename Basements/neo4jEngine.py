from neo4j import GraphDatabase
import os, sys
current_path = os.path.abspath(os.path.join(__file__, os.pardir))
project_path = os.path.abspath(os.path.join(current_path, os.pardir))
sys.path.append(project_path)

import json
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

    def findNodeByType(self, label, node_attributes = dict()) -> list:
        '''
        根据类型查询所有节点
        
        Args:
        label: 节点类型
        node_attributes: 节点属性

        Returns:
        list: 节点列表
        '''
        driver = self.neo4j_connect()
        with driver.session() as session:
            query = f"MATCH (n:{label})"
            if len(node_attributes) > 0:
                query += " WHERE "
                query += " AND ".join([f"n.{key} = ${key}" for key in node_attributes.keys()])
            query += " RETURN n"
            result = session.run(query, **node_attributes)
            res = result.data()
        self.close(driver)
        if len(res) > 0 :
            for i in res:
                i["n"]["节点类型"] = label
        return res

    def findRelatedNode(self, node_name, node_label, rel_type, node_attributes = dict(), rel_attributes=dict()) -> list:
        node_attributes["name"] = node_name
        driver = self.neo4j_connect()
        # 准备关系属性
        rel_attributes_prefixed = {f"rel_{k}": v for k, v in rel_attributes.items()}
        all_params = {**node_attributes, **rel_attributes_prefixed}
        result = list()
        with driver.session() as session:
            # 构建查询
            query = f"MATCH (basic:{node_label})-[r:{rel_type}]->(n) WHERE "
            query += " AND ".join([f"basic.{key} = ${key}" for key in node_attributes.keys()])
            if rel_attributes:
                query += " AND " + " AND ".join([f"r.{k} = $rel_{k}" for k in rel_attributes.keys()])
            query += " RETURN n"

            # 打印填入真实值的Cypher查询
            formatted_query = query
            for key, value in all_params.items():
                formatted_query = formatted_query.replace(f"${key}", repr(value))
            print("Formatted Cypher query:")
            print(formatted_query)

            # 执行查询
            res = session.run(query, **all_params)
            result = res.data()
        self.close(driver)
        return result

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

    def findRelationAttributes(
        self, head_label, tail_label, target_rel_attributes
        , head_attributes=dict(), tail_attributes=dict()
        , rel_type=None, rel_attributes=dict()
        , head_name=None, tail_name=None
    ) -> list:
        """
        查询两个节点之间关系的特定属性，并返回去重结果
        
        Args:
            head_label: 头节点标签
            tail_label: 尾节点标签
            target_rel_attributes: 需要查询的关系属性列表，必填
            head_attributes: 头节点属性条件字典
            tail_attributes: 尾节点属性条件字典
            rel_type: 关系类型
            rel_attributes: 关系属性条件字典
            head_name: 头节点名称（可选）
            tail_name: 尾节点名称（可选）
        
        Returns:
            list: 包含指定关系属性去重值的列表
        """
        if not target_rel_attributes:
            raise ValueError("target_rel_attributes must not be empty")
        
        # 如果提供了name，添加到对应的属性字典中
        if head_name is not None:
            head_attributes["name"] = head_name
        if tail_name is not None:
            tail_attributes["name"] = tail_name
        
        # 为头尾节点的属性添加前缀以区分
        head_attributes_prefixed = {f"head_{k}": v for k, v in head_attributes.items()}
        tail_attributes_prefixed = {f"tail_{k}": v for k, v in tail_attributes.items()}
        rel_attributes_prefixed = {f"rel_{k}": v for k, v in rel_attributes.items()}
        
        # 合并所有参数
        all_params = {
            **head_attributes_prefixed,
            **tail_attributes_prefixed,
            **rel_attributes_prefixed
        }
        
        driver = self.neo4j_connect()
        result = list()
        
        with driver.session() as session:
            # 构建基本查询
            query = f"MATCH (head:{head_label})-[r{':' + rel_type if rel_type else ''}]->(tail:{tail_label})"
            
            where_conditions = []
            
            # 添加头节点属性条件
            if head_attributes:
                where_conditions.extend([f"head.{key} = $head_{key}" for key in head_attributes.keys()])
            
            # 添加尾节点属性条件
            if tail_attributes:
                where_conditions.extend([f"tail.{key} = $tail_{key}" for key in tail_attributes.keys()])
            
            # 添加关系属性条件
            if rel_attributes:
                where_conditions.extend([f"r.{k} = $rel_{k}" for k in rel_attributes.keys()])
            
            # 只有在有where条件时才添加WHERE子句
            if where_conditions:
                query += " WHERE " + " AND ".join(where_conditions)
            
            # 返回指定的关系属性
            return_items = [f"DISTINCT r.{attr}" for attr in target_rel_attributes]
            query += f" RETURN {', '.join(return_items)}"
            
            # 打印填入真实值的Cypher查询（用于调试）
            formatted_query = query
            for key, value in all_params.items():
                formatted_query = formatted_query.replace(f"${key}", repr(value))
            print("Formatted Cypher query:")
            print(formatted_query)
            
            # 执行查询
            res = session.run(query, **all_params)
            result = res.data()
        
        self.close(driver)
        return result


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

    # 测试根据头尾节点查询关系属性：
    neo4j_handler = Neo4jHandler()
    head_label = "WordSource"
    tail_label = "Word"
    rel_type = "HAS_WORD"
    target_rel_attributes = ["Unit"]
    result = neo4j_handler.findRelationAttributes(head_label=head_label, tail_label=tail_label, rel_type=rel_type, target_rel_attributes=target_rel_attributes)
    print("***")
    print(result)

    # # 测试创建节点
    # neo4j_handler = Neo4jHandler()
    # # res = neo4j_handler.findNodeByName("apple", "Word")
    # name = "hello world"
    # label = "word"
    # res = neo4j_handler.createNode(name, label)

    # name = "hello feynmind"
    # label = "word"
    # res = neo4j_handler.createNode(name, label)

    # # 测试关系建立
    # neo4j_handler = Neo4jHandler()
    # head_name = "hello feynmind"
    # head_label = "word"
    # head_attributes = dict()
    # tail_name = "hello world"
    # tail_label = "word"
    # tail_attributes = dict()
    # rel_type = "sameMeaning"
    # rel_attributes = dict()
    # neo4j_handler.createRelationship(head_label, head_name, head_attributes, tail_label, tail_name, tail_attributes, rel_type, rel_attributes)

    # # 测试单词上传
    # neo4j_handler = Neo4jHandler()
    # word = "Thrust"
    # source_attribute = {
    #     "publisher" : "人民教育出版社",
    #     "grade" : "九年级",
    #     "edition" : "2013年",
    #     "volume" : "全一册",
    #     "name" : "人民教育出版社-2013年-九年级-全一册"
    # }
    # relation_attributes = {"Unit" : "Unit 1"}
    # neo4j_handler.create_word(word, source_name=source_attribute["name"], source_attributes=source_attribute, relation_attributes=relation_attributes)

    # #  测试查询相关节点功能， 根据出版社查询单词
    # neo4j_handler = Neo4jHandler()
    # word = "Thrust"
    # source_attribute = {
    #     "publisher" : "人民教育出版社",
    #     "grade" : "九年级",
    #     "edition" : "2014年3月第一版",
    #     "volume" : "全一册",
    #     "name" : "人民教育出版社-2014年3月第一版-九年级-全一册"
    # }
    # relation_attributes = {"Unit" : "Unit 1"}
    # relation_type = "HAS_WORD"
    # res = neo4j_handler.findRelatedNode(
    #     node_name = source_attribute["name"], node_label = "WordSource", rel_type = relation_type,
    #     node_attributes = source_attribute, rel_attributes = relation_attributes
    # )
    # print(len(res))

    # # 测试根据类型查询节点
    # neo4j_handler = Neo4jHandler()
    # label = "WordSource"
    # res = neo4j_handler.findNodeByType(label)
    # print(len(res),"\n",res)

