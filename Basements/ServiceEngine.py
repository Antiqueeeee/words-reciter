import os, sys

from requests import head
current_path = os.path.abspath(os.path.join(__file__, os.pardir))
project_path = os.path.abspath(os.path.join(current_path, os.pardir))
sys.path.append(project_path)

from Basements.neo4jEngine import Neo4jHandler
from Basements.miscellany import Miscellany
from Basements.ItemWord import WordItem

class ServiceEngine:
    def __init__(self):
        self.neo4j_handler = Neo4jHandler()
        self.tools = Miscellany()

    def get_publisher(self) -> list:
        '''
        获取当前数据库中都有哪些出版社
        '''
        results = self.neo4j_handler.findNodeByType(
            label = "WordSource"
        )
        results = [node["n"]["publisher"] for node in results]
        return results

    def get_grade(self, publisher) -> list:
        '''
        获取当前出版社中中有哪些年级
        '''
        results = self.neo4j_handler.findNodeByType(
            label = "WordSource"
            ,node_attributes = {"publisher": publisher}
        )
        results = [node["n"]["grade"] for node in results]
        return results

    def get_volume(self, publisher, grade) -> list:
        results = self.neo4j_handler.findNodeByType(
            label = "WordSource"
            ,node_attributes = {"publisher": publisher, "grade": grade}
        )
        results = [node["n"]["volume"] for node in results]
        return results

    def get_edition(self, publisher, grade, volume) -> list:
        results = self.neo4j_handler.findNodeByType(
            label = "WordSource"
            ,node_attributes = {"publisher": publisher, "grade": grade, "volume": volume}
        )
        results = [node["n"]["edition"] for node in results]
        return results

    def get_unit(self, publisher, grade, volume, edition) -> list:
        target_rel_attributes = ["Unit"]
        head_label = "WordSource"
        head_attributes = {"publisher": publisher, "grade": grade, "volume": volume, "edition": edition}
        results = self.neo4j_handler.findRelationAttributes(
            head_label = head_label,
            head_attributes = head_attributes
            ,rel_type = "HAS_WORD"
            ,tail_label = "Word"
            ,target_rel_attributes = target_rel_attributes
        )
        results = [rel["r.Unit"] for rel in results]
        return results
    
    def publisher_select_word(self, publisher : str, grade : str, edition : str, volume : str, unit : str) -> list:
        '''
        根据出版社相关信息和单元查找单词
        Args:
            publisher: str 
            grade: str
            edition: str
            volume: str
        Returns:
            list: 前端可显示的单词查询结果
        '''
        results = self.neo4j_handler.findRelatedNode(
            node_name = publisher + "-" + edition + "-" + grade + "-" + volume
            , node_label = "WordSource"
            , rel_type = "HAS_WORD"
            , rel_attributes = {"Unit" : unit}
        )
        results = [WordItem(**node["n"]).__dict__ for node in results]
        return results


if __name__ == "__main__":
    # 测试根据出版社信息查询有哪些单元
    publisher = "人民教育出版社"
    grade = "九年级"
    edition = "2014年3月第一版"
    volume = "全一册"
    manager = ServiceEngine()
    results = manager.get_unit(publisher, grade, volume, edition)
    print(results)

    # # 测试根据出版是、年级、版本，查询册数
    # publisher = "人民教育出版社"
    # grade = "九年级"
    # edition = "2014年3月第一版"
    # manager = ServiceEngine()
    # results = manager.get_volume(publisher, grade, edition)
    # print(len(results),results)

    # # 测试根据出版社、年级查询有哪些版本
    # publisher = "人民教育出版社"
    # grade = "九年级"
    # manager = ServiceEngine()
    # results = manager.get_edition(publisher, grade)
    # print(results)

    # # 测试根据出版社查询有哪些年级:
    # publisher = "人民教育出版社"
    # manager = ServiceEngine()
    # results = manager.get_grade(publisher)
    # print(results)

    # # 测试获取图谱中的出版社
    # manager = ServiceEngine()
    # results = manager.get_publisher()
    # print(results)
    
    # # 测试根据出版信息找单词
    # manager = ServiceEngine()
    # results = manager.publisher_select_word(
    #     publisher = "人民教育出版社"
    #     , grade = "九年级"
    #     , edition = "2014年3月第一版"
    #     , volume = "全一册"
    #     , unit = "Unit 1"
    # )
    # print(len(results))