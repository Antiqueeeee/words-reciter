import os, sys
current_path = os.path.abspath(os.path.join(__file__, os.pardir))
project_path = os.path.abspath(os.path.join(current_path, os.pardir))
sys.path.append(project_path)

from Basements.neo4jEngine import Neo4jHandler
from Basements.miscellany import Miscellany
from Basements.ItemWord import WordItem
from Basements.ServiceEngine import ServiceEngine
import pandas as pd
from tqdm import tqdm

class DataManager:
    def __init__(self):
        self.neo4j_handler = Neo4jHandler()
        self.tools = Miscellany()
        self.service_engine = ServiceEngine()

    def upload_words_from_xlsx(self, xlsx_path):
        df = pd.read_excel(xlsx_path)
        file_name, file_extension = os.path.splitext(os.path.basename(xlsx_path))
        wordSource = self.tools.filename_parsing(file_name)
        for index, row in tqdm(df.iterrows()):
            word, pronunce, meaning, unit = row["单词"], row["音标"], row["含义"], row["单元"]
            meaning = meaning.split("\n")
            pronunce = [pronunce] if not pd.isnull(pronunce) else list()
            wordItem = WordItem(name=word, pronunciation = pronunce, meaning = meaning)
            self.neo4j_handler.create_word(wordItem = wordItem, wordSource = wordSource , relation_attributes = {"Unit" : unit})

    def store_words_completion(self, publisher : str, grade : str, edition : str, volume : str, unit : str, searchFlag = -1):
        word_info_list = ["pronunciationRules", "exampleSentences"]
        node_info_list = ["Affix", "Synonyms", "LookAlikeWords", "Inflections"]
        results = self.service_engine.publisher_select_word(publisher, grade, edition, volume, unit)
        results = [res for res in results if res["searchFlag"] == searchFlag]
        for result in results:
            _relatione_nodes, relatione_nodes = list(), list()
            update_attributes = dict()
            response = self.service_engine.gpt_generate_wordinfo(result["name"])
            # response = {'pronunciationRules': [], 'exampleSentences': [{'example': 'Alexander Graham Bell is best known for inventing the telephone.', 'translate': '亚历山大·格拉汉姆·贝尔以发明电话而闻名。'}, {'example': 'In 1876, Bell was awarded the first US patent for the invention of the telephone.', 'translate': '1876年，贝尔因电话的发明而获得了美国第一项专利。'}, {'example': 'Bell also worked on various other scientific projects, including advancements in aerodynamics.', 'translate': '贝尔还参与了包括空气动力学进步在内的其他科学项目。'}], 'Affix': [{"affix":"pro-","meaning":"向前，在前面"},{"affix":"-ject","meaning":"扔或投掷"}], 'synonyms': [], 'lookAlikeWords': [], 'inflections': []}
            # 收集需要更新的属性和建立联系的节点
            for key, value in response.items():
                if key in word_info_list:
                    update_attributes[key] = value
                elif key in node_info_list:
                    for v in value:
                        v["label"] = key
                    if len(value) > 0:
                        _relatione_nodes.extend(value)
            
            # 将数据转换成图谱可用的数据
            # 是不是应该以类型为单位去更新数据，而不是面向具体节点去更新数据？要更新节点把所有节点先封装成Word类型，然后实现一个更新属性的方法接入word类型数据，然后再修改数据
            update_attributes["exampleSentences"] = [sentence["example"] + "\n" + sentence["translate"] for sentence in update_attributes["exampleSentences"]]
            for i in _relatione_nodes:
                if i["label"] == "Inflections" :
                    if i["word"] != result["name"]:
                        relatione_nodes.append(i)
                elif i["label"] == "Synonyms":
                    if i["word"] != result["name"]:
                        relatione_nodes.append(i)
                elif i["label"] == "LookAlikeWords":
                    if i["word"] != result["name"]:
                        relatione_nodes.append(i)           
                else:
                    relatione_nodes.append(i)
            # 更新节点信息
            self.neo4j_handler.update_node_attributes(label = "Word", node_name = result["name"], node_attributes = update_attributes)
            # 建立关联节点
            for node in relatione_nodes:
                label = node.pop("label")
                if label == "Affix":
                    node_name = node.pop("affix")
                    node_label = "Affix"
                    relation_name = "HAS_AFFIX"
                elif label in ["Synonyms", "LookAlikeWords", "Inflections"] :
                    node_name = node.pop("word")
                    node_label = "Word"
                    relation_name = f"HAS_{label.upper()}"
                else:
                    raise ValueError(f"Invalid node name: \n{node}")

                # 检查节点是否存在，如果存在直接建立关系，如果不存在，创建节点并建立关系
                stored = self.neo4j_handler.findNodeByName(name = node_name, label = node_label)
                if len(stored) == 0:
                    self.neo4j_handler.createNode(name = node_name, label = node_label, attributes = node)

                 # 有BUG，当前这次的数据没有存储到neo4j中，因为当前数据和历史数据大概率不会完全一致，没想好要如何融合
                self.neo4j_handler.createRelationship(
                    head_label="Word", head_name=result["name"],
                    tail_label=node_label, tail_name=node_name,
                    rel_type=relation_name,
                    head_attributes=dict(),
                    tail_attributes=dict(),
                )
            # 处理完成后，将节点更新为不需要再补全的状态（0），审核后变为（1）
            self.neo4j_handler.update_node_attributes(label = "Word", node_name = result["name"], node_attributes = {"searchFlag": 0})



            
        


if __name__ == "__main__":
    # 测试上传单词功能
    manager = DataManager()
    xlsx_path = r'C:\FeynmindPython\words-reciter\Examples\Uploads\人民教育出版社-2014年3月第一版-九年级-全一册.xlsx'
    manager.upload_words_from_xlsx(xlsx_path)


    # 测试单词信息补全
    manager = DataManager()
    manager.store_words_completion(
        publisher = "人民教育出版社",
        grade = "九年级",
        edition = "2014年3月第一版",
        volume = "全一册",
        unit = "Unit 1",
    )

