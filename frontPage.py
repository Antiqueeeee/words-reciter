import streamlit as st
import requests
from config import *
import json

# 初始化session_state
if 'publisher' not in st.session_state:
    st.session_state.publisher = None
if 'grade' not in st.session_state:
    st.session_state.grade = None
if 'volume' not in st.session_state:
    st.session_state.volume = None
if 'edition' not in st.session_state:
    st.session_state.edition = None
if 'unit' not in st.session_state:
    st.session_state.unit = None
if 'show_words' not in st.session_state:
    st.session_state.show_words = False
if 'word_index' not in st.session_state:
    st.session_state.word_index = 0

# Streamlit 应用
st.title("英语单词背诵助手")

# 筛选条件
st.sidebar.header("筛选条件")
filter_type = st.sidebar.radio("选择筛选方式", ("Publisher/Edition/Grade/Volume/Unit", "ExamType/Unit"))

if filter_type == "Publisher/Edition/Grade/Volume/Unit":
    # Publisher 选择
    publishers = requests.post(INTERFACE_GET_PUBLISHERS).json()
    publisher = st.sidebar.selectbox("Publisher", publishers, key="publisher_select")
    
    if publisher:
        st.session_state.publisher = publisher
        # Grade 选择
        grades = requests.post(INTERFACE_GET_GRADES, json={"publisher": publisher}).json()
        grade = st.sidebar.selectbox("Grade", grades, key="grade_select")
        
        if grade:
            st.session_state.grade = grade
            # Volume 选择
            volumes = requests.post(INTERFACE_GET_VOLUMES, json={"publisher": publisher, "grade": grade}).json()
            volume = st.sidebar.selectbox("Volume", volumes, key="volume_select")
            
            if volume:
                st.session_state.volume = volume
                # Edition 选择
                editions = requests.post(INTERFACE_GET_EDITIONS, json={"publisher": publisher, "grade": grade, "volume": volume}).json()
                edition = st.sidebar.selectbox("Edition", editions, key="edition_select")
                
                if edition:
                    st.session_state.edition = edition
                    # Unit 选择
                    units = requests.post(INTERFACE_GET_UNITS, json={"publisher": publisher, "grade": grade, "volume": volume, "edition": edition}).json()
                    unit = st.sidebar.selectbox("Unit", units, key="unit_select")
                    
                    if unit:
                        st.session_state.unit = unit
                        
                        # 添加"显示单词"按钮
                        if st.sidebar.button("显示单词"):
                            st.session_state.show_words = True
else:
    # ExamType/Unit 选择逻辑（保持不变）
    exam_type = st.sidebar.selectbox("Exam Type", ["Exam1", "Exam2"])
    unit = st.sidebar.selectbox("Unit", ["Unit1", "Unit2"])

# 新增转义函数
def escape_markdown(text):
    """转义Markdown特殊字符"""
    if isinstance(text, list):
        return [escape_markdown(str(item)) for item in text]
    text = str(text)
    # 转义Markdown特殊字符
    replacements = {
        '*': '\\*',
        # '_': '\\_',
        '`': '\\`',
        '#': '\\#',
        '~': '\\~',
        '>': '\\>',
        '<': '\\<'
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text



# 使用帮助内容
help_content = """
## 使用指南

欢迎使用英语单词背诵助手！请按照以下步骤操作：

1. 在左侧边栏选择筛选条件
2. 逐级选择出版社、年级、卷次、版本和单元
3. 点击"显示单词"按钮开始学习
4. 使用"上一个"/"下一个"按钮切换单词

功能说明：
- 点击喇叭图标可播放发音
- 单词信息包含：发音规则、例句、历史演变等
- 支持中英文对照学习

Tips：
- 可以点击侧边栏顶部的">"按钮收起侧边栏
- 按F11进入全屏模式更专注学习
"""

# 根据状态显示内容
if not st.session_state.show_words:
    # 显示使用帮助
    st.markdown(help_content)
else:
    # 显示单词内容
    filtered_words = requests.post(INTERFACE_PUBLISHER_SELECT_WORD, json={
        "publisher": st.session_state.publisher,
        "grade": st.session_state.grade,
        "volume": st.session_state.volume,
        "edition": st.session_state.edition,
        "unit": st.session_state.unit
    }).json()
    filtered_words = json.loads(filtered_words)

    if filtered_words:
        word = filtered_words[st.session_state.word_index]
        # 在显示前处理数据
        word = {
            key: escape_markdown(value) 
            for key, value in word.items()
        }
        # 清理空数据
        for key, value in word.items():
            if value and (isinstance(value, (list, str, dict))) and len(value) == 0:
                word[key] = None

        # 显示单词信息
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(f"单词: {word['name']}")
        with col2:
            if word.get('pronunciationFilePath'):
                st.audio(word['pronunciationFilePath'])

        with st.expander("发音信息", expanded=True):
            rules = '\n  '.join([f'• {rule}' for rule in word.get('pronunciationRules', [])]) or '暂无'
            st.markdown(f"""
            - 音标: {', '.join(word['pronunciation']) if word.get('pronunciation') else '暂无'}
            - 发音规则:  
            {rules}
            """)

        with st.expander("详细释义", expanded=True):
            content = (
                "**核心含义**  \n" +
                ', '.join(word.get('meaning', ['暂无'])).replace('*', '\\*') + "\n\n" +
                "**典型例句**  \n" +
                ''.join([f'- {sentence}\n' for sentence in word.get('exampleSentences', [])]) + "\n\n" +
                "**搭配用法**  \n" +
                word.get('collocations', '暂无').replace('*', '\\*')
            )
            st.markdown(content)

        # 翻页控制
        col_prev, _, col_next = st.columns([2, 6, 2])
        with col_prev:
            if st.button("⏮ 上一个", disabled=st.session_state.word_index == 0):
                st.session_state.word_index -= 1
                st.rerun()
        with col_next:
            if st.button("⏭ 下一个", disabled=st.session_state.word_index == len(filtered_words)-1):
                st.session_state.word_index += 1
                st.rerun()

        # 显示进度
        st.caption(f"进度: {st.session_state.word_index + 1}/{len(filtered_words)}")
        
        # 添加返回按钮
        if st.button("返回选择界面"):
            st.session_state.show_words = False
            st.session_state.word_index = 0
            st.rerun()
    else:
        st.warning("未找到匹配的单词")
        if st.button("重新选择"):
            st.session_state.show_words = False
            st.session_state.word_index = 0
            st.rerun()