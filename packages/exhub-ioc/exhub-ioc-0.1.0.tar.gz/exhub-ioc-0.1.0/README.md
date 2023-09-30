Pure-Python EPICS-IOC for the Huber SMC motion controller
=========================================================

Why & how?
----------

[EPICS](https://epics-controls.org/) is a distributed control and
state representation system for large-scale experimental and industrial
facilities.

[Huber](https://www.xhuber.com/) is a vendor of electronic equipment
whose products, in particular its SMC 9000 / SMC 9300 series motion
controllers, often end up in large-scale experimental and industrial
facilities.

It comes as a no-brainer that the Huber controllers need an EPICS IOC ;-)

Exhub is written purely in Python and does not depend on C code.
It uses [caproto](https://github.com/caproto/caproto)
for all its EPICS communications infrastructure.

Since Exhub aims for testability on a number of levels, including "dry runs"
without actual attached hardware, it uses the EDA motor model of
[EMMI](https://gitlab.com/codedump2/emmi) to provide a simple, but fully
functional, "simulation mode".

Installation
------------

You install Exhub directly from PyPI:
```
pip install exhub-ioc
```

Or you can download the sources from Gitlab and install it locally:
```
git clone https://gitlab.com/codedump2/exhub
pip intall ./exhub
```

If you feel inclined to develop on Exhub, you surely know that you
can use the `-e` option to install an "editable" version instead:
```
pip install -e ./exhub[test]
```

Operation
---------

### On live Huber controller hardware

The only thing Exhub absolutely requires for operation and can't provide
useful defaults for is the connection to your Huber controller. It uses
[PyVISA](https://github.com/pyvisa/pyvisa) for connection, so simply
running `exhub-ioc` with a PyVISA connection should yield a usable IOC:

```
export EXHUB_VISA_DEVICE="TCPIP::10.0.0.7::1234::SOCKET"
exhub-ioc
```

This connects to the controller that has IP address `10.0.0.7`, on port
`1234` (apparently a standad port for Huber controllers). The output should
be similar to this:
```
INFO:root:Prefix: SMC:Grumpy:
INFO:root:Connecting to TCPIP::10.0.0.7::1234::SOCKET via @py
INFO:root:Huber SMC Version: (1, 2, 26)
INFO:root:Starting IOC with 60 PVs, list following
INFO:root:  SMC:Grumpy:tthR_VAL
INFO:root:  SMC:Grumpy:tthR_RBV                                                                                                                  
...
INFO:root:  SMC:Grumpy:thR_VAL
...
INFO:root:  SMC:Grumpy:mag_VAL
...
INFO:root:  SMC:Grumpy:z_VAL
...
NFO:caproto.ctx:Asyncio server starting up...
INFO:caproto.ctx:Listening on 0.0.0.0:5064
INFO:caproto.ctx:Server startup complete.
```

By default, Exhub will choose one of a few predefined EPCIS prefixes for you
(in this case "SMC:Grumpy:...") and will proceed to create process variables
(PVs) for every axis it finds. If available, as in this case, it will use
the axis aliases configured within the controller
(here: `"tthR"`, `"thR"`, `"mag"` and `"z"`) and build the PV suffixes based
on those. It supports the following variables from the
[EPICS motor record](https://epics.anl.gov/bcda/synApps/motor/index.html):

  - `..._VAL` and `..._RBV`: position setpoint and read-back value
  - `..._RLV`: setpoint for relative movement
  - `..._HLS`, `..._LLS`: high and low limit switch indicators
  - `...DMOV`: the "done moving" indicator
  - `...STOP`: motor halt instruction
  
In addition to this, in an attempt to be compatible with SPEC, it exports,
but doesn't populate, the following EPICS motor record suffixes:
`ACCL`, `BDST`, `BVAL`, `VBAS`, `ERES`, `MRES`, `UEIP` and `VELO`. All
values of these fields are zero, and everything written to them is 
being ignored. At this point, SPEC compatiblity is regarded as a
"best effort" enterprising, not a top priority (...good luck though! :-p)

Exhub also reacts to the following environment variables:

  - `EXHUB_VISA_RESOURCE_MANAGER`: indicates the VISA resource manager to use,
    and defaults to `"@py"`. Shouldn't need to be changed unless you *really*
	know what you're doing.
	
  - `EXHUB_PREFIX`: the EPICS prefix to use for the exported PVs. If you
    intend to use colon separation between the prefix and the variable
	suffixes, you need to include it here. For instance:
	```
	export EXHUB_PREFIX="KMC3:MOTION:"
	```
	will yield you variables named `"KMC3:MOTION:thR_VAL"`, `"KMC3:MOTION:z_VAL"`
	and so on.
	
	(Also note that the motor record suffix is separated by the rest of the
	PV name by an underscore `"_"`; this is non-configurable).
	
  - `EXHUB_POLL_PERIOD`: information from the Huber controller is polled in
	regular intervals (by default every 0.2 seconds). You can use this variable
	to adjust that interval.
	
  - `EXHUB_LOG_LEVEL`: can be one of `DEBUG`, `INFO`, `ERROR`, or `WARNING`
    and sets the Python logger level. Defaults to behavior of `INFO`, which
	prints useful information on startup (mostly about exported/auto-generated
	PVs) but is quiet during operation, unless something unexpected happens
	that the user should be made aware of.
	
  - `EXHUB_IOC_TEST`: if this is set to `"yes"` or `1`, then any real Huber
    hardware is ingored and a mock-up, purely software-based, set of motors
	is used. Then a number of other variables can also be used.
	See [Operation in simulation mode](#in-simulation-mode) below.
  
### In simulation mode

Exhub can be forced to run in a functional, pure-software simulation mode.
"Functional" here means that the motors, indeed, display "kind-of useful"
behavior when instructed to move or stop, or bump against simulated limit
switches. To do this, use the `EXHUB_IOC_TEST` environment variable set to
`"yes"`:
```
export EXHUB_IOC_TEST=yes
exhub-ioc
```

This will result in a simple single-motor simulator:
```
INFO:root:Prefix: SMC:Doc:
INFO:root:Mock-huber: ['mock:-1:+1']
INFO:root:Starting IOC with 15 PVs, list following
INFO:root:  SMC:Doc:mock_VAL
INFO:root:  SMC:Doc:mock_RBV
INFO:root:  SMC:Doc:mock_RLV
INFO:root:  SMC:Doc:mock_HLS
INFO:root:  SMC:Doc:mock_LLS
INFO:root:  SMC:Doc:mock_DMOV
INFO:root:  SMC:Doc:mock_STOP
INFO:root:  SMC:Doc:mock_ACCL
INFO:root:  SMC:Doc:mock_BDST
INFO:root:  SMC:Doc:mock_BVAL
INFO:root:  SMC:Doc:mock_VBAS
INFO:root:  SMC:Doc:mock_ERES
INFO:root:  SMC:Doc:mock_MRES
INFO:root:  SMC:Doc:mock_UEIP
INFO:root:  SMC:Doc:mock_VELO
INFO:caproto.ctx:Asyncio server starting up...
INFO:caproto.ctx:Listening on 0.0.0.0:5064
INFO:caproto.ctx:Server startup complete.
```

The prefix here has been randomly chosen to be `"SMC:Doc:..."`. See above 
[Operation on live controllers](#on-live-huber-controller-hardware)
for a full description of the environment variables -- most of them
make sense and can also be used in the simulation mode.

To simulate additional axes/motors, or to adjust the simulated limit
switches (by default set at -10/+10), use the `EXHUB_MOCK_HUBER`
variable. It takes a string of the form
`"name1:low1:hi1;[name2:low2:hi2;[name3...]]"`, where:
  - `"name..."` is a string label by which to address the motor, akin to
    a Huber axis alias
  - `"low..."` is the value of a low-limit switch, and
  - `"hi..."` is the value of a high-limit switch.
  
Examples:

  - `"EXHUB_MOCK_HUBER=mock:-10:10"` will cause the default behavior.
  
  - `"EXHUB_MOCK_HUBER=x:-7:7;y:-8:8;z:-9:9"` will simulate a device
	with three axes (`"x"`, `"y"` and `"z"`), limited at +/-7, 8 and 9,
	respectively.

Of course, technically Exhub will also accept pyVISA-sim kind of simulations
(set up via the `EXHUB_VISA...` variables). But in practice, the Huber SMC
protocol is very convoluted in its details, and full of exceptions and
special cases. With only light effort we haven't succeeded in fully simulating
that. If you wish to exert a medium-to-heavy amount of work, we'd be very
interested in the results.

The mock-Huber part of the simulation bypasses all the VISA connection
and polling code (which otherwise is done asynchronously, using `asyncio`).
However, it travereses in a regular manner all the rest -- i.e. the IOC and
application logic. It can be used to test higher aspects of the IOC behavior,
and can definitely be used to serve for integration testing of components
higher up in the architecture stack. In fact, this is one of the core
motivations behind Exhub.


Deployment
----------

Installation via PyPI (`pip install ...`) should get you a usable application.
As all configuration is done via environment variables instead of local
files, deployment as a service (e.g. via systemd) should be fairly standard.

However, the way we prefer to deploy Exhub is through a Podman (or Docker)
container. For this, the root folder of Exhub's Git project
[over at Gitlab](https://gitlab.com/codedump2/exhub) contains a `Dockerfile`
which you can use right away. The Dockerfile doesn't pull its Exhub
from PyPI or Gitlab; instead it allows you to use your own, local copy
of Exhub when creating a container. For instance like this:
```
cd /tmp
git clone https://gitlab.com/codedump2/exhub
podman build -t exhub-ioc -f /tmp/exhub/Dockerfile -v /tmp/exhub:/exhub-src:z
```

Running Exhub from its container is straight forward, e.g. in its default
simulation mode:
```
podman run -ti --rm \
    --name=exhub \
	--publish 5064-5065/tcp \
	--publish 5064-5065/udp \
	-e EXHUB_MOCK_TEST=yes \
	localhost/exhub-ioc:latest
```

The ports 5064 and 5065 tcp/udp apparently are needed by the EPICS CA-protocol
for communication. If you are running only one IOC container on your host,
the above should do. If you're trying to run several, every container started
after the first one will, of course, fail to bind to 5064 and/or 5065.

You have two options:

  - start all your IOC containers with `--net=host`, so they can at least
    [collaboratively use](https://caproto.github.io/caproto/v1.1.0/servers.html#running-multiple-servers-on-one-host)
	the UDP broadcast port, or
	
  - try a dedicated EPICS `caRepeater` on the host, and have all the
    container IOCs broadcast their PVs through that repeater.


Other implementations
---------------------

There already exists an
[EPICS driver package](https://www.xhuber.com/fileadmin/user_upload/downloads/software/Huber_EPICS_package.zip) for the SMC-9300 series, and
possibly for other models at
[Huber's service website](https://www.xhuber.com/en/service/). If that
fits your bill, go ahead and use it.

In any case you're welcome to try Exhub!

The main differences are:

  - *Core functionality:* Exhub focuses directly on controlling
    motion of the attached axes in the most direct and compatible
	way possible. As such, it exports a small, but useful subset of
	the
	[EPICS motor record](https://epics.anl.gov/bcda/synApps/motor/index.html)
	process variables only. It tries to hide details of the underlying
	hardware if those aren't directly required for motion operation.
	Setting up the controller hardware to "behave
	properly" is not the scope of the IOC; it should be done by the user
	in advance, by other means.
	
	The Huber package, in contrast, exposes internal architectural details
	specific to the Huber controllers into PVs. Motion control is done in
	a proprietary manner through specialized variables.
	
  - *Application scope:* Exhub is kept as general and application-agnostic
	as possible. It's an out-of-the-box EPICS IOC for Huber controller.
	For instance it autodetects and supports *all* axes exposed by a
	controller.
	
	The Huber package appears (as of September 2023) to have been designed
	and implemented for a specific application, and has undergone very
	limited efforts towards generalized extension.
	
  - *Testability:* One of the main goals in Exhub development was 
	testability -- both of the "live" code on a controller (threre are
	some Python unit tests which can be executed on live hardware), and
	for "dry runs", using a simulated motor model instead of a live
	controller. Exhub is used in CI/CD setups for experimental physics
	beamline endstations.
	
	The Huber package focuses solely on manual operation on live hardware.
	
  - *Documentation:* Last, but not least, we try to make Exhub more
	accessible by providing useful documentation.

Bugs
----

If you find any, you're free to keep them!
Apparently some people eat those. :-p
