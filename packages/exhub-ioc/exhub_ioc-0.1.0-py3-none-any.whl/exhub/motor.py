#!/usr/bin/python3

import pyvisa, logging, asyncio, time
from parse import parse

from exhub.flags import OrthogonalFlagsMap, AxisStatusFlags
from pprint import pprint

class HuberMotor:
    ''' `emmi.eda` compatible motor for a Huber controller.

    This gives comfortable access to a single motor, but for performance
    reasons it actually depends on the collector class `HuberController`,
    which monitors and queries all the motors of a specific controllers
    using aggregate commands of the Huber SMC protocol.
    '''

    def __init__(self, ax, ctrl):
        ''' Initializes individual access to axis `ax` via HuberController `ctrl`. '''
        self.axis = ax
        self.ctrl = ctrl
        self._latest_s_obj = OrthogonalFlagsMap(AxisStatusFlags)
    
    def where(self):
        '''
        Returns current position -- that is the position that we'd be currently
        having if we'd wanted to go from "current" towards "target" within
        the timeslice "mock_timeslice"
        '''
        return self._latest_status['pos']


    def goto(self, val):
        ''' Sends command to move to absolute position (doesn't wait). '''
        self._huber_exec(f'goto{self.axis}:{val}')
        

    def stop(self):
        ''' Sends command to stop (doesn't wait). '''
        self._huber_exec(f'q{self.axis}')


    def moves(self):
        ''' Returns True if the motor moves. '''
        return (not self._latest_s.READY)


    def clear(self):
        '''
        Clears all outstanding error flags (they may pop up again).
        '''
        self._huber_exec(f'cerr{self.axis}')

    @property
    def flags(self):
        return self._latest_s

    @property
    def errors(self):
        if self.flags.ERROR:
            return [self._latest_status['err'], ]
        return []
        
    #
    # Extensions beyond EMMI EDA API -- only for local use!
    #

    @property
    def _latest_s(self):
        self._latest_s_obj.recode(self._latest_status['sbits'])
        return self._latest_s_obj

    def _huber_exec(self, cmd):
        # Executes a huber command on self.ctrl and checks for transmission errors.
        l = self.ctrl.huber.write(cmd)
        if l < len(cmd)+len(self.ctrl.huber.write_termination):
            msg = f'Axis {self.axis}: "goto" failed (length: {l})'
            logging.error(msg)
            raise RuntimeError(msg)

    @property
    def _latest_status(self):
        return self.ctrl.latest_status[self.axis]

    
class HuberHeloError(RuntimeError):
    pass

class HuberTimeoutError(RuntimeError):
    pass

class HuberController:
    ''' Encapsulates aggregate access to axes status & control on a Huber SMC controller.
    '''

    @classmethod
    async def create(Class, dev=None, rman=None):
        ''' Initializes a HuberController asynchronously.

        Initializing a `HuberController` involves reading out the
        "Hello" string and version, which, for robustness reaons,
        is done in a time-consuming matter. We do this asynchronously,
        which is why we can't do this in __init__() and have to
        put it in `create()` instead.
        '''

        self = Class()
        
        # useful for reconnecting on errors=
        self.param_dev = dev
        self.param_rman = rman or "@py"
        self.huber = None
        self.huber_lock = asyncio.Lock()

        logging.info(f"Connecting to {dev} via {rman}")

        self.huber = await self._init_device(self.param_dev, self.param_rman)
        await self._init_axes(self.huber)
        
        return self


    async def _huber_get_config(self, num_axes):
        # Executes a '?conf' query.
        # Returns a dictionary of config parameters, empty lines and
        # commented lines removed.

        expect_lines = None
        
        async with self.huber_lock:
            
            l = self.huber.write('?conf')
            if l < len(self.huber.write_termination)+5:
                raise RuntimeError(f'Huber write error for "?conf"')

            # This is a tricky one: there will be `num_axes` sets of configuration
            # lines (one for each axis) separated by double-\r\n, but the final
            # set only has one single final \r\n.
            #
            # There are two ways of knowing when the final set is finished. One is
            # by counting the expected number of lines (which is tricky to determine
            # -- we'd have to start with an unknown number, then assume that there
            # are at least two axes present, and learn from the first set the number
            # of lines to expect from every other set.
            #
            # The other is by simply waiting for timeout.

            config = {}

            for x in range(1, num_axes+1):
                lines = await self._huber_read(self.huber, timeout=0.2,
                                               separator='\r\n', end='\r\n\r\n')

                if lines[0][0] != '#':
                    raise RuntimeError(f'Expected axis configuration block, '
                                       f'received {lines[0]}')

                axconf = {}
                for l in lines:
                    if len(l) == 0 or l[0] == '#':
                        continue
                    k, v = l.split(':')
                    axconf[k[:len(k)-len(f'{x}')]] = v

                config[x] = axconf
            
        return config


    async def _init_axes(self, huber):
        # Initializes the axes logics.
        # Most important part is to determine the number of axes counts
        # and create a motor class for each axis.
        #
        # Each motor has a numerical ID (the same by which it is known within
        # the Huber controller) and a human-readable name (also known from
        # the Huber controller).

        
        axes = await self._huber_query('?s', separator=';', parser=lambda s: s)
        self.num_axes = len(axes)

        # Try to use smart names of the Huber config; if that fails,
        # we'll just use the stringified axis ID as axis name.
        axis_alias = lambda ax, conf: \
            (conf if conf is not None else {}).get('alias', f'{ax}').split('~')[0]        
        try:
            self._axes_config = await self._huber_get_config(self.num_axes)
        except RuntimeError as e:
            logging.error(f'Cannot determine axis config / alias: {e}')
            self._axes_config = None
        
        self.motors = { axis_alias(x, c): HuberMotor(x, self)
                        for x, c in self._axes_config.items() }


    async def _init_device(self, dev=None, rman=None):
        self._rman = pyvisa.ResourceManager(rman)
        huber = self._rman.open_resource(dev)
        huber.write_termination = '\r\n'
        huber.read_termination = '\r\n'
        huber.timeout = 0
        
        async with self.huber_lock:
            self.smc_version = await self._handle_hello(huber)

        logging.info(f'Huber SMC Version: {self.smc_version}')

        # Just to be sure -- we don't now what "2" will be.
        # We possibly need to change this.
        assert self.smc_version[0] == 1
        assert len(self.smc_version) == 3

        return huber


    async def _handle_hello(self, huber, timeout=1.0):
        # Consume Huber's "Hello" until we run into timeout.
        # This is because we don't (yet) know exactly the termination.
        # The Hello should countain the SMC version (which we return
        # if it looks sane).
        #
        # Finally, we set the termination to a defined \r\n ("txdel3")
        
        logging.debug(f"Waiting for complete Hello (timeout: {timeout} seconds)...")
        
        helo = await self._huber_read(huber, timeout=1.0, end=None)

        logging.debug(f'Hello received: {helo}')
        v = parse('smc {:d}.{:d}.{:d}{ignore}', helo.decode('utf-8'))

        if v is None:
            logging.error(f'Cannot determine SMC version from {helo}')
            raise HuberHeloError(f'Cannot determine SMC version from {helo}')

        nr = huber.write('txdel3')
        assert nr == len(huber.write_termination)+6

        return v.fixed
        

    async def connect(self):
        if self.huber is not None:
            try:
                self._rman.close()                
                self.huber.close()
            except Exception as e:
                logging.warning(f'Disconnect: {e}')
        await self._init_device(self.param_dev, self.param_rman)


    def _smc_format_by_version(self, version):
        # This is a tricky way to account for different SMC versions.
        # For every command we use here (and need to parse the result of)
        # we put an entry into 'fmt', containing the format string as used
        # by `parse.parse()`.
        #
        fmt = {}

        # ?s
        fmt['s'] = '{ax:d}:{sbits:d}'

        # ?p
        fmt['p'] = '{ax:d}:{pos}' ## parsing 'pos' as float will fail if pos is "0"

        # ?status: This one's tricky.
        if version == (1, 1, 165):
            fmt['status'] = '{ax:d}:{data:s}'
            
        elif version[0] == 1 and version[1] == 2:
            if version[2] in (26,):
                fmt['status'] = '{ax:d}:{}'

            elif version[2] >= (86,):
                fmt['status'] = '{ax:d}:{}'
                #fmt['status'] = '{ax:d}:{err}:{errmsg}:{pos:f}:{epos:f}:{lim:d}'\
                #    ':{home:d}:{eref:d}:{rdy:d}:{osc:d}:{oscerr:}:{moving:d}'\
                #    ':{prg:d}:{cfd:d}:{softlim:d}:{blocked:d}{estop:d}'

        else:
            fmt['status'] = '{ax:d}:{}'


        # ?err
        fmt['err'] = "{ax:d}:{err}"

        ## Hard data
        #fmt['s_flags'] = AxisStatusFlags        

        return fmt


    @property
    def _smc_format(self):
        return self._smc_format_by_version(self.smc_version)


    async def _huber_read(self, huber, timeout=None, end='auto', separator=None):
        ''' Async read from an pyVISA device.

        Reads until either `end` is found (if it is not None), or until
        `timeout` seconds have elapsed without any new character.

        Args:
        
            timeout: time in seconds that may elapse, maximum, until
              the read is declared complete. Default of `None` means
              no timeout.

            end: the end marker of reading. If 'auto' is specified,
              the default `self.huber.read_termination` is used. If `None`,
              an end is ignored and reading continues until timeout.

            separator: If not `None`, the incoming string will be separated
              into several parts.

        Returns: a string, or a list of strings.
        '''

        data = b''
        mark = time.time()

        if end == 'auto':
            end = huber.read_termination

        if end is not None:
            _end = end.encode('utf-8')
            
        while True:
            try:
                data += huber.read_raw()
                if (end is not None) and data[-len(_end):] == _end:
                    data = data[:-len(_end)]
                    break

                mark = time.time()

            except pyvisa.errors.VisaIOError as e:
                elapsed = time.time() - mark
                if (timeout is not None) and (elapsed > timeout):
                    if len(data) > 0:
                        break
                    raise HuberTimeoutError(str(e))
                else:
                    # short timeout, not finished yet
                    #print(f'Pausing: {e}, timeout: {timeout}, elapsed: {elapsed}')
                    await asyncio.sleep(0.01)
                    continue

        if separator is not None:
            return [i.strip() for i in data.decode('utf-8').split(separator)]

        return data


    async def _huber_query(self, cmd, return_lines=1, ignore_lines=0,
                          separator=None, parser=None):
        ''' Asynchronously querying the Huber SMC device.

        Most commands return a single line. Some commands return a multi-part
        response with a separator between the parts, and a `read_termination`
        as an end of message. Some return a multi-line (multiple `read_termination`
        occurences).

        We try to deal with all of these.

        Args:
        
            cmd: the command to send

            separator: If specified, this is regarded as the separator
              of message responses.

            return_lines: After how many lines to consider the message complete.
              Useful for muliline messages.

            ignore_lines: Number of additional lines to read (similarly to
              `return_lines`) but not to process.

            parser: Callable to parse the individual items by.
              
        Returns: a list of either string items or parser objects -- one for each
          line / part of a response that is expected.
        '''
        # Dear boys and girls,
        #
        # The SMC data transfer protocol is a fine example of what happens
        # if you program under influence of heavy-duty medication, or
        # excessive recreational drugs.
        #
        # Don't.
        #
        # For instance: some commands return single-lines (terminated by
        # a sequence as reported by the 'txdel' command); some return multi-lines.
        # Of those that return multi-lines, some use \r\n as a line separator
        # (and then 'txdel' as end-of-message marker), and some don't -- they
        # use the 'txdel' as a line separator instead, and then again as
        # end-of-message marker.
        #
        # The result is that we can't trust what comes out on multiline messages,
        # we actually need to implement a line-by-line reader with the
        # expected number of lines.

        async with self.huber_lock:

            nr = self.huber.write(cmd)
            assert nr == len(cmd)+len(self.huber.write_termination)

            data = []

            parse_errors = []

            # Some answers are multiline (i.e. separated by "read_termination").
            # Some are single-line separated by "separator".
            #
            # "parser" always refers to parsing of one element.
            for i in range(return_lines):

                result = await self._huber_read(self.huber, separator=separator)

                if separator is None:
                    assert isinstance(result, bytes)
                    data.append(result.decode('ascii') if parser is None \
                                else parser(result.decode('ascii')))
                else:
                    assert not isinstance(result, str)
                    assert hasattr(result, "__getitem__")
                    for r in result:
                        if len(r) == 0:
                            continue
                        d = r if (len(r) == 0) or (parser is None) else parser(r)
                        if d is None:
                            # Detect parse errors; can't raise an error here because then line
                            # order will get fucked up. We simply increment the erround counter
                            # of doom and bail out... later.    
                            parse_errors.append(f"{cmd}: Don't know what to do with {result}")
                        else:
                            data.append(d)

            for i in range(ignore_lines):
                await self._huber_read(self.huber)

            # ...this is "later".
            if len(parse_errors) > 0:
                for e in parse_errors:
                    logging.error(e)
                raise RuntimeError(f'{cmd} was of a bad breed.')

            return data


    async def status_query(self):
        # Queries current status of all axes.
        #
        # Returns a dictionary with axis ID as keys,
        # and a status dictionary as valye.
        # See ._smc_format_by_version() for status dictionary keys.

        status = {}
        
        for cmdict in (dict(cmd="?s", separator=';'),
                       dict(cmd="?err", return_lines=self.num_axes),
                       dict(cmd="?p", separator=';'),
                       dict(cmd="?status", return_lines=self.num_axes, ignore_lines=1)):

            cmd = cmdict['cmd'][1:]
            
            try:
                
                res = await self._huber_query(**cmdict,
                                              parser = lambda s: parse(self._smc_format[cmd], s))
            except RuntimeError:
                continue
            
            for ax_data in res:
                axis_id = ax_data['ax']
                
                if axis_id not in status:
                    status.setdefault(axis_id, ax_data.named.copy())
                else:
                    status[axis_id].update(ax_data.named)

                # Fixing some parsing peculiarities of 'parse'
                if 'pos' in status[axis_id]:
                    status[axis_id]['pos'] = float(status[axis_id]['pos'])

                # Some temporary extras

                # axis name (string)
                status[axis_id]['name'] = f'AX{axis_id}'


        self.latest_status = status

        return status
    

    def clear_all(self):
        l = self.huber.write('cerr')
        if l != len(self.huber.write_termination)+4:
            raise RuntimeError('Error communicating with Huber (cerr)')


from os import environ
from emmi import eda

class MockHuberController:
    ''' HuberController API compatible mock class, using EMMI EDA MockMotor

    Normally a Huber controller will report its own axes - most importantly
    the number of, aswell as some configuartion details. They also have their
    own limit setups (soft and/or hard limits).

    A mock controller has nothing of that, it needs to be specified by the
    user. But to keep the application oblivious to the mockery, we don't
    want to need to specify any of that via a specific API. We'll collect
    essential axis information through environment variables, starting
    with EXHUB_MOCK_HUBER.
    '''

    @classmethod
    async def create(Class, *args, **kwargs):
        me = Class()

        # Expected format of $MOCK_HUBER env var is "l0:h0;l1:h1;l2:h2;..."
        motors_set = environ.get('EXHUB_MOCK_HUBER', 'mock:-1:+1').split(';')
        mocks = []

        logging.info(f"Mock-huber: {motors_set}")

        for m in motors_set:
            if len(m) == 0:
                logging.warning(f'Mock Huber Motor spec "{m}": don\'t know how to handle')
                continue

            l = m.split(':')
            if len(l) != 3:
                logging.error(f'Mock Huber Motor spec "{m}": bad limits')
                raise HuberHeloError(f'Mock Huber Motor spec "{m}": bad limits')


            mocks.append( (l[0], int(l[-2]), int(l[-1])) )

        
        me.motors = { m[0]: eda.MockMotor(mock_timeslice=1.0,
                                          limits={
                                              'LIMIT_SNEG': m[-2],
                                              'LIMIT_SPOS': m[-1],
                                          }) for m in mocks }
        
        me.num_axes = len(me.motors)
        
        return me

    async def connect(self):
        pass

    async def status_query(self):
        status = {}
        for i,m in enumerate(self.motors.items()):
            status[i+1] = { 'ax': i+1,
                            'name': f'{m[0]}',
                            'sbits': m[1].flags,
                            'pos': m[1].where(),
                            'err': m[1].errors }

        return status

    def clear_all(self):
        pass


#
# A little piece of magic to transparently load either the real huber
# controller, or a test controller 
#
if environ.get('EXHUB_IOC_TEST', None) not in ['yes', 'Yes', 'YES', '1', 'true' ]:
    AutoHuberController = HuberController
else:
    t = environ['EXHUB_IOC_TEST']
    AutoHuberController = MockHuberController
