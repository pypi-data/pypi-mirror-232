#!/usr/bin/python3

from os import environ

#if environ.get('EXHUB_IOC_TEST', None) in ['yes', 'Yes', 'YES', '1', 'true' ]:
#    from exhub.motor import MockHuberController as HuberController
#else:
#    from exhub.motor import HuberController

from exhub.motor import HuberHeloError
from exhub.flags import OrthogonalFlagsMap, AxisStatusFlags
from itertools import chain
from caproto.server import pvproperty, PVGroup
from caproto.server.common import LoopExit

import pyvisa, asyncio, logging

#from parse import parse


class HuberAxisPVGroup(PVGroup):
    ''' PVGroup (i.e. set of EPICS variables) for one Huber motor axis
    '''
    
    VAL  = pvproperty(value=0.0, doc="Position setpoint value")
    RBV  = pvproperty(value=0.0, doc="Position readback value")
    RLV  = pvproperty(value=0.0, doc="Position relative-move setpoint")
    HLS  = pvproperty(value=False, doc="High-limit switch active")
    LLS  = pvproperty(value=False, doc="Low-limit switch active")
    DMOV = pvproperty(value=0, doc="Done-moving")
    STOP = pvproperty(value=0, doc="Stop movement")

    # bogus fields needed for SPEC to recognize this as a motor
    ACCL = pvproperty(value=0.0) # acceleration time in seconds
    BDST = pvproperty(value=0.0) # backlash distance
    BVAL = pvproperty(value=0.0) # backlash velocity
    VBAS = pvproperty(value=0.0) # base velocity (minimum velocity?)
    ERES = pvproperty(value=0.0) # encoder resolution a.k.a. step size
    MRES = pvproperty(value=0.0) # motor resolution a.k.a. step size
    UEIP = pvproperty(value=0.0)
    VELO = pvproperty(value=0.0)

        # SPEC needs the following:
        #
        # Can be ignored / business of the controller?
        #  o ACCL: acceleration time in seconds (0.0)
        #  o BDST: backlash distance egu (0)
        #  o BVAL: backlash velocity egu/s (0)
        #  o VBAS: base velocity (minimum velocity?) egu/s (0)
        #  o ERES: encoder step size egu (0)
        #  o MRES: motor step size egu (0)
        #
        # Calibration fields and coordinate system transformations:
        #  - SET: set/use switch for calibration fields (0: use, 1: set)
        #  - FOFF: offset freeze switch -- is the user prevented from
        #          writing the offset?
        #  - OFF: user offset egu
        #  + DIR: user direction        
        #  - RRBV: raw readback value
        #  - RVAL: raw desired value
        #
        # Unclear:
        #  o UEIP: use encoder if present (always 1?)
        #  o VELO: velocity egu/s (set to 0?)
        #
        # Need to have / already have:
        # <> STOP: stop, 
        # <> VAL: user desired value
        #  - SPMG: stop/pause/move/go -- complicated beast
        #    - Stop: same as STOP?        
        #
        # Nice to have, but not part of the EDA Motor Model:
        #  + DHLM: dial high-limit
        #  + DLLM: dial low-limit
        # <> HLS: at high-limit switch
        # <> LLS: at low-limit switch        
        # <> DMOV: done moving to value
        #
        # Unknown:
        #  + DISP: disable (turn off motor/unusable)        
        #
        # Nice to have, not needed by SPEC:
        #  o EGU: engineering unit names
        # <> RLV: relative-move value: when changed, changes VAL,
        #    then resets itself to 0
        #    
    
    def __init__(self, prefix, motor):
        self.motor = motor
        super().__init__(prefix)


    async def status_update(self):
        # Check the motor for new status data
        if self.motor.where() != self.RBV.value:
            await self.RBV.write(self.motor.where())

        flags = self.motor.flags
        for pv, query in {
                self.HLS:  lambda s: "LIMIT_SPOS"  in s,
                self.LLS:  lambda s: "LIMIT_SNEG"  in s
        }.items():
            await pv.write(query(flags))

        if self.motor.moves() != self.DMOV.value:
            await self.DMOV.write(not self.motor.moves())
    

    @VAL.putter
    async def VAL(self, inst, val):
        self.motor.goto(val)


    @RLV.putter
    async def RLV(self, inst, val):
        if val != 0:
            await self.VAL.write(self.VAL.value+val)
        return 0.0

    @STOP.putter
    async def STOP(self, inst, val):
        if val != 1:
            return

        self.motor.stop()
        while True:
            if not self.motor.moves():
                break
            await asyncio.sleep(0.01)

        await self.VAL.write(self.motor.where())
    
    

class HuberIoc(PVGroup):

    # The update hook
    #update = pvproperty(value=False, record='bi')

    def __init__(self, prefix, huber):
        self._pvdb = {}
        self.huber_ctrl = huber
        
        self.prefix = prefix
        self.axes = []
        
        for name,motor in self.huber_ctrl.motors.items():
            self.axes.append(HuberAxisPVGroup(prefix=prefix+f"{name}_",
                                              motor=motor))

        super().__init__(prefix)


    @property
    def full_pvdb(self):
        # Returns a full PVDB (i.e. our own and that of the motors)
        tmp = self.pvdb
        for x in self.axes:
            tmp.update(x.pvdb)
        return tmp


    #@update.scan(period=0.5, use_scan_field=True)
    #async def update(self, inst, async_lib):
    #    await self.status_update()
        
    async def status_update(self):
        status = await self.huber_ctrl.status_query()
        for stat, axis in zip(status, self.axes):
            await axis.status_update()


    async def status_update_loop(self, period=0.1):
        while True:
            try:
                await self.status_update()
            except (pyvisa.errors.VisaIOError,
                    RuntimeError,
                    pyvisa.errors.InvalidSession) as e:

                logging.error(f'Oops: connection failed with "{e}"')
                logging.error(f'Oops: Traceback follows.')

                import traceback
                traceback.print_exception(e)

                
                # Reconnecting fails. Comment this out to try it out...
                logging.error(f'Oops: exitting now.')
                return
                
                while True:
                    try:
                        logging.info('Trying to reconnect...')
                        await self.huber_ctrl.connect()
                        break
                    except (pyvisa.errors.VisaIOError,
                            pyvisa.errors.InvalidSession,
                            ConnectionRefusedError,
                            HuberHeloError) as e2:
                        logging.error(f'Reconnect failed: {e2}')
                        logging.info("Will try again in 3 seconds...")
                        await asyncio.sleep(3.0)
                logging.info('Have new connection.')
                        
            await asyncio.sleep(period)

