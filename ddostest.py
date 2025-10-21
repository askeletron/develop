import socket
import time
ip = "127.0.0.1"
port = 14888
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as cs:
    while True:
        try:
            cs.connect((ip,port))
            break
        except Exception as err:
            print(f"reconnecting, error: {err}")
    a = str(input())
    cs.send(a.encode("utf-8"))
    while True:
        cs.send(("#"*1000).encode("utf-8"))
   
