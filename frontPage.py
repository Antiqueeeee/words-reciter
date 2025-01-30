import streamlit as st
import requests
from config import *
import json
import pandas as pd

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

# 显示选择的筛选条件
st.write("当前选择:")
st.write(f"出版社: {st.session_state.publisher}")
st.write(f"年级: {st.session_state.grade}")
st.write(f"卷: {st.session_state.volume}")
st.write(f"教材版本号: {st.session_state.edition}")
st.write(f"单元: {st.session_state.unit}")

# 显示单词信息
if st.session_state.show_words:
    # 这里需要根据选择的条件获取实际的单词列表
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
        for key,value in word.items():
            if value  and (isinstance(value, list) or isinstance(value, str) or isinstance(value, dict)):
                if len(value) == 0:
                    word[key] = None

            # if not value or pd.isnull(value):
            #     word[key] = None

        print(f"!!!!filtered_words!!!!!:{type(word)}\n{word}\n\n")
        st.subheader(word['name'])
        st.write("发音: <br>", ", ".join(word['pronunciation']) if word['pronunciation'] else None)
        st.write("发音方式: <br>", "<br>".join(word['pronunciationRules']))
        st.write("含义: ", ", ".join(word['meaning']))
        if word['pronunciationFilePath']:
            st.audio(word['pronunciationFilePath'])
        st.write("例句: ", " ".join(word['exampleSentences']) if word['exampleSentences'] else None)
        st.write("历史: ", word['history'])
        st.write("搭配用法: ", word['collocations'])
        

        # 翻页按钮
        col1, col2 = st.columns(2)
        with col1:
            if st.button("上一个单词", disabled=st.session_state.word_index == 0):
                st.session_state.word_index -= 1
        with col2:
            if st.button("下一个单词", disabled=st.session_state.word_index == len(filtered_words) - 1):
                st.session_state.word_index += 1
    else:
        st.write("没有找到符合条件的单词。")
