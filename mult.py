from mongoengine import *
import time 
import random
import os
import requests
import zmq
from multiprocessing import Pool, Process, Queue


import zmq




from itertools import chain, islice
def chunks(iterable, size=10):
    iterator = iter(iterable)
    for first in iterator:
        yield chain([first], islice(iterator, size - 1))

class Key(Document):
    kw = StringField(required=True)
    scraped = BooleanField(required=True)

    def __repr__(self):
        return self.kw
    def __str__(self):
        return self.kw

class Storage:
    def __init__(self):
        self.db = connect('crawl_storage', username='crawlstorage', password='mangto535')

    def add_kw(self, kw):
        return Key(kw=kw, scraped=False).save()

    def get_10(self):
        kw_obj = Key.objects(scraped=False)[:10]
        return [x.kw for x in kw_obj]
    
    def get_all_queue(self):
        kw_obj = Key.objects(scraped=False)
        return kw_obj

    def change_status(self, kw):
        return Key.objects(kw=kw).first().update(scraped=True)

    def empty(self):
        indicator = Key.objects(scraped=False).first()
        if indicator:
            return True
        else:
            return False


def process_keyword(session, kw):
    time.sleep(1)
    r = requests.get('http://checkip.amazonaws.com/')
    with open('scraped/{}.txt'.format(str(kw)), 'w') as fout:
        fout.write(str(kw))
    print ("PID : {} ==> {} ==> {}".format(os.getpid(), kw, r.text.strip()))
    return r.text.strip()


def process_wrapper(iterable):
    session = requests.Session()


    for item in iterable:
        resp = process_keyword(session, item)
        if resp:
            data = {
                'kw': str(item),
                'result': resp,
            }


# *************************************#
def run_parallel(iterable, processes=4):
    processes = int(processes)
    pool = Pool(processes)
    try:
        pool = Pool(processes)
        jobs = []
        # run for chunks of files
        for chunk in iterable:
            jobs.append(pool.apply_async(process_wrapper,(list(chunk), )))
        for job in jobs:
            job.get()
        pool.close()
    except Exception as e:
        import traceback
        print (e)
        traceback.print_exc()

# *************************************#

def update_queue(queue):
    while True:



if __name__ == "__main__":
    storage = Storage()
    all_queues = storage.get_all_queue()
    chunkified = chunks(all_queues, size=10)
    # Create queues
    task_queue = Queue()
    done_queue = Queue()

    
    with Pool(processes=3) as pool:
        pool.map(process_batch, chunkified)

    run_parallel(chunkified, processes=5)
            
    

            
