# code to test out ssh into rpi using paramiko and run code remotely
# adapted from https://exitcode0.net/python-3-ssh-with-paramiko/

import paramiko

usr = 'pi'
pwd = 'plsdonthackme'
addr = '192.168.1.22'
command = 'python /home/pi/Team5/gesture/BerryIMU/python-BerryIMU-gyro-accel-compass-filters/berryIMU.py'

try:
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    client.connect(addr, username=usr, password=pwd)
    _, ss_stdout, ss_stderr = client.exec_command(command)
    r_out, r_err = ss_stdout.readlines(), ss_stderr.read()
    print(r_err)
    if len(r_err) > 5:
        print(r_err)
    else:
        print(r_out)
    client.close()
except IOError:
    print("didn't work")