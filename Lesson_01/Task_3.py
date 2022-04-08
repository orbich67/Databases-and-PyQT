from tabulate import tabulate
from task_2 import host_range_ping


def host_range_ping_tab():
    host_dict = host_range_ping(True)
    print('-' * 40)
    print(tabulate(host_dict, headers='keys', tablefmt='pipe', stralign='center'))


if __name__ == "__main__":
    host_range_ping_tab()
