import socket, ssl
import subprocess
import json
from datetime import datetime
import smtplib
import configparser
import re

config = configparser.ConfigParser()
config.read(config_path)

config_path = '/home/crypto/config/client.conf'
server_certificate = "/home/crypto/crt/CryptoFrontSSL.crt"
server_ip = config['WEB']['Server_addr']
server_port = config['WEB']['Server_port']
mn_cli_path_locate_cmd = 'find /home/crypto/ -name "*-cli"'
#mn_cli_path_locate_cmd = 'find /root/ALQO/src -name "*-cli"'
mn_status_cmd = 'masternode status'
#mn_cli_path_locate = 'locate -i -r ".*-cli$"'

#mn_cli_path = subprocess.check_output('locate -i -r "/root.*-cli$"',stderr=subprocess.STDOUT, shell=True)
def sendMail(toaddrs=None, subject=None, imsg=None):
    if toaddrs == None:
        toaddrs = config['DEFAULT']['NotificationEmail']
    fromaddr = config['DEFAULT']['SenderEmail']
    msg = 'Subject: {0} \n\n {1}'.format(subject, imsg)
    em_username = config['SERVICE.SMTP']['UserName']
    em_passwd = config['SERVICE.SMTP']['Password']
    server = smtplib.SMTP_SSL(config['SERVICE.SMTP']['Server'], config['SERVICE.SMTP']['Port'])
    server.ehlo()
    server.login(em_username,em_passwd)
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()



def data_alert(string_data=None, nodename=None):
    if string_data == None:
        return False
    for rule in config['ALERTS']['Rules'].split('\n'):
        cat, reg, msg = rule.split('|')
        prog = re.compile(reg)
        if prog.match(string_data):
            print('Rule found: ', reg)
            if cat == 'd':
                reciepments = config['DEFAULT']['DeveloperEmail'].split('\n')
            elif cat == 'c':
                reciepments = config['DEFAULT']['ClientEmail'].split('\n')
            elif cat == 'dc':
                reciepments = config['DEFAULT']['ClientEmail'].split('\n') + config['DEFAULT']['DeveloperEmail'].split('\n')


            sendMail(toaddrs=reciepments, subject=nodename, imsg=msg)
    return True



def exec_command(command):
    try:
        return subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT).decode('utf-8').strip('\n')
        #return subprocess.check_output("{0}".format(command), shell=True, stderr=subprocess.STDOUT).decode('utf-8')
    except subprocess.CalledProcessError as e:
        return e.output.decode('utf-8').strip('\n')

def sendSocketData(message):
    ### MESSAGE CSV FORMAT ###
    ### action,
    ### Action:indb - insert to database
        string_message = json.dumps(message)
        byte_message = string_message.encode('utf-8')
    # try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssl_sock = ssl.wrap_socket(s, ca_certs=server_certificate, cert_reqs=ssl.CERT_REQUIRED)
        ssl_sock.connect((server_ip, server_port))
        ssl_sock.write(byte_message)
        ssl_sock.close()
    # except:
    #     print("Problem with data send to server !!!")

def get_masternode_status_data(cli_path):
    MN_STATUS_REQUEST = exec_command('{0} {1}'.format(cli_path, mn_status_cmd))
    MN_STATUS_DATA = json.loads(MN_STATUS_REQUEST)
    ### KEYS : vin, service, status
    return MN_STATUS_DATA





if __name__ == "__main__":

    mn_cli_path = exec_command(mn_cli_path_locate_cmd)
    hostname = exec_command('hostname')
    mn_status_data = get_masternode_status_data(mn_cli_path)
    ### ACTION: diu - insert or update into db
    dataToSend = {
        'MnStatus':{
            'hostname': hostname,
            'action':'diu',
            'mn_health': mn_status_data,
            'update_time':str(datetime.now())
        }
    }

    print(dataToSend)
    data_alert(string_data=dataToSend, nodename=hostname):
    sendSocketData(dataToSend)
