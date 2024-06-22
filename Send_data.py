import ev3_dc as ev3
import time
import socket
import serial
import hashlib
import os 
import struct
import queue
import pickle
import cv2

current_dir = os.path.dirname(os.path.abspath(__file__)) 
file = "sec.txt"
folder = "data"

frame_queue = queue.Queue()
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 200]

global a
a = ""

com_list = None
global stst_ot 
stst_ot = 1

def ser_in(com,zz):
    global ser 
    ser = serial.Serial(com, zz, timeout=1)
    time.sleep(2) 
    return ser

def start_server(port):
    host = '0.0.0.0'  # Исправлено здесь
    global client_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:    
        server_socket.bind((host, port))
        print('Socket bind complete')
        server_socket.listen(10)
        print("Ждем подключения клиента...")
        client_socket, client_address = server_socket.accept()  # Принимаем подключение
        print(f'Connected to {client_address}')
        return client_socket
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        server_socket.close()
        print("Server stopped")

def send_serial(x):
    global ser
    ser.write(bytes(x, 'utf-8'))
    time.sleep(0.05)

def start_ev3():
    global my_ev3
    global direct
    my_ev3 = ev3.Jukebox(protocol=ev3.BLUETOOTH, host="00:16:53:53:e3:b4")

    direct = '/home/root/lms2012/prjs/Parser/dat.rtf'

    return my_ev3,direct

def parser(client_socket):
    data = client_socket.recv(1024).decode()
    first_part = data[0:22]  # Получаем первые 22 символа
    second_part = data[23:27]  # Получаем оставшиеся символы
    print(first_part, second_part) 

    return first_part, second_part

def code():
    with open(os.path.join(current_dir,folder,file), 'r') as dan:
        secret = dan.read().encode()
        hash_object = hashlib.sha512(secret)
        hex_dig = hash_object.hexdigest()
        return hex_dig
    
def test():
  global stst_ot
  global direct
  while True:
        if com_list and stst_ot==0 :
            com = "(E1D,999,999," + com_list  + "XX)"
            print(com)
            txt_bytes_first = com.encode('utf-8')
            my_ev3.write_file(direct, txt_bytes_first)
            time.sleep(1)
            my_ev3.del_file(direct)
            stst_ot = 1

def cod_read(client_socket):
 while True:
    data = client_socket.recv(1024).decode()
    if data == code():
        dat = "OK"
        client_socket.send(dat.encode())
        return 0
    else:
        dat = "Error"
        client_socket.send(dat.encode())
        print("Error_KOD_P")
        pass

def send_frames(q):
    time.sleep(2)
    max_queue_size = 2  # Установите максимальный размер очереди здесь
    i  = 0 
    while True:
        if q.qsize() > max_queue_size:
            q.queue.clear()  # Очищаем очередь
            continue  # Пропускаем текущую итерацию цикла

        fr = q.get()  # Получаем frame из очереди
        result, fr_encoded = cv2.imencode('.jpg', fr, encode_param)
        if result:
            data = pickle.dumps(fr_encoded, 0)
            size = len(data)
            client_socket.sendall(struct.pack(">L", size) + data)
        time.sleep(0.1)

def receive_messages():
    while True:
        data = client_socket.recv(1024).decode()
        print(data)
        if data:
            command(data)
        time.sleep(0.1)  # Короткая пауза, чтобы избежать чрезмерной загрузки процессора

def command(DAT):
    for i in range(13):
       parse(DAT,i)

def parse(DATA, i):
    global com_list
    global stst_ot
    global stand_list 
    dat1 = DATA.strip('()')
    sitt_list = []
    stand_list = ""
    global a
    if len(dat1) == 2: 
        if dat1 == "ww":
            com_list= "W"
        elif dat1 == "wb":
            com_list = "B"
        elif dat1 == "wr":
            com_list = "R"   
        elif dat1 == "wl":
            com_list = "L"
        elif dat1 == "wh":
            com_list = "H"
        elif dat1 == "wj":
            com_list = "J"
        elif dat1 == "zo":
            com_list = "O"
        elif dat1 == "zc":
            com_list = "C"
        elif dat1 == "zu":
            com_list = "U"
        elif dat1 == "zd":
            com_list = "D"
        print(com_list)

        stst_ot = 0
    # else:
    #     sitt_list = dat1.split(',')
    #     print(sitt_list[i])
 