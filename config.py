from dotenv import load_dotenv
import os

mode = os.getenv('env', 'dev')
load_dotenv(mode + '.env')

NEO4J_URI = os.getenv('NEO4J_URI', "http://localhost:7474")
NEO4J_USER = os.getenv('NEO4J_USER', "neo4j")
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', "neo4j")

SERVER_PORT = int(os.getenv('SERVER_PORT', '8000'))
SERVER_HOST = os.getenv('SERVER_HOST', "127.0.0.1")

# General settings
TTS_DEFAULT_PARMS = {"VOICE" : "en-US-SteffanNeural", "RATE": -30, "VOLUME": 50, "PITCH": 0}
DEFAULT_GPT_MODEL = "gpt-4o"
GPT_MODELS = {
    "gpt-4o" : {
        "base_url" : "https://api2.aigcbest.top/v1",
        "api_key" : "sk-32vbc0ESSkP2NdjpWVJDZRVDVjPKyX6RyHv8kbuRIOIvou13",
    }
}


# Interfaces
INTERFACE_PUBLISHER_SELECT_WORD = f"http://127.0.0.1:{SERVER_PORT}/publisher_select_word"
INTERFACE_GET_PUBLISHERS = f"http://127.0.0.1:{SERVER_PORT}/get_publisher"
INTERFACE_GET_GRADES = f"http://127.0.0.1:{SERVER_PORT}/get_grades"
INTERFACE_GET_VOLUMES = f"http://127.0.0.1:{SERVER_PORT}/get_volumes"
INTERFACE_GET_EDITIONS = f"http://127.0.0.1:{SERVER_PORT}/get_editions"
INTERFACE_GET_UNITS = f"http://127.0.0.1:{SERVER_PORT}/get_units"


# Prompt
WORD_COMPLETION_TEMPLATE = '''
我希望你能扮演一位能帮助中国学生学习英语单词、了解美国、英国文化的老师，通过讲解单词来帮助学生理解单词，达到快速记忆单词的目的。你需要将你分析单词的结果以JSON形式返回。

我会告诉你现在需要你帮我讲解的单词是什么，然后需要你将讲解的结果以JSON形式返回给我，讲解从6个方面进行，具体要求如下：

1. 发音方式（pronunciation）：会读是记忆单词的第一步，学生可以通过读音规则来快速记住单词的拼写。我需要你根据单词进行音节划分，将单词进行分割，每个音节之间用中横线"-"连接，最终结果以List[str]的形式储存。单词可能会有多种发音方式，例如：
   - computer可以被划分为com-pu-ter，则应返回['com-pu-ter']
   - Butterfly可以被划分为But-ter-fly，则应返回['But-ter-fly']
   - 像resume、record这种同形异义词，不同词性有不同发音，那返回的列表中就应该包含多个元素，比如讲解resume的发音方式时应该返回['re-sume','re-su-me']
   - 如果需要讲解的是一个词组，则直接返回空列表[]

2. 例句（examples）：根据当前需要讲解的单词，举3个生活中常用的例子，比如逛街购物时、旅游时等类似生活中常见的场景中会使用到的句子。结果以List[dict]的形式返回，dict中包含example和translate两个字段。例如讲解project的例句时，返回的形式应类似于：
   [
     {{"example":"She is working on a science project for her class that is due next week.","translate":"她正在为班级做一个科学项目，下周截止。"}},
     {{"example":"They plan to project the final presentation onto a large screen for everyone in the auditorium.","translate":"他们计划将最终的演示投影到一个大屏幕上，供礼堂里的所有人观看。"}},
     {{"example":"The community center received a grant to start a new project aimed at helping local youth.","translate":"社区中心获得了一笔拨款，用于启动一个帮助当地青少年的新项目。"}}
   ]

3. 词缀（affix）：当前这个单词包含哪些词缀，这个词缀的含义是什么。以List[dict]的格式返回，dict中包含affix和meaning两个字段。例如讲解单词project时，返回的形式类似于：
   [
     {{"affix":"pro-","meaning":"向前，在前面"}},
     {{"affix":"-ject","meaning":""扔"或"投掷""}}
   ]

4. 同义词（synonyms）：与当前词含义接近的词。以List[dict]的格式返回，dict中包含word和meaning两个字段。如果单词具备多种词性，不同词性之间用\\n进行分隔。例如讲解单词project时，返回的形式类似于：
   [
     {{"word":"scheme","meaning":"n.项目\\nv.密谋；策划"}},
     {{"word":"plan","meaning":"n.计划\\nv.计划"}}
   ]

5. 形近词（lookAlikeWords）：与当前词拼写接近的词。以List[dict]的格式返回，dict中包含word和meaning两个字段。如果单词具备多种词性，不同词性之间用\\n进行分隔。例如讲解单词project时，返回的形式类似于：
   [
     {{"word":"protest","meaning":"n.抗议；反对\\nv.抗议；反对"}},
     {{"word":"protect","meaning":"v.保护"}}
   ]

6. 变形（inflections）：罗列当前单词的原型、第三人称单数形式、过去式、过去分词。以List[dict]的形式按顺序存入。例如讲解单词eat时，返回的形式类似于：
   [
     {{"word":"eat","meaning":"v.吃"}},
     {{"word":"eats","meaning":"v.吃（第三人称单数）"}},
     {{"word":"ate","meaning":"v.吃（过去式）"}},
     {{"word":"eaten","meaning":"v.吃（过去分词）"}}
   ]

现在需要你进行讲解的单词为：{word}
请将分析结果以以下JSON格式返回：
{{
    "pronunciation": [...],
    "examples": [...],
    "affix": [...],
    "synonyms": [...],
    "lookAlikeWords": [...],
    "inflections": [...]
}}
注意不要返回任何多余内容，我会通过“{{”和“}}”两个符号对JSON进行解析
'''


