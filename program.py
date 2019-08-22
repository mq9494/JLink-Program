import pylink
import serial
import time
import os

DEV = ''
gw_mcu = 'STM32F103RC'
lock_mcu = 'STM32L071RB'

lock_boot_addr = 0x08000000
lock_app1_addr = 0x08003800
lock_app2_addr = 0x08010400
lock_sn_addr = 0x0801FE00

lock_boot_bin = 'lock_1.bin'
lock_app1_bin = 'lock_2.bin'
lock_app2_bin = 'lock_3.bin'


def test():
    pass

def program():
    jl = pylink.JLink()
    os.system('cls')
    while True:
        try:
            jl.open()
            jl.set_tif(pylink.enums.JLinkInterfaces.SWD)
            print('JLink连接成功 ...')
        except:
            input('请检查 JLink 是否连接好，按"Enter"键继续 ...')
            continue
        input('请连接好测试板，按“Enter”键开始烧录 ...')
        while True:
            try:
                jl.connect('STM32L071RB')
                if jl.connected():
                    print('MCU连接成功 ...')
                else:
                    print('重连MCU ...')
                    continue
            except pylink.JLinkException:
                continue
            print('开始烧录程序 ...')
            try:
                jl.flash_file(lock_boot_bin, lock_boot_addr)
                jl.flash_file(lock_app1_bin, lock_app1_addr)
                print('烧录成功 ！！！')
                input('请连接好下一块测试板，按“Enter”键开始烧录 ...')
            except pylink.JLinkFlashException:
                print('烧录出错，正在重连 ...')

    pass

def writeSN():
    pass



if __name__ == "__main__":
    pass