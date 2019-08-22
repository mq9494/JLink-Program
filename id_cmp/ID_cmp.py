# -*- coding:utf-8 -*-
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


dev_type = 0
mcu = ''
id_addr = 0
id_value = ''
id_key = ''

os.system('cls')
while True:
    print('\n***********  TEST  START  ******************\n')
    print('1.网关')
    print('2.智能锁\n')
    dev_type = input('请输入测试的设备类型：')
    if dev_type == '1':
        mcu = gw_mcu
        id_addr = gw_id_addr
        id_value = gw_id
        id_key = 'GW-ID'
        break
    elif dev_type == '2':
        mcu = lock_mcu
        id_addr = lock_id_addr
        id_value = lock_id
        id_key = 'DEV-ID'
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
            continue
        qr_code = input('请扫描二维码：\n\t')
        try:
            qr_code = qr_code.split('json=')[1]
            qr_id = eval(qr_code)[id_key]
        except:
            input(Red('请确认二维码是 {} 的二维码！'.format(DEV[dev_type-1])))
            continue
        id_read = jl.memory_read32(id_addr, 1)[0]
        id_read = id_value.format(id_read)
        t = datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S')
        record = t + ',' + DEV[dev_type-1] + ',' + qr_id + ',' + id_read +'\n'
        f = open('qr_code_cmp.csv', 'a+')
        f.write(record)
        f.close()
        if id_read == qr_id:
            result = input(Green('二维码匹配正确！'))
        else:
            print('\t设  备ID：{}'.format(Red(id_read)))
            print('\t二维码ID：{}'.format(Red(qr_id)))
            result = input(Red('二维码匹配错误！'))