from obuch import obuch
from fond import found,set_line,set_obj
from Send_data import ser_in,start_server,send_frames,cod_read,receive_messages,test,start_ev3
from system import system
import queue
from threading import Thread

set_obj(4)
set_line(15,15)
obuch(False,4)

#ser = ser_in("COM7",115200)
soce  = start_server(8485)
cod_read(soce)

ev3  = start_ev3()

print("ev3_ok")

def main(): 
    potoc()

def potoc():
    q = queue.Queue()

    th = Thread(target=found, args=(q,))
    th2 = Thread(target=system)
    th3 = Thread(target=send_frames, args=(q,))
    th4 = Thread(target=receive_messages)
    th5 = Thread(target=test)
    
    th4.start()
    th.start()
    th2.start()
    th3.start()
    th5.start()

    th.join()
    th2.join()
    th3.join()
    th4.join()
    th5.join()

main()
