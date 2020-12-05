# -*- coding: utf-8 -*-
import asyncio
import json
import signal
from dataclasses import dataclass
from datetime import datetime
import jsons
import uvloop

from aiowebsocket.converses import AioWebSocket


async def async_timer(aws):
    print("timers:")


@dataclass
class Command(jsons.JsonSerializable):
    def __init__(self, cmd, path):
        self.cmd = cmd
        self.path = path


@dataclass
class User(jsons.JsonSerializable):
    def __init__(self, id):
        self.id = id


class LoginCommand(Command, jsons.JsonSerializable):
    def __init__(self, cmd, path, user):
        super(LoginCommand, self).__init__(cmd, path)
        self.user = user


async def startup(uri):
    while True:
        try:
            async with AioWebSocket(uri) as aws:
                converse = aws.manipulator
                msg = await converse.receive()
                x = msg.decode()
                userid = json.loads(x)["data"]["user"]["id"]

                # '{"cmd":7,"path":"/yuanda/node/books","user":{"id":"'+ f'{userid} }'}}'
                lc = LoginCommand(cmd=7, path='/yuanda/node/books', user=User(id=userid))
                lcp = lc.dumps()
                xx = LoginCommand.loads(lcp)
                print(xx.cmd)
                await converse.send(lcp)
                while True:
                    try:
                        mes = await converse.receive()
                        # await converse.receive()
                        print('{time}-Client receive: {rec}'
                              .format(time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), rec=mes.decode()))
                        # await converse.writer.drain()
                    except (asyncio.IncompleteReadError, ConnectionError) as ex:
                        print(ex)
                        asyncio.sleep(5)
        except Exception as e:
            print(e)
            await asyncio.sleep(5)
            # await startup(uri)


async def main():
    # remote = 'ws://182.92.191.41:80?username=abc&password=123'
    # remote = 'wss://yun.ydtg.com.cn?username=abc&password=123'
    remote = 'ws://182.92.191.41:8888?username=abc&password=123'
    await asyncio.gather(return_exceptions=True, *(startup(remote) for _ in range(1)))


def exit1(signum, frame):
    print('You choose to stop me.')
    exit()


if __name__ == "__main__":

    signal.signal(signal.SIGINT, exit1)
    signal.signal(signal.SIGTERM, exit1)
    try:
        uvloop.install()
        asyncio.run(main())
    except Exception as e:
        print(e)
    finally:
        print("process exit!!")
