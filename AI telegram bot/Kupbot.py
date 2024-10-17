from aiogram import Bot, Dispatcher, html
import logging
import sys
import io
import random
import string # to process standard python strings
import warnings
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings('ignore')
import nltk
from nltk.stem import WordNetLemmatizer
import telebot
nltk.download('popular', quiet=True) # for downloading packages


#nltk.download('punkt') # first-time use only
#nltk.download('wordnet') # first-time use only

bot = telebot.TeleBot('') # here your api-code # Kupbot named like @@kuper_delivery_bot





@bot.message_handler(commands=['start'])
def start_message(message):
	bot.send_message(message.chat.id,"Добрый день! Я рад,что вы обратились ко мне! Я создан для ответа на часто задаваемые вопросы по поводу доставки Купер. Могу ответить на вопросы по поводу как работает Купер,куда доставляем,как сделать заказ,могут ли заказать юр.лица,про наличие продуктов,про оплату,про перенос и отмену заказа,что с вашим заказом,как узнать где ваш заказ,о возврате,так же могу дать контакты. Подробнее можно узнать на сайте :https://kuper.ru/sp/faq-kuper  \
     \
     ")

with open('chatbot.txt','r', encoding='utf8', errors ='ignore') as fin:
    raw = fin.read().lower()

sent_tokens = nltk.sent_tokenize(raw)
word_tokens = nltk.word_tokenize(raw)

lemmer = WordNetLemmatizer()

GREETING_INPUTS = ("привет", "добрый день", "здравствуй", "здравствуйте", "хэй","доброго времени суток",)
GREETING_RESPONSES = ["привет!", "добрый день!", "*звуки приветствия робота*", "здравствуйте!", "хэй!", "Мне приятно,что вы ко мне обратились","приветствую тебя!"]

def LemTokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]
remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)

def LemNormalize(text):
    return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))


def greeting(sentence):
    """If user's input is a greeting, return a greeting response"""
    for word in sentence.split():
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)


def response(user_response):
    robo_response=''
    sent_tokens.append(user_response)
    TfidfVec = TfidfVectorizer(tokenizer=LemNormalize, stop_words='english')
    tfidf = TfidfVec.fit_transform(sent_tokens)
    vals = cosine_similarity(tfidf[-1], tfidf)
    idx=vals.argsort()[0][-2]
    flat = vals.flatten()
    flat.sort()
    req_tfidf = flat[-2]
    if(req_tfidf==0):
        robo_response=robo_response+"Мне жаль, я тебя не понимаю"
        return robo_response
    else:
        robo_response = robo_response+sent_tokens[idx]
        return robo_response
   




@bot.message_handler(content_types=['text']) 
def start_message(message):
    user_response = message.text.lower()
    if(user_response!='Пока'):
        if(user_response=='спасибо' or user_response=='спасибо большое' or user_response=='благодарю' ):
            bot.send_message(message.chat.id,"Kupbot: You are welcome..")
        else:
            if(greeting(user_response)!=None):
                bot.send_message(message.chat.id,"Kupbot: "+greeting(user_response))
            else:
                bot.send_message(message.chat.id,response(user_response))
                sent_tokens.remove(user_response)
    else:
        bot.send_message(message.chat.id,"Kupbot: Bye! take care..")




  
    
    
bot.polling(none_stop=True)
    
