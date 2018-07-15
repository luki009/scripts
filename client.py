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




config_path = '/home/crypto/scripts/client.conf'
cipher_suite = Fernet(os.environ['CIPHER_KEY'].encode('utf-8'))
config = configparser.ConfigParser()
config.read(config_path)

server_certificate = cipher_suite.decrypt(config['DEFAULT']['SSLCrtPath'].encode('utf-8')).decode('utf-8')
server_ip = cipher_suite.decrypt(config['WEB']['Server_addr'].encode('utf-8')).decode('utf-8')
server_port = cipher_suite.decrypt(config['WEB']['Server_port'].encode('utf-8')).decode('utf-8')
mn_cli_path_locate_cmd = 'find /home/crypto/ -name "*-cli" ! -path "*qa*"'
# mn_conf_path_locate_cmd = 'find /home/crypto/.*core -name "*.conf" ! -path "/home/crypto/.*/sentinel/*" ! -name "masternode*"'

mn_status_cmd = 'masternode status'
sn_status_cmd = 'systemnode status'
smartn_status_cmd = 'smartnode status'
mn_list_cmd = 'masternode list'
sn_list_cmd = 'systemnode list'
smartn_list_cmd = 'smartnode list'
mn_wallet_default_balance_cmd = 'getreceivedbyaddress' # + wallet id
mn_wallet_transactions_cmd = 'listunspent'
mn_import_wallet_cmd = 'importaddress'
#mn_cli_path_locate = 'locate -i -r ".*-cli$"'

#mn_cli_path = subprocess.check_output('locate -i -r "/root.*-cli$"',stderr=subprocess.STDOUT, shell=True)
def sendMail(toaddrs=None, subject=None, imsg=None):
    if toaddrs == None:
        toaddrs = config['DEFAULT']['NotificationEmail']
    fromaddr = config['DEFAULT']['SenderEmail']
    msg = 'Subject: {0} \n\n {1}'.format(subject, imsg)
    em_username = cipher_suite.decrypt(config['SERVICE.SMTP']['UserName'].encode('utf-8')).decode('utf-8')
    em_passwd = cipher_suite.decrypt(config['SERVICE.SMTP']['Password'].encode('utf-8')).decode('utf-8')
    smtp_server_addr = cipher_suite.decrypt(config['SERVICE.SMTP']['Server'].encode('utf-8')).decode('utf-8')
    smtp_server_port = cipher_suite.decrypt(config['SERVICE.SMTP']['Port'].encode('utf-8')).decode('utf-8')
    server = smtplib.SMTP(smtp_server_addr, smtp_server_port)
    server.ehlo()
    server.starttls()
    server.login(em_username,em_passwd)
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()
    return True

# def get_bwk_balance(wallet):
#     try:
#         from bs4 import BeautifulSoup
#     except:
#         exec_command('pip3 install bs4')
#         return str(0)
#     s = requests.get('https://altmix.org/coins/10-Bulwark/explorer/address/{0}'.format(wallet)).text
#     soup = BeautifulSoup(s, 'html.parser')
#     tables = soup.find_all('table')
#     return tables[0].find_all('td')[-1].get_text().strip('\n')

def get_smartcash_balance(wallet):
    try:
        from bs4 import BeautifulSoup
    except:
        exec_command('pip3 install bs4')
        return str(0)
    s = requests.get('https://insight.smartcash.cc/address/{0}'.format(wallet)).text
    soup = BeautifulSoup(s, 'html.parser')
    tables = soup.find_all('tbody')
    print(tables)
    return tables[0].find_all('td')[-3].get_text().strip('\n').strip(' SMART')

def data_alert(string_data=None, nodename=None):
    if string_data == None:
        return False
    for rule in config['ALERTS']['Rules'].split('\n'):
        cat, reg, msg = rule.split(';')
        prog = re.compile(reg)
        if prog.match(str(string_data)):
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
        ssl_sock.connect((server_ip, int(server_port)))
        ssl_sock.write(byte_message)
        ssl_sock.close()
    # except:
    #     print("Problem with data send to server !!!")

def get_masternode_status_data(cli_path, coin):
    masternode = 0
    systemnode = 0
    smartnode = 0
    while masternode != 1 or systemnode != 1 or smartnode != 1:
        cmd = '{0} {1}'.format(cli_path, mn_status_cmd)
        MN_STATUS_REQUEST = exec_command(cmd)
        if re.search("This is not a masternode", MN_STATUS_REQUEST) or re.search("Method not found", MN_STATUS_REQUEST):
            pass
        else:
            masternode = 1
            break
        cmd = '{0} {1}'.format(cli_path, sn_status_cmd)
        MN_STATUS_REQUEST = exec_command(cmd)
        if re.search("This is not a systemnode", MN_STATUS_REQUEST) or re.search("Method not found", MN_STATUS_REQUEST):
            pass
        else:
            systemnode = 1
            break
        cmd = '{0} {1}'.format(cli_path, smartn_status_cmd)
        MN_STATUS_REQUEST = exec_command(cmd)
        if re.search("This is not a smartnode", MN_STATUS_REQUEST) or re.search("Method not found", MN_STATUS_REQUEST):
            break
        else:
            smartnode = 1
            break
    MN_STATUS_DATA = json.loads(re.search('{.*}', MN_STATUS_REQUEST.replace('\n', '')).group(0))
    if coin == "bulwark":
        MN_STATUS_DATA["status"] = MN_STATUS_DATA.pop("message")
        if 'code' in MN_STATUS_DATA:
            MN_TX = '0000000'
        else:
            MN_TX = MN_STATUS_DATA['txhash']


        if re.match('^0*$', MN_TX):
            MN_ACTIVE = 'NEW_START_REQUIRED'
        else:
            cmd = '{0} {1} | grep {2} | wc -l'.format(cli_path, mn_list_cmd, MN_TX)
            MN_LIST_STATUS = exec_command(cmd)
            if int(MN_LIST_STATUS) == 0:
                MN_ACTIVE = 'NOT_LISTED'
            else:
                cmd = '{0} {1}'.format(cli_path, mn_list_cmd)
                node_list = json.loads(exec_command(cmd))
                for node in node_list:
                    if node['txhash'] == MN_TX:
                        MN_ACTIVE = node['status']

    else:
        # print(MN_STATUS_DATA)
        if 'vin' in MN_STATUS_DATA:
            MN_TX = re.search(r"(?<=Point\().*?(?=\),)", MN_STATUS_DATA['vin']).group(0).split(',')[0]
        elif 'outpoint' in MN_STATUS_DATA:
            MN_TX = re.search(r"(?<=Point\().*?(?=\))", MN_STATUS_DATA['outpoint']).group(0).split(',')[0]
        # print(MN_TX)
        # print(masternode, systemnode, smartnode)

        if systemnode == 1:
            if re.match('^0*$', MN_TX):
                MN_ACTIVE = 'NEW_START_REQUIRED'
            else:
                cmd = '{0} {1} | grep {2} | wc -l'.format(cli_path, sn_list_cmd, MN_TX)
                MN_LIST_STATUS = exec_command(cmd)
                if int(MN_LIST_STATUS) == 0:
                    MN_ACTIVE = 'NOT_LISTED'
                else:
                    cmd = '{0} {1} | grep {2}'.format(cli_path, sn_list_cmd, MN_TX)
                    MN_ACTIVE = exec_command(cmd).split(':')[1].strip('\", ')
        elif masternode == 1:
            if re.match('^0*$', MN_TX):
                MN_ACTIVE = 'NEW_START_REQUIRED'
            else:
                cmd = '{0} {1} | grep {2} | wc -l'.format(cli_path, mn_list_cmd, MN_TX)
                MN_LIST_STATUS = exec_command(cmd)
                if int(MN_LIST_STATUS) == 0:
                    MN_ACTIVE = 'NOT_LISTED'
                else:
                    cmd = '{0} {1} | grep {2}'.format(cli_path, mn_list_cmd, MN_TX)
                    MN_ACTIVE = exec_command(cmd).split(':')[1].strip('\", ')

        elif smartnode == 1:
            if re.match('^0*$', MN_TX):
                MN_ACTIVE = 'NEW_START_REQUIRED'
            else:
                cmd = '{0} {1} | grep {2} | wc -l'.format(cli_path, smartn_list_cmd, MN_TX)
                MN_LIST_STATUS = exec_command(cmd)
                if int(MN_LIST_STATUS) == 0:
                    MN_ACTIVE = 'NOT_LISTED'
                else:
                    cmd = '{0} {1} | grep {2}'.format(cli_path, smartn_list_cmd, MN_TX)
                    MN_ACTIVE = exec_command(cmd).split(':')[1].strip('\", ')


    MN_STATUS_DATA['MN_ACTIVE_STATUS'] = MN_ACTIVE
    ### KEYS : vin, service, status
    return MN_STATUS_DATA

def get_masternode_default_balance(cli_path, wallet_id, coin):
    if wallet_id == 'None':
        return str(0)
    if coin == 'bitcloud':
        return requests.get('https://chainz.cryptoid.info/btdx/api.dws?q=getbalance&a={0}'.format(wallet_id)).text
    # elif coin == 'bulwark':
    #
    #     return get_bwk_balance(wallet_id)
    else:
        cmd = '{0} {1} {2}'.format(cli_path, mn_wallet_default_balance_cmd, wallet_id)
        return exec_command(cmd)

def get_masternode_balance(wallet_id, coin):
    if wallet_id == 'None':
        return str(0)
    try:
        if coin == 'bitcloud':
            return requests.get('https://chainz.cryptoid.info/btdx/api.dws?q=getbalance&a={0}'.format(wallet_id)).text
        elif coin == 'bulwark':
            return requests.get('https://explorer.bulwarkcrypto.com/ext/getbalance/{0}'.format(wallet_id)).text
        elif coin == 'alqo':
            return requests.get('https://explorer.alqo.org/api/balance/{0}'.format(wallet_id)).text
        elif coin == 'crowdcoin':
            return requests.get('http://explorer.cryptopros.us/ext/getbalance/{0}'.format(wallet_id)).text
        elif coin == 'innova':
            return requests.get('http://explorer.innovacoin.info/ext/getbalance/{0}'.format(wallet_id)).text
        elif coin == 'vivo':
            return requests.get('http://vivo.explorerz.top:3003/ext/getbalance/{0}'.format(wallet_id)).text
        elif coin == 'smartcash':
            return get_smartcash_balance(wallet_id)
        elif coin == 'crowncoin':
            return requests.get('http://ex.crownlab.eu/ext/getbalance/{0}'.format(wallet_id)).text
        else:
            return str(0)
    except:
        return str(0)

def get_wallet_transactions(cli_path, def_bal):
    cmd = '{0} {1}'.format(cli_path, mn_wallet_transactions_cmd)
    transactions = json.loads(exec_command(cmd))
###############################
    for tx in transactions:
        if float(tx["amount"]) == float(def_bal):
            transactions.remove(tx)
    return transactions

def set_import_address(cli_path, wallet):
    cmd = '{0} {1} "{2}"'.format(cli_path, mn_import_wallet_cmd, wallet)
    exec_command(cmd)


if __name__ == "__main__":
    exec_command('cd /home/crypto/scripts && git pull')

    mn_cli_path = exec_command(mn_cli_path_locate_cmd)
    MN_COIN = mn_cli_path.split('/')[-1].split('-')[0]

    hostname = exec_command('hostname')
    mn_status_data = get_masternode_status_data(mn_cli_path, MN_COIN)
    if 'payee' in mn_status_data:
        mn_wallet = mn_status_data['payee']
    elif 'pubkey' in mn_status_data:
        mn_wallet = mn_status_data['pubkey']
    elif 'addr' in mn_status_data:
        mn_wallet = mn_status_data['addr']
    else:
        mn_wallet = 'None'
        mn_status_data['payee'] = mn_wallet

    # set_import_address(mn_cli_path, mn_wallet)
    DEFAULT_BALANCE = get_masternode_default_balance(mn_cli_path, mn_wallet, MN_COIN).split('.')[0]
    BALANCE = get_masternode_balance(mn_wallet, MN_COIN)
    UPDATE_TIME = datetime.now()
    WALLET_TRANSACTIONS = get_wallet_transactions(mn_cli_path, DEFAULT_BALANCE)



    ### ACTION: diu - insert or update into db
    dataToSend = {
        'action': 'mndata',
        'MnStatus': {
            'hostname': hostname,
            'action':'diu',
            'mn_health': mn_status_data,
            'update_time':str(UPDATE_TIME.strftime("%d.%m.%Y %H:%M:%S"))
        },
        'MnData': {
            'DEFAULT_BALANCE': DEFAULT_BALANCE,
            'BALANCE': BALANCE,
            'WALLET_TRANSACTIONS': WALLET_TRANSACTIONS,
            'MN_COIN': MN_COIN,
        }
    }
    print(dataToSend)
    try:
        data_alert(string_data=dataToSend, nodename=hostname)
    except:
        pass
    sendSocketData(dataToSend)
