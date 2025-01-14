'''This is the driver code.
Streamlit framework serves as the app UI'''
import streamlit as st
import os
import io
from PIL import Image
from google.cloud.vision_v1 import types
from keywordExtractor import processAns, QuestionMatch, wordimportance
from google.cloud import vision_v1p3beta1 as vision

# add google vision token here
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'token.json'

client = vision.ImageAnnotatorClient() # Initialise a Google Cloud Vision Client


def modifyKeywords(keywords, model_answer):
    '''Implements adding or removing a keyword'''
    flag = True
    new_list = []
    item = st.multiselect(
        "Select keywords that you want to remove", keywords, key='69')
    word = st.text_input('Enter a keyword to insert')
    if(word not in model_answer):
        st.write("Invalid keyword, keyword must be present in the model answer")
    val = st.button("Make changes")


def getData():
    '''The main driver method to run the web-app. All required methods are called here.'''
    option = st.selectbox('', ('Select a Question', 'What is a Router?', 'What do you mean by Network?', 'What is the OSI model?',
                          "What are the different Layers of TCP/IP Model?", "What is the work of a Proxy server?", "What is a decoder?", "What is POP3?"))
    if (not (option == 'Select a Question')):
        new_list = []
        model_answer = QuestionMatch(option)
        st.subheader("Model answer")
        st.write(model_answer)

        keywords = list(wordimportance(QuestionMatch(option)).keys())
        st.subheader("Extracted keywords :-")
        st.write(keywords)
        item = st.multiselect(
            "Select keywords that you want to remove", keywords, key='69')
        words = st.text_input('Enter a keywords to insert', '')
        w = words.split(",")
        for word in w:
            if(word.lower() not in model_answer.lower()):
                st.write(
                    "Invalid keyword, keyword must be present in the model answer")
            elif (word != ''):
                st.write("Added keyword ➤ ", word)
                new_list.append(word.lower())
        if st.button("Make changes"):
            for keyword in keywords:
                if (keyword not in item):
                    new_list.append(keyword)
            keywords = new_list
            st.write("Updated list :-")
            st.write(keywords)

        '''Modify g_fac for grammar and s_fac for strength. 
        Provides a choice slider for the human evaluator to set importance of grammar and keyword strength.
        Default weightages for both are 50%, i.e., equal weightage is given to both of them.'''
        g_fac = st.slider("Choose grammar factor", 0, 100, value=50)
        s_fac = st.slider(
            "Choose strength vs presence factor (0→presence 1→strength)", 0, 100, value=(50))

        st.sidebar.write("# Menu")
        img_file = st.sidebar.file_uploader(
            label='', type=['png', 'jpg'], help="upload image to be evaluated")
        if img_file:
            img = Image.open(img_file)
            st.subheader("Student Answer")
            st.image(img)
            save_uploaded_file(img_file)
            FILE_PATH = "images/" + img_file.name
            with io.open(FILE_PATH, 'rb') as image_file:
                content = image_file.read()
            image = vision.Image(content=content)
            image_context = vision.ImageContext(
                language_hints=['en-t-i0-handwrit'])
            response = client.document_text_detection(
                image=image, image_context=image_context)
            docText = response.full_text_annotation.text
            st.write(docText)
            g_fac /= 100
            s_fac /= 100
            score = processAns(option, docText, keywords, g_fac, s_fac)
            if (score < 0):
                score = 0   #Fix for negative score

            st.write("Student score ->", score)
        else:
            st.subheader("Upload Student Answer")


def save_uploaded_file(uploadedfile):
    '''Saves the selected image in Present working directory for google API processing'''
    with open(os.path.join("./images/", uploadedfile.name), "wb") as f:
        f.write(uploadedfile.getbuffer())
    return st.success("Selected image {}".format(uploadedfile.name))

st.title("Student Answer Evaluator") #Sets the title of the streamlit app
getData()
