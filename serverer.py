import socket
import time
import threading
from tkinter import *
#server
connected_clients = []
adresses = []
ip = "192.168.0.73"
showtezt = ""
def serverf():
    """сервер запускать с трэда"""
    global ip
    global showtezt
    global adresses
    global newclient
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ss:
        ss.bind((ip,14888))
        print("Host ip:",ip,"\n")
        def handle_client(client_socket, client_address):
            global showtezt
            print(f"Accepted connection from {client_address}")
            showtezt = f"новый клиент подключен: {str(client_address)}"
            if not client_address in adresses:
                adresses.append(client_address)
            if not client_socket in connected_clients:
                connected_clients.append(client_socket)
            try:
                while True:
                    data = client_socket.recv(1024) # Receive data from the client
                    if not data:
                        break # Client disconnected
            except Exception as e:
                showtezt = f"ошибка содержания клиента: {str(e)}"
            finally:
                try:
                    if client_address in adresses:
                        adresses.pop(adresses.index(client_address))
                    if client_socket in connected_clients:
                        connected_clients.pop(adresses.index(client_socket))
                except: None
                showtezt = f"клиент отключен: {str(client_address)}"
                print(f"Client {client_address} disconnected.")
                client_socket.close()
        def newclients():
            global showtezt
            try:
                while True:
                    ss.listen()
                    conn, addr = ss.accept()
                    client_handler = threading.Thread(target=handle_client, args=(conn, addr))
                    client_handler.start() # Start a new thread for each client
            except Exception as e:
                showtezt = f"ошибка подключения клиента: {str(e)}"
        threading.Thread(target=newclients).start()
        while True:
            try:
                mesg = str(input(""))
                if mesg == "clients":
                    print(adresses)
                
            except: None
def sendmsg(msg:str):
    """отправка сообщения на все клиенты"""
    if connected_clients:
        for i in connected_clients:
            i.send(str(msg).encode("utf-8"))
def closeall():
    """закрытие всех подключенных портов"""
    if connected_clients:
        for i in connected_clients:
            i.close()

serv = threading.Thread(target=serverf)
serv.start()

root = Tk()
root.title("server")

#лабелы-------
lbl1 = Label(root,text=f"IP адрес: {ip}. Слушание начато.")
lbl1.grid(column=0,row=0)
lbl2 = Label(root,text="")
lbl2.grid(column=0,row=3)
lbl3 = Label(root,text=f"кол-во клиентов: {len(connected_clients)}")
lbl3.grid(column=0,row=2)

#кнопкы-------
update_button = Button(root, text="закрыть все соединения", command=closeall)
update_button.grid(column=0,row=1)
def mainlooptk():
    """трэд обновления окна"""
    savednewclient=""
    while True:
        if savednewclient != showtezt:
            savednewclient = showtezt
            lbl2.config(text=f"Внимание, {showtezt}")
            lbl3.config(text=f"кол-во клиентов: {len(connected_clients)}")
            time.sleep(5)
            lbl2.config(text="")
            time.sleep(0.1)
maintk = threading.Thread(target=mainlooptk)
maintk.start()
root.mainloop()




