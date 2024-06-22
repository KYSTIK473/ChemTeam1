import ev3_dc as ev3
import time
import serial


my_ev3 = ev3.Jukebox(protocol=ev3.BLUETOOTH, host="00:16:53:53:e3:b4")

dir = "/home/root/lms2012/prjs/Parser/dat.rtf"

comand = ["WXX"    ,"DCU"    ,"BRS"    ,"WSS"    ,"DOU"    ,"BRW","SSS"  ] 
raz =    ["711,000",'111,000','341,300',"700,500","212,000","832,040","000,000"]
koll_k  = len(comand)

def ser_in(com,zz):
    global ser 
    ser = serial.Serial(com, zz, timeout=1)
    time.sleep(2) 
    return ser

def svet(i):
   global comand
   if comand[i] == "WSX":
      send_serial("-2;")
   elif comand[i] == "DCU":
      send_serial("-1;")
   elif comand[i] == "BRS":
      send_serial('-14;')
   elif comand[i] == "DOU":
      send_serial("-1;")
   elif comand[i] == "SSS":
      send_serial("-16;")

def send_serial(x):
    global ser
    ser.write(bytes(x, 'utf-8'))
    time.sleep(0.05)

def main():
    send_serial("-16;")
    i = 0 
    while True:
     print(i)
     if i < koll_k:
         dat = ("(E3D" + "," + raz[i] + "," + comand[i] + ")")
        
     else:
         dat = "(E1D,222,000,SSS)"

     if i < koll_k +1:
      txt_bytes_first = dat.encode("utf-8")
      my_ev3.write_file(dir, txt_bytes_first)
      svet(i)
      print(txt_bytes_first)
      time.sleep(3)
      my_ev3.del_file(dir)
      time.sleep(4)
      print("Mozno_kill")
     else:
        return 0
     i  = i+1
     
       
ser_in("COM19",115200)
send_serial("-16;")
main()