import telebot
import re
from collections import defaultdict
from supabase import create_client
import sys
from dotenv import load_dotenv
import os

load_dotenv()

API_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = telebot.TeleBot(API_TOKEN)

# ms = defaultdict(list)


url_s = os.getenv("URL_SUPA")
key_s = os.getenv("KEY_SUPA")

try:
    supabase = create_client(url_s, key_s)
except:
    print("Erro ao conectar ao banco de dados")
    sys.exit(1)

# TODO: Adicionar coisas de tratamento de erro
def addLink(user, link):
    supabase.table("links").insert({"url": link, "user_id": user}).execute()

def getLinks(user):
    r = supabase.table("links").select("*").eq("user_id", user).execute()
    # exclui 
    supabase.table("links").delete().eq("user_id", user).execute()
    return r.data

@bot.message_handler(commands=['ola', 'start'])
def send_welcome(message):
    bot.reply_to(message, "Mande links que serão guardados e use o comanod /links ou /l para retornar todos eles(serão apagados de onde foram guardados)")


@bot.message_handler(commands=['links', 'l'])
def a(m):
    r = getLinks(m.chat.id)
    if len(r) == 0:
        bot.send_message(m.chat.id, "Sem links guardados")
    else:
        for i in r:
            bot.send_message(m.chat.id, i["url"])

link_r = 'https?:\/\/[^\s/$.?#].[^\s]*'
@bot.message_handler(func=lambda m: True)
def link_add(m):
    if re.search(link_r, m.text):
        addLink(m.chat.id, m.text)
        bot.reply_to(m, "Link adicionado")
    else:
        bot.reply_to(m, "Não foi reconhecido como um link")

bot.infinity_polling()
