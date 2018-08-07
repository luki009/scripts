import socket, ssl
import sqlite3
import json
import configparser
import smtplib
import _thread
import os
import requests


#server_listen_ip = '185.35.64.209'
server_listen_ip = '0.0.0.0'
server_listen_port = 5005
server_max_connections = 1000
# server_certificate = '/home/crypto/crt/CryptoFrontSSL.crt'
# server_certificate_key = '/home/crypto/crt/CryptoFrontSSL.key'
# server_db_path = '/home/crypto/WEB/cr/db.sqlite3'
# config_path = '/home/crypto/config/server.conf'

# config = configparser.ConfigParser()
# config.read(config_path)
server_certificate = os.path.dirname(os.path.realpath(__file__)) + '/server.crt'
server_certificate_key = os.path.dirname(os.path.realpath(__file__)) + '/server.key'
example_data="Hello from server"
    # connstream.send(example_data)



def get_profit():
    coins = {
        'Bulwark':{"id":224, 'hashrate':55, "algorithm":"NIST5", 'miner':'alexis', 'tag':'BWK', 'block_time':'', 'block_reward':'', 'nethash':'', 'price':'', 'profit':''},
        'DGB-Skein':{'id':114, 'hashrate':630, "algorithm":"Skein", 'miner':'alexis', 'tag':'DGB', 'block_time':'', 'block_reward':'', 'nethash':'', 'price':'', 'profit':''},
        'Zencash':{"id":185, 'hashrate':535, "algorithm":"Equihash", 'miner':'claymore', 'tag':'ZEN', 'block_time':'', 'block_reward':'', 'nethash':'', 'price':'', 'profit':''},
        'Zcash':{"id":166, 'hashrate':535, "algorithm":"Equihash", 'miner':'claymore', 'tag':'ZEC', 'block_time':'', 'block_reward':'', 'nethash':'', 'price':'', 'profit':''},
        'Zclassic':{'id':167, 'hashrate': 535, "algorithm":"Equihash", 'miner':'claymore', 'tag':'ZCL', 'block_time':'', 'block_reward':'', 'nethash':'', 'price':'', 'profit':''},
        'BitcoinGold':{"id":214, 'hashrate':535, "algorithm":"Equihash", 'miner':'claymore', 'tag':'BTG', 'block_time':'', 'block_reward':'', 'nethash':'', 'price':'', 'profit':''},
        'BitcoinPrivate':{'id':230, 'hashrate':535, "algorithm":"Equihash", 'miner':'claymore', 'tag':'BTCP', 'block_time':'', 'block_reward':'', 'nethash':'', 'price':'', 'profit':''},
        'Verge-X17':{'id':219, 'hashrate':13.7, "algorithm":"X17", 'miner':'ccminer', 'tag':'XVG', 'block_time':'', 'block_reward':'', 'nethash':'', 'price':'', 'profit':''},
        'Bitcore':{'id':202, 'hashrate':18, "algorithm": "TimeTravel10", 'miner':'ccminer', 'tag':'BTX', 'block_time':'', 'block_reward':'', 'nethash':'', 'price':'', 'profit':''},
        'Ravencoin':{'id':234, 'hashrate':13, "algorithm":"X16R", 'miner':'ocminer', 'tag':'RVN', 'block_time':'', 'block_reward':'', 'nethash':'', 'price':'', 'profit':''},
        'Luxcoin':{'id':212, 'hashrate':27, "algorithm":"PHI1612", 'miner':'phiminer', 'tag':'LUX', 'block_time':'', 'block_reward':'', 'nethash':'', 'price':'', 'profit':'' },
    }

    for i in coins:
        data = requests.get('https://whattomine.com/coins/{0}.json'.format(coins[i]['id'])).json()
        coins[i]['block_time'] = data['block_time']
        coins[i]['block_reward'] = data['block_reward']
        coins[i]['nethash'] = data['nethash']
        ll = requests.get('https://www.cryptopia.co.nz/api/GetMarket/{0}_BTC'.format(coins[i]['tag'])).json()
        if ll['Data'] is not None:
            coins[i]['price'] = ll['Data']['LastPrice']
        else:
            coins[i]['price'] =  0
        profit = (float(coins[i]['hashrate']) / int(coins[i]['nethash'])) * ((float(coins[i]['block_reward']) * 86400) / float(coins[i]['block_time'])) * float(coins[i]['price'])
        coins[i]['profit'] = profit

    return coins




def processData(conn, data):
    json_data = json.loads(string_data.decode('utf-8'))

def deal_with_client(connstream):
    data = connstream.read(1000000)
    if data:
        print(data)
        dataReturn = processData(connstream, data)
        if dataReturn:
            connstream.send(dataReturn.encode('utf-8'))

if __name__ == "__main__":
    bindsocket = socket.socket()
    bindsocket.bind((server_listen_ip, server_listen_port))
    bindsocket.listen(server_max_connections)


    while True:
        newsocket, fromaddr = bindsocket.accept()
        connstream = ssl.wrap_socket(newsocket,
                                     server_side=True,
                                     certfile=server_certificate,
                                     keyfile=server_certificate_key)

        try:
            deal_with_client(connstream)
        finally:
            connstream.shutdown(socket.SHUT_RDWR)
            connstream.close()
