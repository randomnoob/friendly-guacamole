from .core import pxssh
import traceback
import subprocess
import requests
import time
import os
import stat
import random

LIMIT_NUM_SOCKS = 40
SSHPASS_CMD_TEMPLATE = 'sshpass -p {password} nohup ssh -D {port} -M -S {socket} -f -q -N -C {username}@{host}'

class SockSpin:
    def __init__(self, ssh_dump_filename, num_socks, encoding='utf-8'):
        with open(ssh_dump_filename, encoding=encoding) as dump:
            ssh_strings = [x.strip() for x in dump.readlines()]
            ssh = [x.split('|')[:3] for x in ssh_strings]
            random.shuffle(ssh)
            self.ssh = ssh
            print ('SOCKS list loaded and shuffled')
        self.num_socks = num_socks
        self.cwd = os.getcwd()
        self.base_port = 9001

    def check_ifsocket(self, path, tries=3, wait=0):
        try:
            print ("Checking socket @ ", path)
            if wait:
                time.sleep(1)
            mode = os.stat(path).st_mode
            return stat.S_ISSOCK(mode)
        except FileNotFoundError:
            return False


    @staticmethod
    def try_login(host, username, password):
        try:
            logfile=open(os.path.join(os.getcwd(), "SOCKSPIN.log"), "w")
            p = pxssh(logfile=logfile, encoding='utf-8', timeout=10)
            p.login(host, username, password, login_timeout=4)
            return True
        except Exception as err:
            print("Exception : {0}".format(err))
            # traceback.print_exc()
            return False

    def forkspin(self, host, username, password, port):
        """
        Spin up an SSH session with -M "master" mode and a -S "socket" included, using sshpass
        to pass the password as plain text, enabling the ability to start unattended ssh sessions
        Then checks if "socket" exists. If it does, then return True, meaning socks5 established

        eg sshpass -p passwordishere nohup ssh -D 9001 -M -S ~/.ssh/9001.sock -C -N -f bamboo@chicken.thitgaluoc.com
        the NOHUP is for single-core machines which slows down the forking process of ssh, therefore cause it to close down
        because of SIGHUP signal from the os.
        """
        try:
            # Socket path set to current working dir
            socket_dirpath = os.path.join(self.cwd, 'socket')
            socket_filepath = os.path.join(socket_dirpath, '{}.sock'.format(port))
            if not os.path.exists(socket_dirpath):
                os.mkdir(socket_dirpath)
            # SSHPASS comes to the rescue
            cmd = SSHPASS_CMD_TEMPLATE.format(username=username, password=password, port=port, host=host, socket=socket_filepath)
            print ('____________________________________________________________________________\n{}'.format(cmd))
            # Spawn SSHPASS
            subprocess.Popen(cmd, shell=True)
            # Checks if socket_filepath actually exists
            # Wait 1 seconds for the socket to initialize
            # time.sleep(1)
            # if self.check_ifsocket(socket_filepath):
            #     print ('Socket file FOUND')
            #     return True
            # else:
            #     print ('Socket file doesn\'t exist. Bypassing')
            #     return False
            return (socket_filepath, port)
        except Exception as err:
            print("Exception : {0}".format(err))
            traceback.print_exc()

    def request_through_socks(self, port, host, tries=3):
        try:
            if tries==0:
                return False
            proxy = 'socks5://127.0.0.1:{}'.format(port)
            print ('Testing with : ', proxy)
            r = requests.get('http://icanhazip.com', proxies = {
                                                                'http': proxy,
                                                                'https': proxy
                                                                }, timeout=8)
            if r.status_code == 200:
                return True
            else:
                return self.request_through_socks(port, host, tries=tries-1)
        except ConnectionError as err:
            print ('ConnectionError : {}'.format(err))
            print ('Retrying 3 times')
            return self.check_socks_connect(port, host, tries=tries-1)
        except ConnectionRefusedError as err:
            print ('ConnectionRefusedError')
            return False
        except:
            traceback.print_exc()
            return False

    def google_through_socks(self, port, host, tries=3):
        try:
            if tries==0:
                return False
            proxy = 'socks5://127.0.0.1:{}'.format(port)
            print ('Testing with : ', proxy)
            r = requests.get('https://www.google.com/search?client=ubuntu&channel=fs&q=sfgvdf+&ie=utf-8&oe=utf-8', proxies = {
                                                                'http': proxy,
                                                                'https': proxy
                                                                }, timeout=8)
            if r.status_code == 200:
                if not 'unusual traffic from your computer network' in r.text:
                    return True
                else:
                    return False
            else:
                return self.request_through_socks(port, host, tries=tries-1)
        except ConnectionError as err:
            print ('ConnectionError : {}'.format(err))
            print ('Retrying 3 times')
            return self.check_socks_connect(port, host, tries=tries-1)
        except ConnectionRefusedError as err:
            print ('ConnectionRefusedError')
            return False
        except:
            traceback.print_exc()
            return False


    def spin_socks(self):
        # commands_ran_tuple contains (spawned_socket_file_path, port_number)
        commands_ran_tuple = []
        # ports_remained contains only port number checked against google
        ports_remained = []
        result_port = []
        for plus_port, test in enumerate(self.ssh):
            local_port = self.base_port+plus_port
            host = test[0]
            username = test[1]
            password = test[2]
            forked = self.forkspin(host, username, password, local_port)
            if forked:
                commands_ran_tuple.append(forked)


        # Checks for connectivity
        # Sleep 10 seconds for all connections to be connected
        time.sleep(10)
        for socket_filepath, local_port in commands_ran_tuple:
            if self.check_ifsocket(socket_filepath, tries=1):
                ports_remained.append(local_port)

        # Checks for google blocking
        for local_port in ports_remained:
            sock_request = self.request_through_socks(local_port, host)
            print ('REQUEST THROUGH SOCKS5 : {}'.format(sock_request))
            if sock_request:
                sock_google = self.google_through_socks(local_port, host)
                print ('GOOGLE THROUGH SOCKS5 : {}'.format(sock_google))
                if sock_google:
                    result_port.append(local_port)
                    print ('+++++++++GOT ===>{}<=== SOCKS++++++++\n{}____________________________'.format(len(result_port), result_port))
            if len(result_port) >= self.num_socks:
                break

        result_port = [str(x) for x in result_port]
        print ('RESULT : {}'.format(result_port))
        return result_port
