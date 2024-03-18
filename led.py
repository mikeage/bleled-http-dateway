# pylint: disable=missing-function-docstring
import asyncio
import logging
import os

from bleak import BleakClient
from quart import Quart

if os.getenv("VERBOSE"):
    logLevel = logging.DEBUG
else:
    logLevel = logging.INFO

logging.basicConfig(level=logLevel)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

BLE_ADDRESS = os.getenv("BLE_ADDRESS")
assert BLE_ADDRESS

BLEDOM_CHARACTERISTIC = "0000fff3-0000-1000-8000-00805f9b34fb"


class BleLedDevice:
    def __init__(self, peripheral, characteristics):
        self.peripheral = peripheral
        self.characteristics = characteristics

    @staticmethod
    async def new(bt_client: BleakClient) -> "BleLedDevice":
        characteristics = []
        for service in bt_client.services:
            for characteristic in service.characteristics:
                if characteristic.uuid == BLEDOM_CHARACTERISTIC:
                    characteristics.append(characteristic)

        device = BleLedDevice(bt_client, characteristics)
        # await device.sync_time()
        # await device.power_on()
        return device

    def _characteristic(self):
        return self.characteristics[0]

    async def power_on(self):
        await self.generic_command(0x04, 0xF0, 0x00, 0x01, 0xFF)

    async def power_off(self):
        await self.generic_command(0x04, 0x00, 0x00, 0x00, 0xFF)

    async def set_color(self, red: int, green: int, blue: int):
        await self.generic_command(0x05, 0x03, red, green, blue)

    async def set_brightness(self, value: int):
        await self.generic_command(0x01, min(value, 100), 0, 0, 0)

    async def generic_command(self, id: int, arg0: int = 0x00, arg1: int = 0x00, arg2: int = 0x00, arg3: int = 0x00, arg4: int = 0x00):
        data = bytearray([0x7E, 0x00,
                          id, arg0, arg1, arg2, arg3, arg4,
                          0xEF])

        logger.debug("sending message %s", list(data))
        await self.peripheral.write_gatt_char(self._characteristic(), data)


device = None
logger.info("Starting async app")
app = Quart(__name__)
logger.info("Running")


@app.route("/brightness/<brightness>")
async def set_brightness(brightness):
    brightness = int(brightness)
    logger.info("Setting %s to %s%% brightness", device, brightness)
    await device.set_brightness(brightness)
    return ""

@app.route("/color/<rgb_color>")
async def set_color(rgb_color):
    logger.info("Setting %s to 0x%s%%", device, rgb_color)
    if rgb_color.startswith('#'):
        rgb_color = rgb_color[1:] 
    assert len(rgb_color) == 6
    r = int(rgb_color[0:2], 16)
    g = int(rgb_color[2:4], 16)
    b = int(rgb_color[4:6], 16)
    await device.set_color(r, g, b)
    return ""
    
@app.route("/power/<power>")
async def set_power(power):
    logger.info("Turning %s %s", device, power)
    if power == "on":
        await device.power_on()
    elif power == "off":
        await device.power_off()
    else:
        raise AssertionError
    return ""


def disconnected_callback(client):
    logger.warning("Client %s was disconnected", client)


@app.before_serving
async def main():
    logger.debug("In main")
    client = BleakClient(BLE_ADDRESS)
    await client.connect()
    logger.debug("Connected")

    global device
    device = await BleLedDevice.new(client)
    logger.debug("Device assigned (%s)", device)

    return ""
    # logger.debug("Powering off")
    # await device.power_off()
    # logger.debug("Powered off")
    # await device.power_on()
    # # for i in range(10):
    # # await device.set_color(int(i*10*255/100),0,0)
    # # await asyncio.sleep(1)
    # # await device.set_color(128,64,192)
    # await device.set_color(int(1*10*255/100),0,0)
    # # for i in range(10):
    # # await device.set_brightness(10*i)
    # # await asyncio.sleep(1)
    # await device.set_brightness(10)
    # await asyncio.sleep(1)
    # await device.set_brightness(100)
    # await asyncio.sleep(1)
    # await device.set_color(int(10*10*255/100),0,0)
    # await asyncio.sleep(1)
    # await device.set_brightness(10)
    # await asyncio.sleep(1)
    # await device.set_brightness(100)
    # await asyncio.sleep(1)

    # await device.power_off()


# app.run()
# asyncio.run(main())
