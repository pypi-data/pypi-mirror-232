from tqdm import tqdm
import paramiko
from typing import Set


def find_server_ipv4(username, password,
                     segment1: int = None, segment2: int = None, segment3: int = None, segment4: int = None,
                     port: int = 22) -> Set:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ip1_range = [segment1] if segment1 else list(range(256))
    ip2_range = [segment2] if segment2 else list(range(256))
    ip3_range = [segment3] if segment3 else list(range(256))
    ip4_range = [segment4] if segment4 else list(range(256))

    ips = [f"{i}.{j}.{x}.{y}" for y in ip4_range for x in ip3_range for j in ip2_range for i in ip1_range]
    wrong_ip = set()

    for ip in tqdm(ips, total=len(ips)):
        try:
            ssh.connect(hostname=ip, port=port, username=username, password=password, timeout=0.5)
        except Exception:
            wrong_ip.add(ip)

    return set(ips).difference(set(wrong_ip))


if __name__ == '__main__':
    print(find_server_ipv4('lizhen', 'lizhen123', 192, 168, 1))
