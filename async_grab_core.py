import aiohttp
import asyncio
import logging

async def fetch(session, url, *args, **kwargs):
    await asyncio.sleep(1) #Sleep for 1 sec
    async with session.get(url, *args, **kwargs) as response:
        return await response.text()

async def grab_url(sequence_num, session, proxy, url, *args, **kwargs):
    resp = await fetch(session, url, *args, **kwargs)
    print (f"Proxy {proxy} grabbed : {str(resp).strip()[:10]}, request number {sequence_num}")
    return (url, resp)

async def grab_batch(url_list, proxy, *args, **kwargs):
    async with aiohttp.ClientSession() as session:
        results = []
        for idx, url in enumerate(url_list):
            result = await grab_url(idx, session, proxy, url, *args, **kwargs)
            results.append(result)
            # with open('scraped/{}_{}.txt'.format(proxy, idx), 'w') as fout:
            #     fout.write(result[1])
        return results
