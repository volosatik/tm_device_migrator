import socket
import paramiko
from scp import SCPClient
import csv
from pathlib import Path
import os
from datetime import date 

"""SET THIS CORRECTLY"""
OLD_GATEWAY = '10.108.125.230'
NEW_GATEWAY = '172.31.0.5'

file_to_use = 'configuration.csv'
file_with_sh_script_Template = 'file_for_uci_sh_script.txt'

def set_the_gateway_for_device_pool(file):
    Path(file).write_text(Path(file).read_text().replace('SOME_GATEWAY',NEW_GATEWAY))

#set_the_gateway_for_device_pool(file_with_sh_script_Template)

def configuration_parser(file):
    device_list_tmp = []
    with open(file, newline='') as devices_list_file:
        configuration_reader = csv.reader(devices_list_file, delimiter = '\t')
        for row in configuration_reader:
            if len(row):
                device_list_tmp.append(tuple(row)+('ТМ3',))
    return device_list_tmp


def ensure_dir(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

def device_migration(entry_data, tobe_device_gateway, current_gateway):
    if not isinstance(entry_data, tuple):
        print(f'format error')
    else:
        device_address = entry_data[0]
        device_id = entry_data[1]
        device_type = entry_data[2]
        print(f'connecting to device with adress {device_address} and id {device_id}')
        """Static Params """
        user = "root"
        secret = "tmsoft"
        port = 22
        """Not to be static params"""
        host = device_address
        source_addr = int(device_id)
        # this params are set to default gateway
        string0 = 'system.@watchcat[0].pinghosts'
        string1 = 'mspd48.socket.address'
        string2 = 'ntpclient.@ntpserver[0].hostname'
        string3 = 'system.ntp.server'
        string4 = 'mwan3.wan.track_ip'
        string5 = 'mwan3.wan2.track_ip'
        gateway_default = tobe_device_gateway
        # this param is default port
        string6 = 'mspd48.socket.port'
        port_default = '11000'
        # this params are set to default apn
        string7 = 'network.wan.apn'
        string8 = 'network.wan2.apn'
        apn_default = 'iotutilities'

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((current_gateway, 0))
        sock.connect((host, port))

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=host, username=user, password=secret, sock=sock)

        stdin, stdout, stderr = ssh_client.exec_command('uci get mspd48.main.address')
        data = stdout.read() + stderr.read()
        mspd48_addr = int(str.strip(str(data), "'b'\\n'"))
        if mspd48_addr == source_addr:
            try:
                print(f'changing configuration of the device with id {mspd48_addr}')
                stdin, stdout, stderr = ssh_client.exec_command(f'uci set {string0}={gateway_default}')
                stdin, stdout, stderr = ssh_client.exec_command(f'uci set {string1}={gateway_default}')
                stdin, stdout, stderr = ssh_client.exec_command(f'uci set {string2}={gateway_default}')
                stdin, stdout, stderr = ssh_client.exec_command(f'uci set {string3}={gateway_default}')
                stdin, stdout, stderr = ssh_client.exec_command(f'uci set {string4}={gateway_default}')
                stdin, stdout, stderr = ssh_client.exec_command(f'uci set {string5}={gateway_default}')
                stdin, stdout, stderr = ssh_client.exec_command(f'uci set {string6}={port_default}')
                stdin, stdout, stderr = ssh_client.exec_command(f'uci set {string7}={apn_default}')
                stdin, stdout, stderr = ssh_client.exec_command(f'uci set {string8}={apn_default}')
                stdin, stdout, stderr = ssh_client.exec_command(f'uci commit')
                stdin, stdout, stderr = ssh_client.exec_command('uci show')
                print(f'finished changing configuration of the device with id {mspd48_addr}')
                dirname = date.today().strftime("%b-%d-%Y")
                path = './'+dirname
#            ensure_dir(path)
                os.makedirs(path, exist_ok=True)		
                with open (path+'/'+str(mspd48_addr)+'.txt', 'w') as writer:
                    writer.writelines(str(stdout.read() + stderr.read()))
                scp_client = SCPClient(ssh_client.get_transport())
            #
                print("start loading sh script")
                scp_client.put("/home/nkaluzhi/tm_device_migrator/file_for_uci_sh_script.txt", "/bin/tester.sh")
                scp_client.close()
                print("end loading sh script")
                stdin, stdout, stderr = ssh_client.exec_command('reboot')
                print("rebooting device")
            except Exception as err:
                raise ValueError(str(err))
        else:
#            print(f'ip {device_address} and id {device_id} do not match')
            raise ValueError(f'ip {device_address} and id {device_id} do not match')
        ssh_client.close()
        sock.close()

