import os, sys
current_path = os.path.abspath(os.path.join(__file__, os.pardir))
project_path = os.path.abspath(os.path.join(current_path, os.pardir))
sys.path.append(project_path)

from Basements.neo4jEngine import Neo4jHandler
from Basements.miscellany import Miscellany
from Basements.ItemWord import WordItem
import pandas as pd
from tqdm import tqdm

class DataManager:
    def __init__(self):
        self.neo4j_handler = Neo4jHandler()
        self.tools = Miscellany()

    def upload_words_from_xlsx(self, xlsx_path):
        df = pd.read_excel(xlsx_path)
        file_name, file_extension = os.path.splitext(os.path.basename(xlsx_path))
        wordSource = self.tools.filename_parsing(file_name)
        for index, row in tqdm(df.iterrows()):
            word, pronunce, meaning, unit = row["单词"], row["音标"], row["含义"], row["单元"]
            meaning = meaning.split("\n")
            wordItem = WordItem(name=word, pronunciation = pronunce, meaning = meaning)
            self.neo4j_handler.create_word(wordItem = wordItem, wordSource = wordSource , relation_attributes = {"Unit" : unit})



if __name__ == "__main__":
    manager = DataManager()
    xlsx_path = r'C:\FeynmindPython\words-reciter\Examples\人民教育出版社-2014年3月第一版-九年级-全一册.xlsx'
    manager.upload_words_from_xlsx(xlsx_path)
