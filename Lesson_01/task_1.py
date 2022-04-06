import platform
import socket
import subprocess
from ipaddress import ip_address


def get_ip_address(host):
    try:
        ipv4 = socket.gethostbyname(host)
    except socket.gaierror:
        return False
    return ip_address(ipv4)


def host_ping(lst, get_list=False):
    result = {'Доступные узлы': [], 'Недоступные узлы': []}
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    for host in lst:
        ipv4 = get_ip_address(host)
        if ipv4:
            args = ['ping', param, '1', str(ipv4)]
            reply = subprocess.Popen(args, stdout=subprocess.PIPE)
            if reply.wait() == 0:
                result['Доступные узлы'].append(f'{host}')
                # print(f'{host} - Узел доступен (ip: {ipv4})')
                print(f'{host} - Узел доступен')
                continue
        result['Недоступные узлы'].append(f'{host}\n')
        print(f'{host} - Узел не доступен')
    if get_list:
        return result


if __name__ == '__main__':
    lst_hosts = ['yandex.rus', 'gb.ru', 'localhost', 'a.a.a.a', '8.8.8.8']
    host_ping(lst_hosts)
