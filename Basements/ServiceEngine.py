import os, sys

current_path = os.path.abspath(os.path.join(__file__, os.pardir))
project_path = os.path.abspath(os.path.join(current_path, os.pardir))
sys.path.append(project_path)

from Basements.neo4jEngine import Neo4jHandler
from Basements.miscellany import Miscellany
from Basements.ItemWord import WordItem
from Basements.GPTEngine import GPTEngine
import pandas as pd

from config import WORD_COMPLETION_TEMPLATE
class ServiceEngine:
    def __init__(self):
        self.neo4j_handler = Neo4jHandler()
        self.tools = Miscellany()
        self.gpt = GPTEngine()

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
    
    def publisher_select_word(self, publisher: str, grade: str, edition: str, volume: str, unit: str = None) -> list:
        '''
        根据出版社相关信息和单元查找单词
        Args:
            publisher: str 
            grade: str
            edition: str
            volume: str
            unit: str (optional)
        Returns:
            list: 前端可显示的单词查询结果
        '''
        node_name = f"{publisher}-{edition}-{grade}-{volume}"
        node_label = "WordSource"
        
        if unit:
            rel_attributes = {"Unit": unit}
        else:
            rel_attributes = {}
        
        results = self.neo4j_handler.findRelatedNode(
            node_name=node_name,
            node_label=node_label,
            rel_type="HAS_WORD",
            rel_attributes=rel_attributes
        )
        
        results = [WordItem(**node["n"]).__dict__ for node in results]
        return results


    def stored_word_completion(self):
        to_be_generated_words = self.neo4j_handler.findNodeByType(
            label = "Word"
            ,node_attributes = {"search_flag":-1}
        )
        to_be_generated_words = [node["n"] for node in to_be_generated_words]
        return to_be_generated_words

    def publisher_words_export(self, publisher : str, grade : str, edition : str, volume : str, unit : str, searchFlag = -1) -> str:
        results = self.publisher_select_word(publisher, grade, edition, volume, unit)
        words = list()
        for word in results:
            if word["searchFlag"] != searchFlag:
                continue
            for key, value in word.items():
                if isinstance(value, list):
                    word[key] = "\n".join(value)
            words.append(word)
        frame = pd.DataFrame(words)
        
        current = self.tools.time_now(format='%Y%m%d')
        filename = current + "-" + publisher + "-" + edition + "-" + grade + "-" + volume + "-" + unit  + ".csv"
        file_path = os.path.join(project_path, "Examples", "Exports", filename)
        return frame.to_csv(file_path, index = False, encoding = "utf-8-sig")

    def gpt_generate_wordinfo(self, word : str):
        prompt = WORD_COMPLETION_TEMPLATE.format(word=word)
        response = self.gpt.chat(prompt = prompt,left_tag="{", right_tag="}")
        return response


if __name__ == "__main__":
    # 页面上要显示学习进度，页面上有，但不明显
    # 增加控制是否显示单词含义的开关
    # 页面上显示单词相关的知识图谱
    # 播放按钮不太好用
    # 单元列表不是按顺序排列的
    # 点击显示单词切换单元后，进度没有重置
    # 单词顺序和书上不一致

    # 测试按出版社信息导出单词
    manager = ServiceEngine()
    results = manager.publisher_words_export(
        publisher = "人民教育出版社"
        , grade = "九年级"
        , edition = "2014年3月第一版"
        , volume = "全一册"
        , unit = "Unit 1"
    )

    # # 测试根据出版社信息查询有哪些单元
    # publisher = "人民教育出版社"
    # grade = "九年级"
    # edition = "2014年3月第一版"
    # volume = "全一册"
    # manager = ServiceEngine()
    # results = manager.get_unit(publisher, grade, volume, edition)
    # print(results)

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