import asyncio
import json
import pprint
from dataclasses import dataclass
from datetime import datetime

import aiohttp
import jsons

https = 'http://101.200.203.153:8888'
token = 'sgdsgdsikhuewikdnjlkgh'


class QueryCondition(object):
    query = {'api': '/get'}

    def __init__(self, path):
        self.query['nodePath'] = path

    def get_count(self, count):
        self.query['count'] = count
        return self

    def orderby(self, order):
        self.query['orderBy'] = order
        return self

    def equalto(self, to):
        self.query['equalTo'] = to
        return self

    def startat(self, sa):
        self.query['startAt'] = sa
        return self

    def endat(self, ea):
        self.query['endAt'] = ea
        return self

    def limit_to_first(self, lf):
        self.query['limitToFirst'] = lf
        return self

    def limit_to_last(self, ll):
        self.query['limitToLast'] = ll
        return self

    def get_json(self):
        return jsons.dumps(self.query)
        # return json.JSONEncoder().encode(self.query)


async def get_tree(path):
    try:
        url = https + '/node/getTree'
        o = {'path': path, 'token': token}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=o) as response:
                msg = await response.text()
                print(msg)
                return msg
    except Exception as e:
        print(e)


async def get_node_by_con(q: QueryCondition):
    try:
        o = {'token': token}
        url = https + '/node/sdkapi'

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=o, data=q.get_json()) as response:
                msg = await response.json()
                pp = pprint.PrettyPrinter(indent=4, width=80, compact=False)
                if 'nodeContent' in msg.keys():
                    pp.pprint(msg['nodeContent'])
                    return msg['nodeContent']
                else:
                    return ''
    except Exception as e:
        print("get_node_by_con Value Exception:" + str(e))


class QueueAll:
    def __init__(self, queue):
        self.q = queue

    # 生产者
    async def addr_request(self, queue):
        await self.q.put(queue)

    # 消费者
    async def consume(self):
        while True:
            item = await self.q.get()
            # num = item[0]  # 因为存放的时候是元组，就取第一个数
            rs = await item[0](item[1])
            print(f'\t 消费： {rs}...')
            self.q.task_done()


async def main():
    queue = asyncio.PriorityQueue()
    await queue.join()
    q = QueueAll(queue)
    consumer = asyncio.ensure_future(q.consume())
    # await q.consume()
    while 1:
        await q.addr_request((get_tree, "/cem/orders"))

        # 阻塞并关闭------------------------------------
        await asyncio.sleep(1)
    consumer.cancel()

    # await get_tree('/cem/orders')
    # q = QueryCondition('/cem/CygpProducts')
    # await get_node_by_con(q.limit_to_first(100))


loop = asyncio.get_event_loop()
loop.run_until_complete(main())

# q = QueryCondition('/books')
# print(q.startat(0).limit_to_first(20).limit_to_last(50).orderby('ch').get_json())
