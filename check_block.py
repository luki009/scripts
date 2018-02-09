import os
import sys
import subprocess
import time


def exec_command(command):
    try:
        return subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT).decode('utf-8').strip('\n')
        #return subprocess.check_output("{0}".format(command), shell=True, stderr=subprocess.STDOUT).decode('utf-8')
    except subprocess.CalledProcessError as e:
        return e.output.decode('utf-8').strip('\n')


if __name__ == '__main__':
    mn_cli_path_locate_cmd = 'find /home/crypto/ -name "*-cli" ! -path "*qa*"'
    mn_cli_path = exec_command(mn_cli_path_locate_cmd)
    src_path = '/'.join(mn_cli_path.split('/')[:-1])
    MN_COIN = mn_cli_path.split('/')[-1].split('-')[0]
    coind = MN_COIN.lower() + 'd'
    coind_cmd = src_path + '/' + MN_COIN.lower() + 'd -daemon -reindex'
    stop_daemon_cmd = mn_cli_path + ' stop'
    blockcount_cmd = mn_cli_path + ' getblockcount'
    actual_blocks = exec_command(blockcount_cmd)
    try:
        with open('/home/crypto/blocks.txt', 'r') as blocks:
             blockcount = blocks.read()
    except:
        with open('/home/crypto/blocks.txt', 'w') as blocks:
             blocks.write('0')
             sys.exit()

    if int(blockcount) == int(actual_blocks):
        exec_command(stop_daemon_cmd)
        time.sleep(10)
        exec_command(coind_cmd)
        # print('blocks are same')
        with open('/home/crypto/blocks.txt', 'w') as blocks:
             blocks.write(actual_blocks)
    else:
        # print('blocks are different')
        with open('/home/crypto/blocks.txt', 'w') as blocks:
             blocks.write(actual_blocks)
             sys.exit()
