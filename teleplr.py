import telebot
import telebot.types
from config import TELETOEKN as il
import os
import re
import time
from sclib.sync import SoundcloudAPI, Track, Playlist
bot = telebot.TeleBot(il)

api = SoundcloudAPI()  

data = []
busychats = []

commandslist = "\n\n-start\n-playmusic <имя автора латинскими буквами, без пробелов> <название песни только латинскими>\n-playplaylist\n-savetrack <имя автора латинскими буквами, без пробелов> <название песни только латинскими>\n-showplaylist\n-help"

def clrfromlist(id):
    if id in busychats:
        busychats.pop(busychats.index(id))

def toname(mesg):
    """конвертирует текстовую информацию (о исполнителе и песне) в валидный формат"""
    try:
        txet = ""
        txtfr = mesg
        txtfr = re.sub(r'[^a-zA-Z0-9\s]', ' ', txtfr)
        a = txtfr.lower().split()
        autho = a[0]
        for i in range(len(a)):
            if i > 0:
                txet+=str(a[i])
                if i < len(a)-1:
                    txet+=" "
        txet = re.sub(r'[^a-zA-Z0-9\s]', ' ', txet)
        txet = txet.replace(' ', '-')

        return [autho,txet]
    except:
        return False

def checktrackexist(mesg):
    """проверяет существование трэка на серверах soundcloud"""
    try:
        autho = ""
        txet = ""
        chec = toname(mesg)
        if chec != False:
            autho = chec[0]
            txet = chec[1]
        else:
            return False
        print(f"{autho} {txet}")
        track = api.resolve(f'https://soundcloud.com/{autho}/{txet}')
        return track
    except:
        return False

def createtrack(mesg,id):
    """скачивает новый трэк, скидывает и затем удаляет"""
    busychats.append(id.from_user.id)
    try:
        track = checktrackexist(mesg)
        
        assert type(track) is Track

        bot.send_message(id.chat.id,f'Скидываю: {track.label_name}\nАвтор: {track.artist}')
        filename = fr'temp\music.mp3'
        with open(filename, 'wb+') as file:
            track.write_mp3_to(file)
        with open(filename, 'rb') as file:
            bot.send_voice(id.chat.id, file)

        os.remove(filename)
        clrfromlist(id.from_user.id)
    except Exception as err:
        print(err)
        clrfromlist(id.from_user.id)
        bot.send_message(id.chat.id,'не найдено')

def writedata(name,data:list):
    """вписывает новую информацию в userdata.txt пользователя, если папка или файл не существуют - создаёт то, чего не хватает."""
    tostrname = ""
    for i in range(len(data)):
        if i!= len(data)-1:
            tostrname+=f"{data[i]} "
        else:
            tostrname+=f"{data[i]}"

    if checktrackexist(tostrname) == False:
        return
    print("passed")
    dest = checkfold(name)
    with open(fr"{dest}\userdata.txt","r",encoding="utf-8") as file:
        found=False
        tup = file.read().split()
        for i in range(len(tup)):
            if i%2==0:
                if tup[i]==data[0] and tup[i+1] ==data[1]:
                    found = True
                    break
        if not found:
            with open(fr"{dest}\userdata.txt","a",encoding="utf-8") as file:
                for i in data:
                    file.write(f"{i} ")

def checkfold(name):
    """проверка существования папки, если нет то создать. Возвращает местоположение файла"""
    a = fr"savedtracks\\{name}"
    if not os.path.exists(a):
        os.makedirs(a)
    while not os.path.exists(a):
        time.sleep(0.1)
    return a

#приветствие-----------------------------------------------------------------------------------------

@bot.message_handler(commands=['start'])
def handle_start_help(message):
    bot.reply_to(message,'Здравствуй. Это teleplayer бот!! Этот бот сохраняет песни и хранит их на компе либо в колледже либо у меня дома. Напиши /help для списка команд \nПоделитесь своей любимой песней прям в чате!!\n(создан для дз)')
    #playmusic (/playmusic <имя автора ЛАТИНСКИМИ буквами, без пробелов> <название песни (тоже латинскими)>).\nplayplaylist (/playmusic <имя автора ЛАТИНСКИМИ буквами, без пробелов> <название плейлиста (тоже латинскими)>)\n

@bot.message_handler(commands=['help'])
def handle_start_help(message):
    bot.send_message(message.chat.id,f"Список команд: {commandslist}")

#проигрывание----------------------------------------------------------------------------------------

@bot.message_handler(commands=['playmusic'])
def handle_start_help(message):
    """играет музыку"""
    if message.from_user.id not in busychats:
        createtrack(f"{message.text.split()[1]} {message.text.split()[2]}",message)
    else:
        bot.send_message(message.chat.id,f'Занят!!')

@bot.message_handler(commands=['playplaylist'])
def handle_start_help(message):
    """играет музыку с плейлиста пользователя, ту песню, которую он выбрал цифрой после команды"""
    if message.from_user.id not in busychats:
        textspl = message.text.split()
        if len(message.text.split()) < 2:
            bot.send_message(message.chat.id,f'неправильно?')
            return
        datadest = fr"{checkfold(message.from_user.id)}\\userdata.txt"
        if os.path.exists(datadest):
            with open(datadest,"r") as file:
                listreade = file.read().split()
                for i in range(len(listreade)):
                    if i == int(textspl[1]) and i%2==0:
                        bot.send_message(message.chat.id,f'скидываю?')
                        createtrack(f"{listreade[i]} {listreade[i+1]}",message)
        else:
            bot.send_message(message.chat.id,f'Плейлиста не существует')
    else:
        bot.send_message(message.chat.id,f'Занят!!')

#сохранение------------------------------------------------------------------------------------------

@bot.message_handler(commands=['savetrack'])
def handle_start_help(message):
    if message.from_user.id not in busychats:
        writedata(message.from_user.id,toname(f"{message.text.split()[1]} {message.text.split()[2]}"))
    else:
        bot.send_message(message.chat.id,f'Занят!!')

#т.д.-------------------------------------------------------------------------------------------------

@bot.message_handler(commands=['showplaylist'])
def handle_start_help(message):
    if message.from_user.id not in busychats:
        if os.path.exists(fr"{checkfold(message.from_user.id)}\userdata.txt"):
            listofmusics="Список ваших песен\n"
            with open(fr"{checkfold(message.from_user.id)}\userdata.txt","r",encoding="utf-8") as file:
                ls = file.read().split()
                for x in range(len(ls)):
                    if x%2==0:
                        listofmusics+=f"{x}:{ls[x]} "
                        listofmusics+=f"{ls[x+1]}\n"
            bot.send_message(message.chat.id,listofmusics)
        else:
            bot.send_message(message.chat.id,f'Плейлиста не существует')
    else:
        bot.send_message(message.chat.id,f'Занят!!')

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "savetrack":
            bot.send_message(call.message.chat.id, "ббббред")
    elif call.data == "onblack":
            bot.send_message(call.message.chat.id, "бббб")

@bot.message_handler(func=lambda call: True)
def send_welcome(call):
    bot.send_message(call.chat.id,f"''{call.text}'' :skull: :skull: :nerd_emoji:")

bot.infinity_polling()