import serial
import time
import datetime
import serial.tools.list_ports
import os
from color import *

port_count = 0
port_list = list(serial.tools.list_ports.comports())
for i in port_list:
    port = list(i)
    port_count += 1
    print("{}. {} {} {}".format(port_count, port[0], port[1], port[2]))
# print(l[0][0])
port_input = input('请选择使用的端口序号:')

port = list(port_list[int(port_input)-1])[0]
baudrate = 115200
databits = 8
stopbits = 1
prioty = None

lock_test_record_file = 'Lock_ProductionPCBtest.csv'
gw_test_record_file = 'GW_ProductionPCBtest.csv'
config_file_lock = 'config_lock'
config_file_gw = 'config_gw'

config_file = ''
test_record_file = ''
id_key = ''
dev_type = ''

while True:
    print('\n***********  TEST  START  ******************\n')
    print('1.网关')
    print('2.智能锁\n')
    dev_type = input('请输入测试的设备类型：')
    if dev_type == '1':
        test_record_file = gw_test_record_file
        id_key = 'GW-ID'
        config_file = config_file_gw
        break
    elif dev_type == '2':
        test_record_file = lock_test_record_file
        id_key = 'DEV-ID'
        config_file = config_file_lock
        break
    else:
        os.system('cls')
        print(Red('\n请输入正确的设备类型序号！'))
        continue




f_config = open(config_file, 'r')

config = f_config.readline()
config = config.split(',')
pcb_sum = int(config[0])
pcb_pass = int(config[1])
pcb_fail = int(config[2])

t = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

sp = serial.Serial(port=port, baudrate=baudrate)

os.system('cls')
while True:
    try:
        print('请接好接插件，再上电...')
        line = sp.readline()
        line = sp.readline()
        # print(line)
        os.system('cls')
        data = line.decode('gbk')
        if 'Test Start' in data:
            sp.close()
            sp = serial.Serial(port=port, baudrate=baudrate, timeout=21)
            id = ''
            pcb_sum += 1
            while True:
                line = sp.readline()
                data = line.decode('gbk')
                if data != '':
                    if 'y/n' in data or 'Y/n' in data:
                        write_data = input(data)
                        if write_data == '' or write_data == 'y' or write_data == 'Y':
                            write_data = 'y'
                        elif write_data == 'n' or write_data == 'N':
                            write_data = 'n'
                        else:
                            print('\t请输入 Y/n ...\n')
                            continue
                        write_data1 = write_data.encode('gbk')
                        sp.write(write_data1)
                    elif 'result' in data:
                        result = eval(data)
                        error = result['result']
                        print()
                        if error == 0:
                            r = Green('测试成功！')
                            pcb_pass += 1
                        elif error == (1<<0):
                            r = Red('语音测试失败！')
                            pcb_fail += 1
                        elif error == (1<<1):
                            r = Red('LED灯测试失败！')
                            pcb_fail += 1
                        elif error == (1<<2):
                            r = Red('Lora测试失败！')
                            pcb_fail += 1
                        elif error == (1<<3):
                            if dev_type == '1':
                                r = Red('Flash测试失败！')
                            if dev_type == '2':
                                r = Red('指纹测试失败！')                                
                            pcb_fail += 1
                        elif error == (1<<4):
                            r = Red('按键测试失败！')
                            pcb_fail += 1
                        elif error == (1<<5):
                            if dev_type == '1':
                                r = Red('GM3测试失败！')
                            if dev_type == '2':
                                r = Red('语音测试失败！')
                            pcb_fail += 1
                        elif error == (1<<6):
                            r = Red('电机测试失败！')
                            pcb_fail += 1
                        elif error == (1<<7):
                            r = Red('背光测试失败！')
                            pcb_fail += 1
                        print(r, '测试用时：{}'.format(result['time']))
                        print()
                        t = datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S')
                        record = t + ',' + id + ',' + '{} of {}'.format(pcb_pass, pcb_sum) + '\n'
                        config = '{},{},{}'.format(pcb_sum, pcb_pass, pcb_fail)
                        # print(record)
                        # print(config)
                        f_record = open(test_record_file, 'a+')
                        f_record.write(record)
                        f_record.close()
                        f_config_w = open(config_file, 'w')
                        f_config_w.write(config)
                        f_config_w.close()
                        break
                    else:
                        print(data)
                        if id_key in data:
                            id = data[11:-2]
                            
                else:
                    print('串口通信超时 ...')
                    break
            sp.close()
            sp = serial.Serial(port=port, baudrate=baudrate)
        else:
            sp.close()
            sp = serial.Serial(port=port, baudrate=baudrate)
    except KeyboardInterrupt as e:
        print('退出测试')
        exit()

    