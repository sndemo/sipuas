import argparse
import asyncio
import logging

import aiosip

sip_config = {
    'srv_host': 'xxxxxx',
    'srv_port': '6000',
    'realm': 'XXXXXX',
    'user': 'YYYYYY',
    'pwd': 'ZZZZZZ',
    'local_ip': '0.0.0.0',
    'local_port': 6200
}


async def on_invite(request, message):
    print('Call ringing!')
    dialog = await request.prepare(status_code=100)
    await dialog.reply(message, status_code=180)

    await asyncio.sleep(3)
    await dialog.reply(message, status_code=200)
    print('Call started!')

    async for message in dialog:
        await dialog.reply(message, 200)
        if message.method == 'BYE':
            break


class Dialplan(aiosip.BaseDialplan):

    async def resolve(self, *args, **kwargs):
        await super().resolve(*args, **kwargs)

        if kwargs['method'] == 'INVITE':
            return on_invite


def start(app, protocol):
    app.loop.run_until_complete(
        app.run(
            protocol=protocol,
            local_addr=(sip_config['local_ip'], sip_config['local_port'])))

    print('Serving on {} {}'.format(
        (sip_config['local_ip'], sip_config['local_port']), protocol))

    try:
        app.loop.run_forever()
    except KeyboardInterrupt:
        pass

    print('Closing')
    app.loop.run_until_complete(app.close())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--protocol', default='tcp')
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    app = aiosip.Application(loop=loop, dialplan=Dialplan())

    if args.protocol == 'udp':
        start(app, aiosip.UDP)
    elif args.protocol == 'tcp':
        start(app, aiosip.TCP)
    elif args.protocol == 'ws':
        start(app, aiosip.WS)
    else:
        raise RuntimeError("Unsupported protocol: {}".format(args.protocol))

    loop.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()
