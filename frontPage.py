import streamlit as st
from typing import List, Optional
from Basements.ItemWord import WordItem

# 示例单词数据
words = [
    WordItem(name="example", meaning=["示例", "例子"], pronunciationFilePath=r"C:\FeynmindPython\words-reciter\Examples\tts.wav",
         exampleSentences=["This is an example sentence."], history="Example history",
         reciteTrick="Example trick", collocations="Example collocations", pronunciation=["ɪɡˈzæmpəl"]),
    # 添加更多单词
]

# Streamlit 应用
st.title("英语单词背诵助手")

# 筛选条件
st.sidebar.header("筛选条件")
filter_type = st.sidebar.radio("选择筛选方式", ("Publisher/Edition/Grade/Volume/Unit", "ExamType/Unit"))

if filter_type == "Publisher/Edition/Grade/Volume/Unit":
    publisher = st.sidebar.selectbox("Publisher", ["Publisher1", "Publisher2"])
    edition = st.sidebar.selectbox("Edition", ["Edition1", "Edition2"])
    grade = st.sidebar.selectbox("Grade", ["Grade1", "Grade2"])
    volume = st.sidebar.selectbox("Volume", ["Volume1", "Volume2"])
    unit = st.sidebar.selectbox("Unit", ["Unit1", "Unit2"])
    # 根据选择筛选单词
    filtered_words = words  # 这里需要根据选择的条件进行实际筛选
else:
    exam_type = st.sidebar.selectbox("Exam Type", ["Exam1", "Exam2"])
    unit = st.sidebar.selectbox("Unit", ["Unit1", "Unit2"])
    # 根据选择筛选单词
    filtered_words = words  # 这里需要根据选择的条件进行实际筛选

# 当前单词索引
if 'word_index' not in st.session_state:
    st.session_state.word_index = 0

# 显示单词信息
if filtered_words:
    word = filtered_words[st.session_state.word_index]
    st.subheader(word.name)
    st.write("含义: ", ", ".join(word.meaning))
    if word.pronunciationFilePath:
        st.audio(word.pronunciationFilePath)
    st.write("例句: ", " ".join(word.exampleSentences))
    st.write("历史: ", word.history)
    st.write("背诵技巧: ", word.reciteTrick)
    st.write("搭配用法: ", word.collocations)
    st.write("发音: ", ", ".join(word.pronunciation))

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


# 筛选逻辑还未实现，现在默认是N级联动么？
# 不知道筛选出来了多少单词
# 不知道当前的学习进度是多少
# 开关选择展示单词的时候是否遮蔽单词含义
# 在页面上渲染当前单词的图谱，展示与该单词的所有依赖关系
# 页面逻辑简单一些，交互方式尽可能简单一些
# 能不能把发音规则总结出来，或者把当前单词的发音方式总结出来
# 根据出版社筛选单词后，是不是展示一张图片和用户确认要背的是不是这些单词？
