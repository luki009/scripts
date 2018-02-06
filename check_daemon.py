import os
import sys
import subprocess


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
    process_cmd = 'ps ax | grep -v grep | grep ' + coind

    if exec_command(process_cmd):
        sys.exit()
    else:
        print("daemon is dead")
        exec_command(process_cmd)
