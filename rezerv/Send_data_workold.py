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

def ser_in(com,zz):
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


def send_serial(x,ser):
    ser.write(bytes(x, 'utf-8'))
    time.sleep(0.05)

def start_ev3(host):
    
    my_ev3 = ev3.Jukebox(ev3.BLUETOOTH,host)

    dir = '/home/root/lms2012/prjs/Parser/dat.rtf'

    return my_ev3,dir

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
    
def test(ser,ev3_d):
  while True:
      x, y = parser()

      txt_bytes_first = x.encode('utf-8')
      ev3_d.write_file(dir, txt_bytes_first)
      send_serial(str(y),ser)
      time.sleep(1)
      ev3_d.del_file(dir)

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
        time.sleep(0.05)

def receive_messages():
    while True:
        try:
            data = client_socket.recv(1024).decode()
            if data:
                command(data)
        except ConnectionResetError as e:
            print(f"Connection was reset: {e}")
            # Attempt to reconnect or handle the disconnection appropriately
        time.sleep(0.1)  # Short pause to avoid overloading the CPU

def command(DAT):
    for i in range(13):
       parse(DAT,i)

def parse(DATA, i):
    dat1 = DATA.strip('()')
    dat_list = dat1.split(',')
    print(dat_list[i])
    return dat_list[i]