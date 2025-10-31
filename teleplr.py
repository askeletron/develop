import telebot
import telebot.types
from config import TELETOEKN as il
import os
import re
import time
from sclib.sync import SoundcloudAPI, Track, Playlist
bot = telebot.TeleBot(il)

api = SoundcloudAPI()  

data = {} #  хранение информации о пользователе (сохраняет текущую позицию пользователя в плейлисте)
busychats = [] #  список занятых чатов, 

commandslist = "\n\n-start\n-playmusic <имя автора латинскими буквами, без пробелов> <название песни только латинскими>\n-nextsong (играет следующую песню в вашем плейлисте)\n-savetrack <имя автора латинскими буквами, без пробелов> <название песни только латинскими>\n-showplaylist\n-help"

def clrfromlist(id):
    """убирает с списка занятых чатов указанный чат"""
    if id in busychats:
        busychats.pop(busychats.index(id))

def toname(mesg):
    """конвертирует текстовую информацию (о исполнителе и песне) в валидный формат"""
    try:
        txet = ""
        txtfr = mesg
        minind = 0
        if type(mesg) == telebot.types.Message:
            minind=1
            txtfr = mesg.text
        txtfr = re.sub(r'[^a-zA-Z0-9\-\s]', ' ', txtfr)
        a = txtfr.lower().split()
        autho = a[minind]
        for i in range(len(a)):
            if i > minind:
                txet+=str(a[i])
                if i < len(a)-1:
                    txet+=" "
        txet = txet.replace(' ', '-')

        return [autho,txet]
    except:
        return False

def checktrackexist(mesg):
    """проверяет существование трэка на серверах soundcloud и возваращает трек, иначе False"""
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

        bot.reply_to(id,f'Загружаю: {track.title}\nАвтор: {track.artist}')
        filename = fr'temp\music.mp3'
        with open(filename, 'wb+') as file:
            track.write_mp3_to(file)
            bot.send_voice(id.chat.id, file)
        
        os.remove(filename)
        clrfromlist(id.from_user.id)
    except Exception as err:
        print(err)
        clrfromlist(id.from_user.id)
        bot.reply_to(id,f"не удалось; {"превышено время ожидания" if type(err) == TimeoutError else str(err)}")

def writedata(mesg):
    """вписывает новую информацию в userdata.txt пользователя, если папка или файл не существуют - создаёт то, чего не хватает."""
    
    if checktrackexist(mesg) == False:
        return
    print("passed")
    filt = toname(mesg)
    dest = checkfold(mesg.from_user.id)
    if not os.path.exists(fr"{dest}\userdata.txt"):
        with open(fr"{dest}\userdata.txt","x"): pass
    with open(fr"{dest}\userdata.txt","r",encoding="utf-8") as file:
        found=False
        tup = file.read().split()
        for i in range(len(tup)):
            if i%2==0:
                if tup[i]== filt[0] and tup[i+1] ==filt[1]:
                    found = True
                    break
        if not found:
            with open(fr"{dest}\userdata.txt","a",encoding="utf-8") as file:
                for i in filt:
                    file.write(f"{i} ")
            bot.reply_to(mesg,'Успешно добавлено')
            

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

@bot.message_handler(commands=['help'])
def handle_start_help(message):
    bot.send_message(message.chat.id,f"Список команд: {commandslist}")

#проигрывание----------------------------------------------------------------------------------------

@bot.message_handler(commands=['playmusic'])
def handle_start_help(message):
    """играет музыку"""
    if message.from_user.id not in busychats:
        createtrack(message,message)
    else:
        bot.send_message(message.chat.id,f'Занят!!')

@bot.message_handler(commands=['nextsong'])
def handle_start_help(message):
    """играет следующую музыку с плейлиста пользователя"""
    if message.from_user.id not in busychats:

        datadest = fr"{checkfold(message.from_user.id)}\\userdata.txt"
        if os.path.exists(datadest):
            with open(datadest,"r") as file:
                listreade = file.read().split()
                
                if not message.from_user.id in data:   # создание информации о пользователе в словаре data
                    data[message.from_user.id] = 0
                else:
                    if data[message.from_user.id] < len(listreade)//2: data[message.from_user.id] += 2
                    else: data[message.from_user.id] = 0
                print(data)
                for i in range(len(listreade)):
                    if i == data[message.from_user.id] and i%2==0:
                        bot.reply_to(message,'Скидываю')
                        createtrack(f"{listreade[i]} {listreade[i+1]}",message)
        else:
            bot.reply_to(message,'Плейлиста не существует')
    else:
        bot.send_message(message.chat.id,f'Занят!!')

#сохранение------------------------------------------------------------------------------------------

@bot.message_handler(commands=['savetrack'])
def handle_start_help(message):
    """сохранение трэка в файл пользователя (плейлист)"""
    if message.from_user.id not in busychats:
        writedata(message)
    else:
        bot.send_message(message.chat.id,f'Занят!!')

#т.д.-------------------------------------------------------------------------------------------------

@bot.message_handler(commands=['showplaylist'])
def handle_start_help(message):
    """отправляет плейлист пользователя"""
    if message.from_user.id not in busychats:
        if os.path.exists(fr"{checkfold(message.from_user.id)}\userdata.txt"):
            listofmusics="Список ваших песен\n"
            with open(fr"{checkfold(message.from_user.id)}\userdata.txt","r",encoding="utf-8") as file:
                ls = file.read().split()
                for x in range(len(ls)):
                    if x%2==0:
                        listofmusics+=f"{ls[x]} "
                        listofmusics+=f"{ls[x+1]}\n"
            bot.send_message(message.chat.id,listofmusics)
        else:
            bot.send_message(message.chat.id,f'Плейлиста не существует')
    else:
        bot.send_message(message.chat.id,f'Занят!!')

# @bot.message_handler(func=lambda call: True)
# def send_welcome(call):
#     bot.send_message(call.chat.id,f"''{call.text}'' :skull: :skull: :nerd_emoji:")

bot.infinity_polling()