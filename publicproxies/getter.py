from spys import get_spysone_proxies
from mongoengine import *

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
import items


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
    seed = get_spysone_proxies()
    items.Storage() #make a db connection
    for proxy in seed:
        url = "http://{}".format(proxy)
        if not items.Proxy.objects(proxy_url=url):
            items.Proxy(proxy_url=url).save()
        print ("Inserted {} into DB".format(url))
    return items.Proxy.objects()


if __name__ == "__main__":
    seed = seed_proxies_public()
    print (seed)
