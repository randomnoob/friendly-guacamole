import asyncio
import random
import time
import logging

from itertools import chain, islice
from async_grab_core import grab_batch

from items import Key, Storage, Keyword

async def random_sleep(t):
    # sleep for T seconds on average
    await asyncio.sleep(t * random.random() * 2)

async def consumer(queue):
    while True:
        callback, work_list, proxy = await queue.get()
        # Grab the pages, mark each
        results = await grab_batch(work_list, proxy)
        # Mark the task as done
        queue.task_done()
        # print (f"Done work : {results}")

async def producer(queue):
    while True:
        storage = Storage()
        try:
            tenkey = storage.get_10()
            # print (f"TENKEY : {tenkey}")
        except:
            break
        if queue.full():
            await asyncio.sleep(5)
            print ("Sleeping 5 seconds to prevent choking")
        template = "https://en.wikipedia.org/w/api.php?action=query&list=search&prop=info&format=json&srsearch={}"
        urls = [template.format(str(k)) for k in tenkey]
        # urls = ['http://checkip.amazonaws.com/' for i in range(0,10)]
        work = (urls, random.randrange(1,1500))
        await queue.put(work)
        print(f'produced 10 URLs')

def main():
    queue = asyncio.Queue(maxsize=20)
    loop = asyncio.get_event_loop()
    num_producer = 5
    num_consumer = 3000
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
