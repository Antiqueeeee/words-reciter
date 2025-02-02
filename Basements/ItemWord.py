from dataclasses import dataclass, field
from typing import List, Optional

# 图谱中的实体类型
@dataclass
class Wordaffix:
    name : str # 词缀
    affixMeaning : str # 词缀含义

@dataclass
class WordItem:
    index: int # 单词在单词表中的序号
    name: str  # 单词
    meaning: List[str]  # 单词含义, 用WordMeaning主要限制存储的内容，本质上就是str
    searchFlag : int = -1 # 搜索标记
    pronunciationFilePath: Optional[str] = str()  # 发音文件路径
    exampleSentences: Optional[List[str]] = field(default_factory=list)  # 例句
    history: Optional[str] = str()  # 发展历史和文化背景
    collocations: Optional[str] = str()  # 搭配用法
    pronunciation: Optional[List[str]] = field(default_factory=list)  # 发音
    pronunciationRules: Optional[List[str]] = field(default_factory=list)  # 发音规则

@dataclass
class WordSource:
    # 将出版社、年级、年份、考试类型等都合并到Source当中 
    # 那也应该有一个存储的规范，如果是教材上的单词，要有出版社、版本号、年份、年级、上下册等
    # 如果是考试，那就有考试类型就行 
    # 如果是CET4、GRE之类的
    name: str  # 节点名称
    publisher: Optional[str] = str()  # 出版社
    grade: Optional[str] = str()  # 年级
    examType: Optional[str] = str()  # 考试类型
    edition: Optional[str] = str()  # 版次
    volume: Optional[str] = str()  # 上下册


@dataclass
class WordPartOfSpeech: # 只有固定的几个，V、ADV、ADJ等等
    name : str # 词性
    

# 图谱中与Word类有关联的节点类型
@dataclass
class WordHasRelationship:
    HAS_AFFIX : List[Wordaffix] # 词缀 Contains-Affix
    partOfSpeech : List[WordPartOfSpeech]  # 单词具备的词性，可以通过单词含义得到 Contains-PartOfSpeech
    HAS_SYNONYMS : List[WordItem] # 同义词 Contains-Synonyms
    HAS_LOOKALIKEWORDS : List[WordItem] # 形近词 Contains-LookAlikeWords
    HAS_INFLECTIONS : List[WordItem] # 变形 Contains-Inflections
    rootWord : List[WordItem] # 根单词,词根 Contains-Root
    HAS_WORD : List[WordSource] # 来源 ComesFrom








# 单词表
# https://www.sohu.com/a/485193126_121124286

# class WordSentence:
#     sentence : str # 原句子
#     translation_chinese : str # 中文翻译

# class WordInflections:
#     word : str # 变形单词
#     meaning : str # 变形含义
#     part_of_speech : str # 变形词性


# class WordMeaning: 
#     # 不同词性可能对应不同含义
#     meaning : str # 意思
#     current_part_of_speech : str # 当前词性