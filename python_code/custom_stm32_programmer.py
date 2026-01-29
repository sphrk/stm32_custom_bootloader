
## python custom_stm32_programmer.py --com-port com4 -w "<Path to bin file>"
## Ex:
## python custom_stm32_programmer.py --com-port com4 -w "D:\stm32_proj\Blink\Debug\Blink_100ms_PA3_PA4.bin"

## Ex: Erase Main App Flash
## python custom_stm32_programmer.py --com-port com4 -e
## Ex python custom_stm32_programmer.py --com-port <COM PORT> -e

## Ex: Write application bin file to Main App Flash
## python custom_stm32_programmer.py --com-port <COM PORT> -w "<Path to bin file>"


import os
import serial
# import struct
# import time
from tqdm import tqdm
import argparse


FLASH_FIRST_ADDR    = 0x08000000
FLASH_MAIN_APP_ADDR = 0x08008000
FLASH_TOTAL_SIZE    = 0x10000 # 64 kByte
FLASH_MAIN_APP_SECTION_SIZE = 0x8000 # 64kByte Main Section Size

CMD_TEST = 0x01
CMD_READ_FLASH = 0x02
CMD_ERASE_FLASH = 0x03
CMD_WRITE_FLASH = 0x04
# serial.Serial()
class MySerial(serial.Serial):
    def __init__(self, port, baud, timeout):
        super().__init__()
        self.port = port
        self.baudrate = baud
        self.timeout = timeout
        
    def send_test_cmd(self):
        if not self.is_open:
            raise Exception('Port is Not Open.')
        self.write([CMD_TEST])
        resp = self.read(1) # >>> type(res) # >>> <class 'bytes'>
        if resp and resp[0] == 0xff:
            print('Test Connection: OK')
        else:
            raise Exception('')
        return resp

    def read_flash(self, addr, n_byte):
        if not self.is_open:
            raise Exception('Port is Not Open.')
        
        if n_byte > 255:
            raise Exception('n_byte Must be less than 255.')
        
        msg = [CMD_READ_FLASH,
                (addr & 0xff),
                (addr>>8 & 0xff),
                (addr>>16 & 0xff),
                (addr>>24 & 0xff),
                n_byte]
        self.write(msg)
        resp = self.read(n_byte)
        return resp
    
    def erase_flash(self):
        if not self.is_open:
            raise Exception('Port is Not Open.')
       
        self.write([CMD_ERASE_FLASH])
        resp = self.read(1)
        # print('resp :', resp)
        if len(resp) and (resp[0] == 0xff):
            print('ERASE FLASH DONE.')
        else:
            raise Exception('ERASE FLASH ERROR.')
        return resp

    def write_flash(self, addr, n_byte, bytes_array):
        if not self.is_open:
            raise Exception('Port is Not Open.')
        
        msg = [CMD_WRITE_FLASH,
                (addr & 0xff),
                (addr>>8 & 0xff),
                (addr>>16 & 0xff),
                (addr>>24 & 0xff),
                n_byte]
        # print(list(map(hex, msg)))
        # print(list(map(hex, bytes_array)))
        self.write(msg)
        self.write(bytes_array)
        resp = self.read(1)
        # print('----->', resp)
        if resp and resp[0] == 0xff:
            return 1
        else:
            raise Exception('WRITE FLASH ERROR.')

    
    def read_flash_all(self, chunk_size=128, filename='a.bin'):
        start_addr = FLASH_FIRST_ADDR
        chunk_count = FLASH_TOTAL_SIZE // chunk_size
        print(chunk_count)
        with open(filename, 'wb+') as fp:
            for i in range(chunk_count):
                resp = self.read_flash(start_addr + i * chunk_size, chunk_size)
                fp.write(resp)
        print('READ FLASH DONE.')
        return 1
    
    def write_main_app_to_flash(self, filename, chunk_size=128):
        with open(filename, 'rb') as fp:
            data = fp.read()

        bytes_count = len(data)
        chunk_count = bytes_count // chunk_size
        remained_chunk_size = bytes_count % chunk_size
        print(f"{bytes_count= }, {chunk_count= }, {remained_chunk_size= }")

        flash_addr = FLASH_MAIN_APP_ADDR
        for i in tqdm(range(chunk_count)):
            ##### flash_addr = flash_addr + i * chunk_size
            # print(i, len(data[i * chunk_size:(i+1) * chunk_size]))
            self.write_flash(flash_addr + i * chunk_size, 
                             chunk_size, data[i * chunk_size:(i+1) * chunk_size])

        if remained_chunk_size:
            i += 1
            # print(i, len(data[i * chunk_size:]))
            self.write_flash(flash_addr + i * chunk_size, 
                             remained_chunk_size, data[i * chunk_size:])

        print('Memmory Programmed.')

## ---------------------------------------------------------------------------------------


parser = argparse.ArgumentParser(description='Custom STM32 Programmer for Custom USB Bootloader.')

parser.add_argument('--com-port', nargs=1, required=True, help='')

parser.add_argument('-t', '--test', action='store_true', help='Test USB Connection')
parser.add_argument('-e', '--erase', action='store_true', help='Erase Flash Memory (Main App)')

parser.add_argument('-r', '--read', action='store_true', help='Read Flash Memory (Main App)')
parser.add_argument('-o', dest='output_filename', help='Read Flash Memory (Main App)')

parser.add_argument('-w', '--write', nargs=1, help='Write Flash Memory (Main App)')

args = parser.parse_args()
# print(args)

com_port = args.com_port[0]
# if not valid com_port:
#     raise Exception('COM PORT is Not Valid.')

flag_test = args.test
flag_erase = args.erase
flag_read = args.read
flag_write = args.write


if not (flag_test or flag_erase or flag_read or flag_write):
    # print('exit')
    exit()

# PORT = 'COM4'
BAUD = 115200
TIMEOUT = 2 # sec
ser = MySerial(com_port, BAUD, TIMEOUT)

ser.close()
ser.open()
print('PORT OPENNED.')
ser.reset_input_buffer()
try:
    # Test Connection
    resp = ser.send_test_cmd()

    if flag_erase:
        ser.erase_flash()
    
    if flag_read:
        if args.output_filename is None:
            filename = 'o.bin'
        else:
            filename = args.output_filename

    if flag_write:
        if not flag_erase:
            ser.erase_flash()
        
        filename = args.write[0]
        
        if not os.path.exists(filename):
            raise Exception(f'"{filename}" File Not Exists.')
        
        ser.write_main_app_to_flash(filename=filename, chunk_size=128)
    

except Exception as e:
    raise (e)
finally:
    ser.close()
    print('PORT CLOSED.')


