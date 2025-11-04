import telebot
import telebot.types
import telebot.types
from config import TELETOEKN as il
import os
import re
import time
from sclib.sync import SoundcloudAPI, Track
#название библиотеки по каким-то причинам отличается, может использоваться SClib, или, как в моём случае, sclib.sync

bot = telebot.TeleBot(il)

api = SoundcloudAPI()  

data = {} #  хранение информации о пользователе (сохраняет текущую позицию пользователя в плейлисте)
busychats = [] #  список занятых пользователей

#СПИСОК КОМАНД
commandslist = "\n\n-start\n-playmusic <имя автора латинскими буквами, без пробелов> <название песни только латинскими>\n-nextsong (играет следующую песню в вашем плейлисте)\n-savetrack <имя автора латинскими буквами, без пробелов> <название песни только латинскими>\n-showplaylist\n-help"

def clrfromlist(id):
    """убирает с списка занятых чатов указанный чат"""
    #id = ID ПОЛЬЗОВАТЕЛЯ
    if id in busychats:
        busychats.pop(busychats.index(id))

def toname(mesg):
    """конвертирует текстовую информацию (о исполнителе и песне) в валидный формат"""
    try:
        txet = ""
        txtfr = mesg
        minSTART = 0 # ОБОЗНАЧЕНИЕ НАЧАЛА В ЗАДАННОМ СПЛИТОВАННОМ ТЕКСТЕ (Т.К. ДАННАЯ ФУНКЦИЯ ПРИНИМАЕТ ИЗНАЧАЛЬНО СООБЩЕНИЕ TELEBOT-A,
                     # А ЗНАЧИТ ВМЕСТЕ С ТЕКСТОМ ПРИХОДИТ И ТЕКСТ ФУНКЦИИ (ПРИМЕР: /playmusic A B -> playmusic A B), ДАННАЯ ПЕРЕМЕННАЯ
                     # ФИЛЬТРУЕТ ТЕКСТ ФУНКЦИИ (В СЛУЧАЕ ПРИМЕРА - playmusic) ЧТОБЫ НЕ ВКЛЮЧАТЬ ЕГО В ФИЛЬТРОВАННЫЙ ТЕКСТ,
                     # НО БЫВАЮТ СЛУЧАИ КОГДА ВМЕСТО СООБЩЕНИЯ ОТПРАВЛЯЕТСЯ СРАЗУ ЖЕ ТЕКСТ, ЭТО АДАПТАЦИЯ К ПРИНИМАНИЮ И ТЕКСТА И СООБЩЕНИЯ)
        if isinstance(mesg,telebot.types.Message):
            minSTART = 1
            txtfr = mesg.text 
        splittedExtText = re.sub(r'[^a-zA-Z0-9\-\s]', ' ', txtfr).lower().split()
        for i in range(len(splittedExtText)):
            if i > minSTART:
                txet+=str(splittedExtText[i])
                if i < len(splittedExtText)-1:
                    txet+=" "
        return [splittedExtText[minSTART],txet.replace(' ', '-')] # формат -> <author> <track name>
    except Exception as ERR:
        print(f"ошибка toname: {ERR}")
        # RETURN FALSE ЧТОБЫ ОБОЗНАЧИТЬ, ЧТО ЗАДАННЫЙ ФОРМАТ НЕПРАВИЛЬНЫЙ!!!!!!!!!!!!!!!
        return False

def checktrackexist(mesg):
    """проверяет существование трэка на серверах soundcloud и возваращает трек, иначе False"""
    try:
        chec = toname(mesg)
        return api.resolve(f'https://soundcloud.com/{chec[0]}/{chec[1]}') if chec else False  # формат -> <track>
    except Exception as ERR:
        print(f"ошибка ChTRACKEx: {ERR}")
        # RETURN FALSE ЧТОБЫ ОБОЗНАЧИТЬ, ЧТО ЗАДАННАЯ МУЗЫКА НЕ НАЙДЕНА!!!!!!!!!!!!!!!
        return False

def createtrack(mesg,id):
    """скачивает новый трэк, скидывает и затем удаляет"""
    busychats.append(id.from_user.id)
    try:
        track = checktrackexist(mesg) #проверка существования песни
        assert type(track) is Track
        bot.reply_to(id,f'Загружаю: {track.title}\nАвтор: {track.artist}')
        filename = fr'temp\music.mp3' #МЕСТОПОЛОЖЕНИЕ ПЕСНИ
        with open(filename, 'wb+') as file:
            track.write_mp3_to(file)
            bot.send_voice(id.chat.id, file)
        os.remove(filename)
        clrfromlist(id.from_user.id)
    except Exception as err:
        print(f"error CrTRACK {err}")
        clrfromlist(id.from_user.id)
        bot.reply_to(id,f"не удалось; {"превышено время ожидания" if type(err) == TimeoutError else str(err)}")

def writedata(mesg):
    """вписывает новую информацию в userdata.txt пользователя, если папка или файл не существуют - создаёт то, чего не хватает."""
    if not checktrackexist(mesg):
        return 
    print("passed")
    filt = toname(mesg) #фильтрация заданного функции имени mesg через toname 
    dest = checkfold(mesg.from_user.id) #местонахождение папки
    if not os.path.exists(fr"{dest}\userdata.txt"):
        #проверка существования txt файла сохранения, если нет то создать
        with open(fr"{dest}\userdata.txt","x"): pass
    with open(fr"{dest}\userdata.txt","r",encoding="utf-8") as file:
        found = False #найдена ли заданная песня в файле сохранения пользователя, если False то добавить
        extInf = file.read().split() #сплитованный прочитанный текст
        # ниже идёт проверка переменной found
        for i in range(len(extInf)):
            if i%2==0:
                if extInf[i]== filt[0] and extInf[i+1] ==filt[1]:
                    found = True
                    break
        if not found:
            with open(fr"{dest}\userdata.txt","a",encoding="utf-8") as file:
                for i in filt:
                    file.write(f"{i} ")
            bot.reply_to(mesg,'Успешно добавлено')
            

def checkfold(name):
    """проверка существования папки, если нет то создать. Обязательно возвращает местоположение файла"""
    dest = fr"savedtracks\\{name}" #местонахождение папки
    if not os.path.exists(dest):
        os.makedirs(dest)
    while not os.path.exists(dest): time.sleep(0.1)
    return dest

#приветствие-----------------------------------------------------------------------------------------

@bot.message_handler(commands=['start'])
def handle_start_help(message):
    bot.reply_to(message,'Здравствуй. Это teleplayer бот!! Этот бот сохраняет песни и хранит их на компе либо в колледже либо у меня дома.' \
    ' Напиши /help для списка команд \nПоделитесь своей любимой песней прям в чате!!\n(создан для дз)')

@bot.message_handler(commands=['help'])
def handle_start_help(message):
    bot.send_message(message.chat.id,f"Список команд: {commandslist}")

#проигрывание----------------------------------------------------------------------------------------

@bot.message_handler(commands=['playmusic'])
def handle_start_help(message):
    """скидывание заданной песни"""
    if message.from_user.id not in busychats: #провека занятости пользователя
        createtrack(message,message)
    else:
        bot.send_message(message.chat.id,f'Занят!!')

@bot.message_handler(commands=['nextsong'])
def handle_start_help(message):
    """играет следующую музыку с плейлиста пользователя"""
    if message.from_user.id not in busychats: #провека занятости пользователя
        datadest = fr"{checkfold(message.from_user.id)}\\userdata.txt" #местонахождение файла сохранения пользователя
        #проверка существования файла сохранения пользователя
        if os.path.exists(datadest):
            with open(datadest,"r") as file:
                extInf = file.read().split() #сплитованный прочитанный текст
                
                if not message.from_user.id in data: #больше информации в кэпшоне возле самого списка
                    data[message.from_user.id] = 0
                else:
                    # использование значений с файла сохранения пользователя (прибавляет 2, т.к. название песни находится на чётных местах)
                    if data[message.from_user.id] < len(extInf)//2: data[message.from_user.id] += 2
                    else: data[message.from_user.id] = 0
                print(data)
                for i in range(len(extInf)):
                    if i == data[message.from_user.id] and i%2==0:
                        bot.reply_to(message,'Скидываю')
                        createtrack(f"{extInf[i]} {extInf[i+1]}",message)
                        break
        else:
            bot.reply_to(message,'Плейлиста не существует')
    else:
        bot.send_message(message.chat.id,f'Занят!!')

#сохранение------------------------------------------------------------------------------------------

@bot.message_handler(commands=['savetrack'])
def handle_start_help(message):
    """сохранение трэка в файл пользователя (плейлист)"""
    if message.from_user.id not in busychats: #провека занятости пользователя
        writedata(message)
    else:
        bot.send_message(message.chat.id,f'Занят!!')

#т.д.-------------------------------------------------------------------------------------------------

@bot.message_handler(commands=['showplaylist'])
def handle_start_help(message):
    """отправляет плейлист пользователя"""
    if message.from_user.id not in busychats: #проверка занятости пользователя
        #проверка существования файла сохранения пользователя
        if os.path.exists(fr"{checkfold(message.from_user.id)}\userdata.txt"): 
            listofmusics="Список ваших песен\n"
            with open(fr"{checkfold(message.from_user.id)}\userdata.txt","r",encoding="utf-8") as file:
                #считывание и добавление в string авторов и названий песен
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