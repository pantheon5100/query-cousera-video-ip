import socket
import os
import re
import msvcrt
import multiprocessing


def get_ip_list(domain):
    """
    To get the resolved ip address of the domain.
    :param domain: string, such as "d3c33hcgiwev3.cloudfront.net"
    :return: list, the resolved ip address
    """
    ip_list = []
    try:
        addrs = socket.getaddrinfo(domain, None)
        for item in addrs:
            if item[4][0] not in ip_list:
                ip_list.append(item[4][0])
    except Exception as e:
        # print(str(e))
        pass
    return ip_list


def ping_res(domain, res_queue, n=5):
    """
    Ping the target domain.
    res_queue is the 'multiprocessing.Queue' to preserve the result. n is the number of ping times.
    Return the failure rate of ping.
    """
    ping = os.popen('ping -n {} {}'.format(n, domain)).read()
    # Find the target line from the ping results.
    ping = re.compile(r'数据包..+', re.M).findall(ping)
    if not ping:
        ping = re.compile(r'Packets..+', re.M).findall(ping)
    fail_rate = int(ping[0].split('(')[-1].split('%')[0])
    res_queue.put((domain, fail_rate))
    print("IP: {}, Failure Rate: {}%".format(domain, fail_rate))
    return fail_rate


def select_best_mul():
    """
    Using multiprocessing to create process to ping the resolved ip address simultaneous.
    Print the recommend ip address.
    """
    ip_list = get_ip_list("d3c33hcgiwev3.cloudfront.net")

    process_record = []
    res_queue = multiprocessing.Queue()
    for ip in ip_list:
        process = multiprocessing.Process(target=ping_res, args=(ip, res_queue, 5))
        process.start()
        process_record.append(process)

    for process in process_record:
        process.join()

    best = (None, 100)
    for _ in process_record:
        ip_rate = res_queue.get()
        if ip_rate[1] < best[1]:
            best = ip_rate

    print("\nThe recommend choice:{} \n with failure rate: {}%.".format(best[0], best[1]) )


if __name__ == "__main__":
    print("IP addresses with the minimum failure rate are available.")
    print("Start querying...")
    # select_best
    select_best_mul()
    print("Enter 'y' to end...")
    while msvcrt.getch() != b"y":
        pass
