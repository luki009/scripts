import socket, ssl
import subprocess
import json
from datetime import datetime
import smtplib
import configparser
import re
import os
from cryptography.fernet import Fernet
import requests

_DATA = {
    'action': 'remcmd',
    'client': socket.gethostname(),
}
_BUFFER_SIZE = 1024
_END_DATA = b'>END<'

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
        return subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT).decode('utf-8').strip('\n')
        #return subprocess.check_output("{0}".format(command), shell=True, stderr=subprocess.STDOUT).decode('utf-8')
    except subprocess.CalledProcessError as e:
        return e.output.decode('utf-8').strip('\n')

def restartWallet():
    pass

def cleanRestartWallet():
    pass
def runCmd(cmd):
    exec_command(cmd)

def responseDispatcher(data):
    string_data = data.decode('utf-8')
    json_data = json.loads(string_data)
    if json_data['action'] == 'remcmd':
        if json_data['cmd'] == 'wall_restart':
            restartWallet()
        elif json_data['cmd'] == 'wall_clean_restart':
            cleanRestartWallet()
        elif json_data['cmd'] == 'cmd':
            runCmd(cmd)
        else:
            pass

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
    responseDispatcher(data)
    ssl_sock.close()

if __name__ == "__main__":
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
