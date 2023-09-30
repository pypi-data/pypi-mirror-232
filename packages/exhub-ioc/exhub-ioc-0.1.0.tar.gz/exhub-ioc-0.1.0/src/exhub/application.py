#!/usr/bin/python3

#from emmi.scpi import MagicHuber

from caproto.asyncio.server import run as ca_run
from caproto.asyncio.server import start_server, Context
#import caproto as ca

from exhub.motor import AutoHuberController
from exhub.ioc import HuberIoc

import logging, asyncio, random

from os import environ

class Application:
    
    def __init__(self, prefix, dev=None, rman=None, args=None):
        
        if args is None:
            args = []

        self.prefix = prefix
        
        self.huber_device = dict(
            dev=dev or environ.get('EXHUB_VISA_DEVICE',
                                   "TCPIP::10.0.0.178::1234::SOCKET"),
            rman=rman or environ.get('EXHUB_VISA_RESOURCE_MANAGER',
                                     "@py"))

        #logging.info(f'Connecting to: {self.huber_device}')

        # for simulation try:
        # self.huber_device = dict(
            #dev="ASRL1::INSTR",
            #rman="tests/visa-sim-huber.yml@sim")
            
        
    async def async_run(self):

        # don't start automatic status query -- we'll do this manually here
        self.huber_ctrl = await AutoHuberController.create(**self.huber_device)
        
        self.ioc = HuberIoc(self.prefix, self.huber_ctrl)
        
        logging.info(f'Starting IOC with {len(self.ioc.full_pvdb)} PVs, list following')
        
        for pv in self.ioc.full_pvdb:
            logging.info(f"  {pv}")
            
        #await start_server(self.ioc.pvdb)
        
        ctx = Context(self.ioc.full_pvdb)
        asyncio.create_task(ctx.run())

        try:
            period=float(environ.get('EXHUB_POLL_PERIOD', '0.2'))
        except Exception as e:
            logging.error(f"Don't understand EXHUB_POLL_PERIOD="f
                          f"{environ.get('EXHUB_POLL_PERIOD', '0.2')}".
                          f" Defaulting to 0.2 seconds.")
            period=0.2

        return await self.ioc.status_update_loop(period=period)
        
        
def main():

    logging.basicConfig(level={
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "WARN": logging.WARNING,
    }[environ.get('EXHUB_LOG_LEVEL', 'INFO').upper()])

    prefix = environ.get('EXHUB_PREFIX',
                         'SMC:'+random.choice([
                             'Doc', 'Grumpy', 'Happy', 'Sleepy',
                             'Bashful', 'Sneezy', 'Dopey' ])+":")

    logging.info(f'Prefix: {prefix}')
    
    
    app = Application(prefix=prefix)
    asyncio.run(app.async_run())


if __name__ == "__main__":
    main()
