import os, sys
current_path = os.path.abspath(os.path.join(__file__, os.pardir))
project_path = os.path.abspath(os.path.join(current_path, os.pardir))
sys.path.append(project_path)

from Basements.neo4j_handler import Neo4jHandler
from Basements.miscellany import Miscellany
from Basements.ItemWord import WordItem
import pandas as pd

class DataManager:
    def __init__(self):
        self.neo4j_handler = Neo4jHandler()
        self.tools = Miscellany()

    def upload_words_from_xlsx(self, xlsx_path):
        df = pd.read_excel(xlsx_path)
        file_name, file_extension = os.path.splitext(os.path.basename(xlsx_path))
        wordsource = self.tools.filename_parsing(file_name)
        
        for index, row in df.iterrows():
            word, pronunce, meaning, unit = row["单词"], row["音标"], row["含义"], row["单元"]
            
            wordItem = WordItem(word, pronunce, meaning, wordsource)
