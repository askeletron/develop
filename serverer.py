import socket
import time
import threading
import sys
import os
import re
import tkinter as tk

#server
#полностью сделано askeletron

#словарь значений
opts={
    "ip": "",
    "port": 14888,
    "countauth": 0,

    "adresses": [],
    "connected_clients": [],
    "banned": [],
    
    "showtext": "",

    "ignore": False,
    "isstarted": False,

    "ln": lambda: threading.Thread(target=serverapp.server.serverf, daemon=True).start()
}

class serverapp:
    """сервер со своим визуальным окном и основными функциями"""
    
    def serverf():
        """главная функция сервера"""

        #проверка валидности IP адреса
        if opts["ip"] == "":
            try:
                opts["ip"] = socket.gethostbyname_ex(socket.gethostname())[2][1]
            except:
                opts["ip"] = socket.gethostname(socket.gethostname())
                opts["showtext"] = f"Ошибка, IP адрес изменён на {opts["ip"]}"

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ss:
            ss.bind((opts["ip"],opts["port"]))
            print("Host ip:",opts["ip"],"\n")

            def bancl(clientadr,txtt):
                """добавление клиента в список забаненных"""

                opts["banned"].append(clientadr[0])
                print(f"бан клиента: {clientadr}, {txtt}")
                opts["showtext"] = f"Клиент забанен - {txtt}: {clientadr}"

            def handle_client(client_socket, client_address):
                """функция для содержания индвидиуального клиента (запуск с трэда)"""

                print(f"accepted connection from {client_address}")
                
                opts["showtext"] = f"Новый клиент подключен: {str(client_address)}"

                #проверка если клиента уже не существует не сервере
                if not client_address[0] in opts["adresses"]:
                    opts["adresses"].append(client_address[0]); opts["adresses"].append(0); opts["adresses"].append(False)
                else: client_socket.close()
                # =================================================

                opts["connected_clients"].append(client_socket) if not client_socket in opts["connected_clients"] else None
                try:
                    while True:
                        data = client_socket.recv(1024)
                        print(f"debug: {data}")

                        # проверка траффика и бан, если траффик слишком велик
                        if opts["adresses"][opts["adresses"].index(client_address[0])+1] > 1000 or sys.getsizeof(data) > 500:
                            bancl(client_address[0], "подозрение DoS атаки")
                            break
                        opts["adresses"][opts["adresses"].index(client_address[0])+1]+=sys.getsizeof(data) #добавление траффика клиенту
                        #========================================================

                        datafilt = data.decode("utf-8")

                        if opts["adresses"][opts["adresses"].index(client_address[0])+2] == False:
                            # проверка если клиент не зарегестрирован и, если так, ожидание пароля
                            if datafilt == "12345":
                                print('nice')
                                opts["countauth"] +=1
                                opts["adresses"][opts["adresses"].index(client_address[0])+2] = True
                            else:
                                # применение суровых условий при вводе неправильного пароля (бан)
                                print('wrong')
                                bancl(client_address[0], "неправильный пароль")
                                break
                        else:
                            if not data:
                                #если информации нет (что означает отключение клиента), то выйти из цикла (стереть клиента с сервера)
                                break
                except Exception as e:
                    if opts["ignore"] == False:
                        print(f"ошибка содержания клиента: {str(e)}")
                        opts["showtext"] = f"Ошибка содержания клиента: {str(e)}"
                finally:
                    # -- завершение подключения с клиентом (очистка его из списков)
                    if not client_address[0] in opts["banned"] and client_address[0] in opts["adresses"]:
                        opts["showtext"] = f"Клиент отключен: {client_address}"
                    try:
                        if client_socket in opts["connected_clients"]:
                            opts["connected_clients"].pop(opts["connected_clients"].index(client_socket))
                        if client_address[0] in opts["adresses"]:
                            if opts["adresses"][opts["adresses"].index(client_address[0])+2] == True:
                                opts["countauth"]-=1
                            for i in range(2,-1,-1):
                                print(i)
                                opts["adresses"].pop(opts["adresses"].index(client_address[0])+i)
                    except Exception as err:
                        if opts["ignore"] == False:
                            print(f"err lists {str(err)}")
                            opts["showtext"] = f"Ошибка списков: {str(err)}"
                    
                    print(f"client {client_address} disconnected.")
                    client_socket.close()
            try:
                while True:
                    ss.listen()
                    conn, addr = ss.accept()
                    if addr[0] in opts["banned"]:
                        opts["showtext"] = f"Попытка подключения заБАНенного {addr}" if opts["ignore"] == False else None
                        conn.close()
                    else:
                        client_handler = threading.Thread(target=handle_client, args=(conn, addr))
                        client_handler.daemon = True
                        client_handler.start()
            except Exception as e:
                if opts["ignore"] == False:
                    print(f"ошибка подключения клиента: {str(e)}")
                    opts["showtext"] = f"Ошибка подключения клиента: {str(e)}"


    def sendmsg(msg:str):
        """отправка сообщения на все клиенты"""
        if len(opts["connected_clients"]) > 0:
            for i in opts["connected_clients"]:
                i.send(str(msg).encode("utf-8"))
    def closeall():
        """закрытие всех подключенных портов"""
        if len(opts["connected_clients"]) > 0:
            for i in opts["connected_clients"]:
                i.close()

    def appcreate():
        def mainlooptk():
            """обновление значений в окне"""

            saved_showText="" #------- последнее сохранённое значение текста (активирование при изменении)
            saved_AuthCount = 0 #----- последнее сохранённое число кол-ва зарегестрированных (активирование при изменении)
            saved_ConnCount=0 #------- последнее сохранённое число кол-ва присоединённых клиентов (активирование при изменении)

            list_cmd=[] #------------- список строк (label-ов) в отображаемой коммандной строке

            while True:
                #основное обновление значений (в цикле для постоянного обновления)
                if saved_showText != opts["showtext"]:
                    #добавление новых строк в коммандной строке
                    saved_showText = opts["showtext"]
                    
                    lbll = tk.Label(cmd,text=opts["showtext"], wraplength=400, justify=tk.LEFT)
                    lbll.pack(anchor="nw")
                    if len(list_cmd) > 3:
                        list_cmd[0].destroy()
                        list_cmd.pop(0)
                    list_cmd.append(lbll)

                if saved_AuthCount != opts["countauth"]:
                    saved_AuthCount = opts["countauth"]
                    auth_info.config(text=f"кол-во зарег. клиентов: {opts["countauth"]}")

                if saved_ConnCount != len(opts["connected_clients"]):
                    saved_ConnCount = len(opts["connected_clients"])
                    connclients_info.config(text=f"кол-во всего клиентов: {len(opts["connected_clients"])}")

                time.sleep(0.1)
        def cmds():
            """выполняемые комманды и их функции"""
            mesg = text_var.get().split()
            match mesg:
                case "clients", *wtv:
                    opts["showtext"] = str(opts["adresses"])
                case "conns", *wtv:
                    opts["showtext"] = str(opts["connected_clients"])
                case "banned", *wtv:
                    opts["showtext"] = str(opts["banned"])
                case "unban", wtv:
                    opts["banned"].pop(wtv)
                    opts["showtext"] = f"разбанен {opts["banned"][wtv]}"
                case "ignore", wtv:
                    try:
                        if bool(wtv):
                            ign = bool(wtv)
                            opts["showtext"] = f"теперь игнорируются ошибки и заходы забаненных: {ign}"
                    except: None
                case "ban", wtv:
                    opts["showtext"] = f"забанен {wtv}"
                    opts["banned"].append(wtv)
                case "unbanall", *wtv:
                    opts["showtext"] = "разбанены все"
                    opts["banned"].clear()
                case "ip", wtv:
                    if opts["isstarted"] == False:
                        opts["showtext"] = f"{opts["ip"]} > {wtv}"
                        opts["ip"] = wtv
                    else:
                        opts["showtext"] = "Невозможно поменять конфиг - сервер запущен."

                case "portch", wtv:
                    if opts["isstarted"] == False and int(wtv) <= 65535:
                        try:
                            if int(wtv):
                                opts["showtext"] = f"{opts["port"]} > {wtv}"
                                opts["port"] = int(wtv)
                        except:
                            opts["showtext"] = "Ошибка, порт должен быть INT"
                    else:
                        opts["showtext"] = "Невозможно поменять конфиг - сервер уже запущен."
                case "start", *wtv:
                    if opts["isstarted"] == False:
                        threading.Thread(target=serverapp.serverf,daemon=True).start()
                        while time.sleep(0.1): 
                            if opts["ip"]!="":
                                break 
                        main_info.config(text=f"IP адрес - {opts["ip"]} слушание начато")
                        opts["showtext"] = "Сервер запущен."
                        opts["isstarted"] = True
                    else:
                        opts["showtext"] = "Сервер уже запущен."
                case _:
                    opts["showtext"] = "Неизвестная комманда"

        # === основное окно------

        root = tk.Tk()
        root.resizable(False,False)
        root.title("server")
        root.geometry("400x290")


        # === списки и рамки(Frame)------

        mainfr = tk.Frame(root,borderwidth=3, relief=tk.SUNKEN)
        mainfr.pack(anchor=tk.CENTER)
        cmd = tk.Frame(root,borderwidth=3, relief=tk.SUNKEN, width=400, height=100)
        cmd.pack(anchor=tk.CENTER)
        cmd.pack_propagate(False)


        # === ввод------

        text_var = tk.StringVar()
        vvod=tk.Entry(root,width=200,textvariable=text_var)
        vvod.pack(anchor=tk.CENTER)

        text_var.set("напишите ip для конфига IP адреса. start - запустить сервер с текущим конфигом.")


        # === лабелы-------

        main_info = tk.Label(mainfr,text=f"Сервер выключен. Ожидание конфигурации.")
        main_info.pack(anchor=tk.CENTER,padx=1, pady=1)

        auth_info = tk.Label(mainfr,text=f"кол-во зарег. клиентов: {opts["countauth"]}")
        auth_info.pack(anchor=tk.CENTER,padx=1, pady=1)

        connclients_info = tk.Label(mainfr,text=f"кол-во всего клиентов: {len(opts["connected_clients"])}")
        connclients_info.pack(anchor=tk.CENTER,padx=1, pady=1)


        # === кнопкы-------

        closconns = tk.Button(mainfr, text="закрыть все соединения", command=serverapp.closeall)
        closconns.pack(anchor=tk.CENTER,padx=1, pady=1)
        closconns = tk.Button(root, text="Ввод", command=cmds)
        closconns.pack(anchor=tk.NW,padx=1, pady=1)

        #тред обновления окна
        threading.Thread(target=mainlooptk,daemon = True).start()
        
        root.mainloop()
        print("closed")
newapp = serverapp.appcreate()