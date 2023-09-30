#!/usr/bin/python3

from exhub.motor import AutoHuberController
import pytest, asyncio

@pytest.fixture
def huber_device():
    return {
        'dev': 'TCPIP::10.0.0.178::1234::SOCKET',
        'rman': '@py'
    }


@pytest.mark.asyncio
async def test_motor(huber_device):
    
    ctrl = await AutoHuberController.create(**huber_device)

    print(f'Axes: {ctrl.num_axes}')
    await asyncio.sleep(3)
    
