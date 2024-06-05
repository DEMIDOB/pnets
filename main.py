import threading
import netifaces

from ipv4 import IPv4

THREADS_NUM = 32


def main():
    addr = netifaces.ifaddresses("en0")
    en0 = addr[netifaces.AF_INET]

    assert len(en0) > 0, "Failed to determine the external iP-Address"

    me = en0[0]
    my_ip = IPv4(me["addr"])
    netmask = IPv4(me["netmask"])

    my_ip.apply_mask(netmask)

    ips = []

    for _ in range(netmask.num_devices - 1):
        my_ip.inc()
        ips.append(IPv4(my_ip.ip_str))

    # print(ips)
    res = [False for _ in range(len(ips))]

    def _thread_target(idx: int):
        nonlocal ips
        ips_count = len(ips)

        for current_level in range(ips_count // THREADS_NUM + 1):
            current_idx = THREADS_NUM * current_level + idx
            if current_idx >= len(res):
                continue

            current_ip = ips[current_idx]
            res[current_idx] = current_ip.lookup()

    threads = [threading.Thread(target=_thread_target, args=(i, )) for i in range(THREADS_NUM)]

    for t in threads:
        t.start()

    for i, t in enumerate(threads):
        t.join()

    max_name_len = 0
    for r_ip in ips:
        max_name_len = max((len(r_ip.name), max_name_len))

    for r_ip in sorted(ips, key=lambda x: x.name):
        if r_ip.is_alive:
            print(r_ip.name + " " * (max_name_len - len(r_ip.name)), r_ip.ip_str)


if __name__ == '__main__':
    main()
