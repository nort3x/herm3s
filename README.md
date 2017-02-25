# herm3s
simple sample of botnets (python)

[Note] Herm3s is 'NOT' a fully functional botnet 

1-its simple
2-good for beginners
3-easy to edit
4-no any encryptions

Herm3s is a botnet written in Python for beginners to start thinking how botnets work and how can you improve it in your way

iam not responsible for anything you are going to do with it

every help you might need is in the source by it self but i will dump it here:
------------- Master -----------------------
# defaults (change these parameters)
# or just leave them be like this if you want just test it out
sv_ip = '127.0.0.1'
sv_port = 3223
password = 'change_me'
silent = 0  # 0 = verbose/ -1 = very verbose/ 1 = silent

# interactive shell commands:
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


-------- Slave ---------
# defaults (change these parameters)
# or just leave them be like this if you want just test it out

sv_ip = '127.0.0.1'
sv_port = 3223
retry_delay_connect = 5
password = 'change_me'
default_name = 'Slave_t3st'

[Hint] in last paragraph be sure to check this out:
# main spinner
# for melting(start up function) and make hidden directory remove # from get_ready()
# get_ready()

-peace <3
nort3x
