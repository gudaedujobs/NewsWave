import streamlit as st
from PIL import Image
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
from newspaper import Article
import io
import nltk
from googletrans import Translator

nltk.download('punkt')

# -*- coding: utf-8 -*-

st.set_page_config(page_title='NewsWave: News📰 Portal', page_icon='./Meta/newspaper.ico')
sup_lang_val = {"English": 'en', "Hindi": "hi", "Gujarati": 'gu', "Marathi": 'mr', "Kannada": "kn",
                "Tamil": 'ta', "Telugu": 'te'}
sup_lang_key = {v: k for k, v in sup_lang_val.items()}


def fetch_news_search_topic(topic):
    site = 'https://news.google.com/rss/search?q={}'.format(topic)
    op = urlopen(site)  # Open that site
    rd = op.read()  # read data from site
    op.close()  # close the object
    sp_page = soup(rd, 'xml')  # scrapping data from site
    news_list = sp_page.find_all('item')  # finding news
    return news_list


def header(url):
    st.markdown(f'<p style="color:#1de9aa;font-weight:bold;font-size:19px;">{url}</p>',
                unsafe_allow_html=True)


def lang_header(url):
    st.markdown(
        f'<p style="color:#ffffff;font-weight:bold;text-align:center;font-size:15px;background-color:#fc235a;padding-top:1px;padding-bottom:1px">{url}</p>',
        unsafe_allow_html=True)


def fetch_top_news():
    site = 'https://news.google.com/news/rss'
    op = urlopen(site)  # Open that site
    rd = op.read()  # read data from site
    op.close()  # close the object
    sp_page = soup(rd, 'xml')  # scrapping data from site
    news_list = sp_page.find_all('item')  # finding news
    return news_list


def fetch_category_news(topic):
    site = 'https://news.google.com/news/rss/headlines/section/topic/{}'.format(topic)
    op = urlopen(site)  # Open that site
    rd = op.read()  # read data from site
    op.close()  # close the object
    sp_page = soup(rd, 'xml')  # scrapping data from site
    news_list = sp_page.find_all('item')  # finding news
    return news_list


def fetch_news_poster(poster_link):
    try:
        u = urlopen(poster_link)
        raw_data = u.read()
        image = Image.open(io.BytesIO(raw_data))
        st.image(image, use_column_width=True)
    except:
        image = Image.open('./Meta/no_image.jpg')
        st.image(image, use_column_width=False)


def display_news(list_of_news, news_quantity, language):
    try:
        c = 0
        translator = Translator()
        for news in list_of_news:
            c += 1
            # st.markdown(f"({c})[ {news.title.text}]({news.link.text})")
            # st.write('**({}) {}**'.format(c, news.title.text))

            news_data = Article(news.link.text)
            try:
                news_data.download()
                news_data.parse()
                news_data.nlp()
            except Exception as e:
                st.error(e)
            if language != 'en':
                news_title = news.title.text
                news_title_tr = translator.translate(news_title, dest=language)
                header('({}) {}'.format(c, news_title_tr.text))
                fetch_news_poster(news_data.top_image)
                with st.expander(news_title_tr.text):
                    news_summ = news_data.summary
                    if news_summ:
                        news_summ_tr = translator.translate(str(news_summ), dest=language)
                        st.markdown(
                            '''<p style='text-align: justify;'>{}"</p>'''.format(news_summ_tr.text),
                            unsafe_allow_html=True)
                        st.markdown("[Read more at {}...]({})".format(news.source.text, news.link.text))
                    else:
                        st.warning("Didn't found anything......")
                st.success("Published Date: " + news.pubDate.text)
                if c >= news_quantity:
                    break
            else:
                news_title = news.title.text
                header('({}) {}'.format(c, news_title))
                fetch_news_poster(news_data.top_image)
                with st.expander(news_title):
                    news_summ = news_data.summary
                    st.markdown(
                        '''<p style='text-align: justify;'>{}"</p>'''.format(news_summ),
                        unsafe_allow_html=True)
                    st.markdown("[Read more at {}...]({})".format(news.source.text, news.link.text))
                st.success("Published Date: " + news.pubDate.text)
                if c >= news_quantity:
                    break

    except Exception as e:
        print(e)
        st.warning("Something went wrong with scraper, please try again...")


def run():
    st.title("NewsWave: A News📰 in your Language")
    image = Image.open('./Meta/newspaper.png')
    # Setup Image
    col1, col2, col3 = st.columns([3, 5, 3])
    with col1:
        st.write("")

    with col2:
        st.image(image, use_column_width=False)

    with col3:
        st.write("")
    # Language Selection
    supp_lang = ['English', 'Hindi', 'Gujarati', 'Marathi', 'Kannada', 'Tamil','Telugu']
    chosen_language = st.radio(
        "Preferred Language",
        supp_lang, horizontal=True)
    language_code = sup_lang_val[chosen_language]
    lang_header("Selected Language is: " + chosen_language)

    category = ['--Select--', 'Trending🔥 News', 'Favourite💙 Topics', 'Search🔍 Topic']
    cat_op = st.selectbox('Select your Category', category)
    if cat_op == category[0]:
        st.warning('Please select Type!!')
    elif cat_op == category[1]:
        st.subheader("✅ Here is the Trending🔥 news for you")
        no_of_news = st.slider('Number of News:', min_value=5, max_value=25, step=1)
        news_list = fetch_top_news()
        display_news(news_list, no_of_news, language_code)
    elif cat_op == category[2]:
        av_topics = ['Choose Topic', 'WORLD', 'NATION', 'BUSINESS', 'TECHNOLOGY', 'ENTERTAINMENT', 'SPORTS',
                     'SCIENCE',
                     'HEALTH']
        st.subheader("Choose your favourite Topic")
        chosen_topic = st.selectbox("Choose your favourite Topic", av_topics)
        if chosen_topic == av_topics[0]:
            st.warning("Please Choose the Topic")
        else:
            no_of_news = st.slider('Number of News:', min_value=5, max_value=25, step=1)
            news_list = fetch_category_news(chosen_topic)
            if news_list:
                st.subheader("✅ Here are the some {} News for you".format(chosen_topic))
                display_news(news_list, no_of_news, language_code)
            else:
                st.error("No News found for {}".format(chosen_topic))

    elif cat_op == category[3]:
        user_topic = st.text_input("Enter your Topic🔍")
        no_of_news = st.slider('Number of News:', min_value=5, max_value=15, step=1)

        if st.button("Search") and user_topic != '':
            user_topic_pr = user_topic.replace(' ', '')
            news_list = fetch_news_search_topic(topic=user_topic_pr)
            if news_list:
                st.subheader("✅ Here are the some {} News for you".format(user_topic.capitalize()))
                display_news(news_list, no_of_news, language_code)
            else:
                st.error("No News found for {}".format(user_topic))
        else:
            st.warning("Please write Topic Name to Search🔍")


run()
