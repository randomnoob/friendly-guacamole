from items import Proxy, Storage
from mongoengine import *
from socks5ssh.initsocks import SockSpin

def seed_proxies():
    """
    Get proxies from common sites and fill the DB with those
    Proxy format : {host}:{port}
    """
    seed_local_proxies = SockSpin(ssh_dump_filename="randomssh.txt", num_socks=500).spin_socks()
    storage = Storage() #make a db connection
    for port in seed_local_proxies:
        Proxy(port=port).save()
    return seed_local_proxies


def seed_proxies_public():
    """
    Get proxies from common sites and fill the DB with those
    Proxy format : {host}:{port}
    """
    seed_local_proxies = SockSpin(ssh_dump_filename="randomssh.txt", num_socks=500).spin_socks()
    storage = Storage() #make a db connection
    for port in seed_local_proxies:
        Proxy(port=port).save()
    return seed_local_proxies

if __name__ == "__main__":
    seed = seed_proxies_public()
    print (seed)
