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


config_path = '/home/crypto/scripts/client.conf'
cipher_suite = Fernet(os.environ['CIPHER_KEY'].encode('utf-8'))
config = configparser.ConfigParser()
config.read(config_path)

server_certificate = cipher_suite.decrypt(config['DEFAULT']['SSLCrtPath'].encode('utf-8')).decode('utf-8')
server_ip = cipher_suite.decrypt(config['WEB']['Server_addr'].encode('utf-8')).decode('utf-8')
server_port = cipher_suite.decrypt(config['WEB']['Server_port'].encode('utf-8')).decode('utf-8')
mn_cli_path_locate_cmd = 'find /home/crypto/ -name "*-cli" ! -path "*qa*"'
# mn_conf_path_locate_cmd = 'find /home/crypto/.*core -name "*.conf" ! -path "/home/crypto/.*/sentinel/*" ! -name "masternode*"'

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





def sendSocketData(message):
    ### MESSAGE CSV FORMAT ###
    ### action,
    ### Action:indb - insert to database
        string_message = json.dumps(message)
        byte_message = string_message.encode('utf-8')
    # try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssl_sock = ssl.wrap_socket(s, ca_certs=server_certificate, cert_reqs=ssl.CERT_REQUIRED)
        ssl_sock.connect((server_ip, int(server_port)))
        ssl_sock.write(byte_message)
        data = ssl_sock.recv(1024).decode()
            if data:
                responseDispatcher(data)
            else:
                pass
            ssl_sock.close()
            break

    # except:
    #     print("Problem with data send to server !!!")


if __name__ == "__main__":

   
    sendSocketData(_DATA)
