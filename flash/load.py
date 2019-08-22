from color import *
import time
import datetime
import pylink
import os

DEV = ['网关', '智能锁']
gw_mcu = 'STM32F103RC'
gw_id_addr = 0x08035000
gw_id = '000000{:08X}'

lock_mcu = 'STM32L071RB'
lock_id_addr = 0x0801FE00
lock_id = '010000{:08X}'


bin_path = '../../bin/'
file_bin_lock = ''
file_bin_gw = ''

record_file_lock = 'lock_qr_code_write.csv'
record_file_gw = 'gw_qr_code_write.csv'
record_file = ''


for root, dirs, files in os.walk(bin_path):
    # print(files)
    for file_name in files:
        if 'lock' in file_name:
            file_bin_lock = file_name
        if 'gateway' in file_name:
            file_bin_gw = file_name



dev_type = 0
mcu = ''
id_addr = 0
id_value = ''
id_key = ''

file_bin = ''
program_addr = 0x08000000

os.system('cls')
while True:
    print('\n***********  TEST  START  ******************\n')
    print('1.网关\t\t{}'.format(file_bin_gw))
    print('2.智能锁\t\t{}\n'.format(file_bin_lock))
    dev_type = input('请输入测试的设备类型：')
    if dev_type == '1':
        mcu = gw_mcu
        id_addr = gw_id_addr
        id_value = gw_id
        id_key = 'GW-ID'
        file_bin = bin_path + file_bin_gw
        record_file = record_file_gw
        break
    elif dev_type == '2':
        mcu = lock_mcu
        id_addr = lock_id_addr
        id_value = lock_id
        id_key = 'DEV-ID'
        file_bin = bin_path + file_bin_lock
        record_file = record_file_lock
        break
    else:
        os.system('cls')
        print(Red('\n请输入正确的设备类型序号！'))
        continue

dev_type = int(dev_type)
jl = pylink.JLink()


while True:
    try:
        jl.open()
        jl.set_tif(pylink.enums.JLinkInterfaces.SWD)
        # print('JLink连接成功 ...')
    except:
        input('请检查 JLink 是否连接好，按"Enter"键继续 ...')
        continue

    while True:
        record = ''
        try:
            os.system('cls')
            jl.connect(mcu)
            if jl.connected():
                print('MCU连接成功 ...')
            else:
                print('重连MCU ...')
                continue
        except pylink.JLinkException:
            print('连接MCU ...')
            break
        qr_code = input('请扫描二维码：\n\t')
        try:
            # 用于二维码
            qr_code = qr_code.split('json=')[1]     
            qr_id = eval(qr_code)[id_key][-8:]

            # 用于条形码
            # qr_id = qr_code[-8:]
            
            qr_id = int(qr_id, 16)
        except:
            input(Red('请确认二维码是 {} 的二维码！'.format(DEV[dev_type-1])))
            continue
        try:
            jl.erase()
            jl.flash_file(file_bin, program_addr)
            jl.flash_write32(id_addr, [qr_id])
            id_read = jl.memory_read32(id_addr, 1)[0]
        except:
            input('请确认 JLink 连接正确 。。。')
            continue
        t = datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S')
        record = t + ',' + DEV[dev_type-1] + ',' + id_value.format(qr_id) + ',' + str(id_read) +'\n'
        f = open(record_file, 'a+')
        f.write(record)
        f.close()
        if id_read == qr_id:
            result = input(Green('二维码写入正确！'))
        else:
            result = input(Red('二维码写入错误！'))
    continue