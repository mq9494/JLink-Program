import serial
import time
import datetime
import serial.tools.list_ports
import os, sys
import msvcrt

def myInput(strP, timeout = 5):
    print(strP)
    start_time = time.time()
    input = ''
    while True:
        if msvcrt.kbhit():
            input = msvcrt.getche()
        if len(input) != 0 or (time.time() - start_time) > timeout:
            break
    if len(input) > 0:
        return input
    else:
        return b'n'


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
test_log_lock = 'log_lock.txt'
test_log_gw = 'log_gw.txt'
config_file_lock = 'config_lock'
config_file_gw = 'config_gw'

config_file = ''
test_record_file = ''
id_key = ''
dev_type = ''
test_log = ''

while True:
    print('\n***********  TEST  START  ******************\n')
    print('1.网关')
    print('2.智能锁\n')
    dev_type = input('请输入测试的设备类型：')
    if dev_type == '1':
        test_record_file = gw_test_record_file
        id_key = 'GW-ID'
        config_file = config_file_gw
        test_log = test_log_gw
        break
    elif dev_type == '2':
        test_record_file = lock_test_record_file
        id_key = 'DEV-ID'
        config_file = config_file_lock
        test_log = test_log_lock
        break
    else:
        os.system('cls')
        print(('\n请输入正确的设备类型序号！'))
        continue




f_config = open(config_file, 'r')

config = f_config.readline()
config = config.split(',')
pcb_sum = int(config[0])
pcb_pass = int(config[1])
pcb_fail = int(config[2])

t = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

while True:
    try:
        sp = serial.Serial(port=port, baudrate=baudrate)
        break
    except:
        input('串口可能被占用，无法打开！')

os.system('cls')
while True:
    try:
        print('请接好接插件，再上电...')
        line = sp.readline()
        # print(line)
        os.system('cls')
        try:
            data = line.decode('gbk')
            f_log = open(test_log, 'a+')
            f_log.write(data)
            f_log.close()
        except:
            continue
        if 'Test Start' in data:
            sp.close()
            sp = serial.Serial(port=port, baudrate=baudrate, timeout=120)
            id = ''
            pcb_sum += 1
            while True:
                line = sp.readline()
                # print(line)
                try:
                    data = line.decode('gbk')
                    f_log = open(test_log, 'a+')
                    f_log.write(data)
                    f_log.close()
                except:
                    continue
                # print(data)
                if data != '':
                    if 'y/n' in data or 'Y/n' in data or 'Y\\n' in data:
                        write_data = myInput(data, timeout=9).decode('gbk')
                        # print(write_data)
                        while True:
                            if write_data == '' or write_data == 'y' or write_data == 'Y' or write_data == '\r':
                                write_data = 'y'
                                break
                            elif write_data == 'n' or write_data == 'N':
                                write_data = 'n'
                                break
                            else:
                                # print('\t请输入 Y/n ...\n')
                                write_data = myInput('\t请输入 Y/n ...\n', timeout=9).decode('gbk')
                                continue
                        write_data1 = write_data.encode('gbk')
                        sp.write(write_data1)
                    elif 'result' in data:
                        r = ''
                        result = eval(data)
                        error = result['result']
                        print()
                        if error == 0:
                            r = ('测试成功！')
                            pcb_pass += 1
                        if error & (1<<0) == (1<<0):
                            r += ('语音测试失败！')
                            pcb_fail += 1
                        if error & (1<<1) == (1<<1):
                            r += ('LED灯测试失败！')
                            pcb_fail += 1
                        if error & (1<<2) == (1<<2):
                            r += ('Lora测试失败！')
                            pcb_fail += 1
                        if error & (1<<3) == (1<<3):
                            if dev_type == '1':
                                r += ('Flash测试失败！')
                            if dev_type == '2':
                                r += ('指纹测试失败！')                                
                            pcb_fail += 1
                        if error & (1<<4) == (1<<4):
                            r += ('按键测试失败！')
                            pcb_fail += 1
                        if error & (1<<5) == (1<<5):
                            if dev_type == '1':
                                r += ('GM3测试失败！')
                            if dev_type == '2':
                                r += ('语音测试失败！')
                            pcb_fail += 1
                        if error & (1<<6) == (1<<6):
                            r += ('电机测试失败！')
                            pcb_fail += 1
                        if error & (1<<7) == (1<<7):
                            r += ('背光测试失败！')
                            pcb_fail += 1
                        if error & (1<<8) == (1<<8):
                            r += ('低功耗测试失败！')
                            pcb_fail += 1
                        print(r, '测试用时：{} 秒'.format(result['time']))
                        print()
                        t = datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S')
                        record = t + ',' + id + ',' + r + ',' + '{}'.format(pcb_sum) + '\n'
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
            pass
            # sp.close()
            # sp = serial.Serial(port=port, baudrate=baudrate)
    except KeyboardInterrupt as e:
        print('退出测试')
        exit()

    