#!/usr/bin/python3

class OrthogonalFlagsMap:
    '''
    This is a mapping helper for various flags-to-strings facilities
    (Harp warnings, Harp flags, ...) encoded as a i.e. a bitwise field
    of *several* items. You can iterate through the warnings to reach
    all of them:
    ```
       >>> warn = OrthogonalFlagsMap(HarpWarnings, 0x441)
       >>> [ warn.text(w) for w in warn ]
       [ 'Sync rate is zero', 'Input rate is too high', 'Time span is too small' ]
       >>> warn.INPT_RATE_ZERO
       True
       >>> warn.INPT_RATE_TOO_HIGH
       False
    ```
    '''
    
    def __init__(self, flagsMap, code=None):
        '''
        Initializes the mapper. Parameters:
          - `code`: This is a bitwise field of flags that this instance represents.
          - `flagsMap`: This is a dictionary which maps single string keys to
            `(flagMask, flagDescription)` tuples. The string key part
            is a non-changeable string that describes the flags for all eternity,
            and which the user (or other program layers) can use to access the flag.
            `flagDescription` is a human-readable string which can change, e.g.
            by translation or a more precise specification, and `flagMask` is a bit
            mask that indicates whether the flag is set or not.
        '''
        self.flagsMap = flagsMap
        if code is not None:
            self.recode(code)
    
    def recode(self, code):
        '''
        Resets the code to `code` and returns a reference to self.
        This is to update the active/inactive flags list to the
        ones encoded in `code` without altering the identity of the
        object.
        '''
        self.code = code
        return self

    def __str__(self):
        return str([f for f in self.keys()])

    def __getattr__(self, key):
        return (self.code & self.flagsMap[key][0]) != 0

    def __iter__(self):
        ''' Iterate through all warnings encoded in `self.code`. '''
        for k,v in self.flagsMap.items():
            if (v[0] & self.code) != 0:
                yield k

    def keys(self):
        '''
        Mimic a bit of a `dict`-like interface: return all the HHLIB API
        warning keys that are encoded in `self.code`.
        '''
        for k in self:
            yield k

    def items(self):
        '''
        Mimic a bit more a `dict`-like interface: return all the HHLIB API
        warning keys that are encoded in `self.code`.
        '''
        for k,v in self.flagsMap.items():
            if (v[0] & self.code):
                yield (k, v[1])
    
    def __getitem__(self, flag):
        ''' Another way of reading a flag '''
        return self.__getattr__(flag)

    def text(self, flag):
        '''
        Returns the description text.
        '''
        return self.flagsMap.get(flag, None)[1]

    def mask(self, flag):
        '''
        Returns the numerical mask value.
        '''
        return self.flagsMap.get(flag, None)[0]

    def __len__(self):
        return len([i for i in self.items()])


AxisStatusFlags = {
    'READY':       (0x0001, "Axis ready"),
    'REF_OK':      (0x0002, "Reference position installed"),
    'LIMIT_NEG':   (0x0004, "Negative limit switch active"),
    'LIMIT_POS':   (0x0008, "Positive limit switch active"),
    'HOMED':       (0x0010, "Axis homed / initialized"),
    'ENABLED':     (0x0020, "Axis enabled"),
    'BUSY':        (0x0040, "Execution in progress"),
    'IDLE':        (0x0080, "Controller idle / all axes stopped"),
    'OSCILLATING': (0x0100, "Oscillation in progress"),
    'OSC_ERROR':   (0x0200, "Oscillation error"),
    'ENC_REF_OK':  (0x0400, "Encoder reference installed"),
    
    'LIMIT_SNEG':  (0x1000, "Negative soft limit"),
    'LIMIT_SPOS':  (0x2000, "Positive soft limit"),
    'BLOCKED':     (0x4000, "Controller blocked"),
    'ERROR':       (0x8000, "Error message pending"),
    'EXT_STOP':   (0x10000, "External stop active")
}
