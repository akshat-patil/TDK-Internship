import snap7 
import time

IP="192.168.0.1"
RACK=0
SLOT=1
DB_NUMBER = 1
START_ADDRESS = 0
plc = snap7.client.Client()
output_ON = b'\x01'
output_OFF = b'\x00'
output_ON_timer = 1

def plc_connect():
    plc.connect(IP,RACK,SLOT)

def plc_disconnect():
    plc.disconnect()
    plc.destroy()

def main():
    plc_connect()
    plc.db_write(DB_NUMBER, START_ADDRESS, output_ON)
    time.sleep(output_ON_timer)
    plc.db_write(DB_NUMBER, START_ADDRESS, output_OFF)
    plc_disconnect()

if __name__ == "__main__":
    main()
