from task_1 import get_ip_address, host_ping


def host_range_ping(get_list=False):
    while True:
        ip_start = input('Введите первоначальный адрес: ')
        try:
            ipv4_start = get_ip_address(ip_start)
            if ipv4_start:
                print('Начальный ip-адрес: ', str(ipv4_start))
            last_oct = int(str(ipv4_start).split('.')[3])
            break
        except Exception as e:
            print('Некорректный ip-адрес. ', e)

    while True:
        ip_end = input('Введите количество проверяемых адресов: ')
        if not ip_end.isnumeric():
            print('Необходимо ввести число!')
        else:
            if (last_oct + int(ip_end)) > 255 + 1:
                print(f'Может меняться только последний октет каждого адреса,\n'
                      f'максимально возможное число доступных адресов для проверки: {255 + 1 - last_oct}\n')
            else:
                break
    host_list = []
    for num in range(int(ip_end)):
        host_list.append(str(ipv4_start + num))
    if not get_list:
        host_ping(host_list)
    else:
        return host_ping(host_list, True)


if __name__ == "__main__":
    host_range_ping()
