import asyncio
import random
import time, datetime
import logging

from itertools import chain, islice
from async_grab_core_v2 import grab_batch

from items import Proxy, Key, Storage, KeywordBatch, GoogleResult

async def random_sleep(t):
    # sleep for T seconds on average
    await asyncio.sleep(t * random.random() * 2)

def consumer_success_callback(storage, keyword_obj):
    storage.mark_proxy_last_used(keyword_obj.proxy)
    storage.mark_proxy_idle(keyword_obj.proxy)
    res = GoogleResult(keyword=keyword_obj.keyword,
                html=keyword_obj.scraped_result,
                time=str(datetime.datetime.now()))
    return res.save()
    
def consumer_failed_callback(storage, keyword_obj):
    changed_status = storage.change_status(kw=keyword_obj.keyword, scraped=False)
    storage.mark_proxy_last_used(keyword_obj.proxy)
    storage.mark_proxy_idle(keyword_obj.proxy)
    storage.mark_proxy_dead(keyword_obj.proxy)
    return changed_status

async def consumer(queue):
    while True:
        # work is a list of Keyword instances
        storage, keywords = await queue.get()
        # Grab the pages
        await grab_batch(keyword_obj_list=keywords,
                                storage=storage,
                                success_callback=consumer_success_callback,
                                failed_callback=consumer_failed_callback)

        # Mark the task as done
        queue.task_done()
        # print (f"Done work : {results}")

async def producer(queue):
    while True:
        storage = Storage()
        try:
            tenkey = storage.get_10(string=True)
            # print (f"TENKEY : {tenkey}")
        except:
            break
        if queue.full():
            await asyncio.sleep(5)
            print ("Sleeping 5 seconds to prevent choking")
        template = "https://en.wikipedia.org/w/api.php?action=query&list=search&prop=info&format=json&srsearch={}"
        proxy = storage.get_proxy()
        keywords = KeywordBatch(tenkey, template, proxy).get_keywords()
        work = (storage, keywords)
        await queue.put(work)
        # print(f'produced 10 URLs')

def main():
    queue = asyncio.Queue(maxsize=20)
    loop = asyncio.get_event_loop()
    num_producer = 2
    num_consumer = 5
    try:
        for i in range(1,num_producer):
            loop.create_task(producer(queue))
        for i in range(1,num_consumer):
            loop.create_task(consumer(queue))
        loop.run_forever()
    except KeyboardInterrupt:
        logging.info("Process interrupted")
    finally:
        loop.close()
        logging.info("Successfully shutdown the Mayhem service.")


if __name__ == "__main__":
    # asyncio.run(main())
    main()
