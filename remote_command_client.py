import socket, ssl
import subprocess
import json
from datetime import datetime
import smtplib
import configparser
import re
import os, shutil
import sys
from cryptography.fernet import Fernet
import requests
import time

_DATA = {
    'action': 'remcmd',
    'client': socket.gethostname(),
}
_BUFFER_SIZE = 1024
_END_DATA = b'>END<'

_CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
config_path = '/home/crypto/scripts/client.conf'
cipher_suite = Fernet(os.environ['CIPHER_KEY'].encode('utf-8'))
config = configparser.ConfigParser()
config.read(config_path)

server_certificate = cipher_suite.decrypt(config['DEFAULT']['SSLCrtPath'].encode('utf-8')).decode('utf-8')
server_ip = cipher_suite.decrypt(config['WEB']['Server_addr'].encode('utf-8')).decode('utf-8')
server_port = cipher_suite.decrypt(config['WEB']['Server_port'].encode('utf-8')).decode('utf-8')
mn_cli_path_locate_cmd = 'find /home/crypto/ -name "*-cli" ! -path "*qa*"'
mn_conf_path_locate_cmd = 'find /home/crypto/.*core -name "*.conf" ! -path "/home/crypto/.*/sentinel/*" ! -name "masternode*"'
# server_ip = 'localhost'
# server_port = 9000

def exec_command(command):
    try:
        return 0, subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT).decode('utf-8').strip('\n')
        #return subprocess.check_output("{0}".format(command), shell=True, stderr=subprocess.STDOUT).decode('utf-8')
    except subprocess.CalledProcessError as e:
        return 1, e.returncode, e.output.decode('utf-8').strip('\n')

def exec_command_no_wait(command):
    try:
        return 0, subprocess.run(command, shell=True, stderr=subprocess.STDOUT).decode('utf-8').strip('\n')
        #return subprocess.check_output("{0}".format(command), shell=True, stderr=subprocess.STDOUT).decode('utf-8')
    except subprocess.CalledProcessError as e:
        return 1, e.returncode, e.output.decode('utf-8').strip('\n')



def stopWallet():
    mn_cli_path_locate_cmd = 'find /home/crypto/ -name "*-cli" ! -path "*qa*"'
    mn_cli_path = exec_command(mn_cli_path_locate_cmd)
    if mn_cli_path[0] == 0:
        stop_daemon_cmd = mn_cli_path[1] + ' stop'
        res = exec_command(stop_daemon_cmd)
        if res[0] == 0:
            time.sleep(20)
            return True
        else:
            return False
    else:
        return False

def startWallet():
    mn_cli_path_locate_cmd = 'find /home/crypto/ -name "*-cli" ! -path "*qa*"'
    mn_cli_path = exec_command(mn_cli_path_locate_cmd)
    src_path = '/'.join(mn_cli_path[1].split('/')[:-1])
    MN_COIN = mn_cli_path[1].split('/')[-1].split('-')[0]
    coind = MN_COIN.lower() + 'd'
    coind_cmd = src_path + '/' + coind + ' -daemon -reindex'

    start_res = exec_command_no_wait(coind_cmd)
    if start_res[0] == 0:
        time.sleep(20)
        return True
    else:
        return False

def removeWalletFiles():
    mn_cli_path_locate_cmd = 'find /home/crypto/ -name "*-cli" ! -path "*qa*"'
    mn_cli_path = exec_command(mn_cli_path_locate_cmd)
    MN_COIN = mn_cli_path[1].split('/')[-1].split('-')[0]

    protected_files = ['wallet.dat', '{0}.conf'.format(MN_COIN.lower())]
    if '.conf' in protected_files:
        return False

    wallet_locate_cmd = 'find /home/crypto/ -name "wallet.dat"'
    wallet_path = exec_command(wallet_locate_cmd)
    wallet_data_path = ('/').join(wallet_path[1].split('/')[:-1])
    cf = len([name for name in os.listdir(wallet_data_path)])
    for the_file in os.listdir(wallet_data_path):
        if the_file in protected_files:
            continue
        file_path = os.path.join(wallet_data_path, the_file)
        if os.path.isfile(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    if len([name for name in os.listdir(wallet_data_path)]) == cf:
        return False
    else:
        return True

def restartWallet():
    print('restart wallet started')
    stop_res = stopWallet()
    print(stop_res)
    if stop_res:
        start_res = startWallet()
        if start_res:
            return 0, 'Wallet has been successfully restarted.'
        else:
            return 1, 'Unable to start wallet'
    else:
        return 1, 'Unable to stop wallet'
def cleanRestartWallet():
    stop_res = stopWallet()
    if stop_res:
        rem_res = removeWalletFiles()
        if rem_res:
            start_res = startWallet()
            if start_res:
                return 0, 'Wallet has been successfully restarted and files removed'
            else:
                return 1, 'Unable to start wallet'
        else:
            return 1, 'Unable to remove files'
    else:
        return 1, 'Unable to stop wallet'

def runCmd(cmd):
    return exec_command(cmd)
def updateWallet():
    update_res = exec_command(_CURRENT_PATH + '/update_wallet.sh')
    if update_res[0] == 0:
        return 0, 'Update Successfull'
    else:
        return 1, 'Update failed: {0}'.format(update_res[1])

def responseDispatcher(data):
    string_data = data.decode('utf-8')
    json_data = json.loads(string_data)
    if json_data['action'] == 'remcmd':
        if len(json_data) == 2:
            print("no action")
            sys.exit()
        if json_data['cmd'] == 'wall_restart':
            resp_status = restartWallet()
        elif json_data['cmd'] == 'wall_clean_restart':
            resp_status = cleanRestartWallet()
        elif json_data['cmd'] == 'cmd':
            resp_status = runCmd(cmd)
        elif json_data['cmd'] == 'update_wallet':
            resp_status = updateWallet()
        else:
            sys.exit()
    resp_data = _DATA
    resp_data['action'] = 'remcmd_resp'
    resp_data['cmd_id'] = json_data['cmd_id']
    if resp_status[0] == 0:
        resp_data['status'] = 'SUCCESSFULL'
        resp_data['output'] = resp_status[1]
    else:
        resp_data['status'] = 'FAILED'
        resp_data['output'] = resp_status[1]
    sendSocketData(resp_data)

def sendSocketData(message):
    data = b''
    string_message = json.dumps(message)
    byte_message = string_message.encode('utf-8')

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssl_sock = ssl.wrap_socket(s, ca_certs=server_certificate, cert_reqs=ssl.CERT_REQUIRED)
    ssl_sock.connect((server_ip, int(server_port)))
    ssl_sock.send(byte_message + _END_DATA)
    data = b''
    while True:
        packet = ssl_sock.recv(_BUFFER_SIZE)
        data += packet
        if data.decode('utf-8')[-5:] == _END_DATA.decode('utf-8'):
            data = data[:-5]
            break
    print(data)
    if data:
        responseDispatcher(data)
    ssl_sock.close()

if __name__ == "__main__":
    exec_command('cd /home/crypto/scripts && git pul')
    sendSocketData(_DATA)
    # string_message = json.dumps(_DATA)
    # byte_message = string_message.encode('utf-8')
    #
    # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # sock = ssl.wrap_socket(sock, ca_certs=server_certificate, cert_reqs=ssl.CERT_REQUIRED)
    # sock.connect((server_ip, int(server_port)))
    # sock.sendall(byte_message)
    # sock.shutdown(socket.SHUT_WR)
    # try:
    #
    #     while True:
    #         packet = sock.recv(1024)
    #         result += packet
    #         if not packet:
    #             break
    #
    #     print(result.decode('utf-8'))
    #
    # finally:
    #     sock.close()
