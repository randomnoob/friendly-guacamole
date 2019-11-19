import aiohttp
import asyncio
import logging
import random

async def fetch(session, url, *args, **kwargs):
    await asyncio.sleep(1) #Sleep for 1 sec
    async with session.get(url, *args, **kwargs) as response:
        return await response.text()

async def grab_url(sequence_num, session, keyword, *args, **kwargs):
    resp = await fetch(session, keyword.url, *args, **kwargs)
    keyword.scraped_result = resp
    print (f"Proxy {keyword.proxy} grabbed : {str(resp).strip()[:10]}, request number {sequence_num}")
    return keyword

async def grab_batch(keyword_obj_list, storage, success_callback, failed_callback, *args, **kwargs):
    async with aiohttp.ClientSession() as session:
        results = []
        for idx, keyword in enumerate(keyword_obj_list):
            grab = await grab_url(idx, session, keyword, *args, **kwargs)
            if random.random() < 0.5:
                grab = keyword
                grab.scraped_result = ''
            # FAILED CASE
            if not grab.scraped_result: #In case cannot get the result, reverse its status to scraped=False
                call = failed_callback(storage, grab)
                # changed = storage_obj.change_status(keyword.keyword, scraped=False)
                print (f"Failed callback {keyword} ==> {call}")
            # SUCCESS CASE
            else:
                call = success_callback(storage, grab)
                print (f"Success callback {keyword} ==> {call}")
                results.append(grab)
        return results
