import struct
from bleak import BleakClient, BleakScanner
from collections import deque

sliding_window = deque(maxlen=20)
name_map = {"p1": "player_1", "p2": "player_2"}
device = None
async def connect_arduino(player, macos_use_bdaddr=False):
    name = name_map[player]
    print(f"starting scan for device {name}...")

    device = await BleakScanner.find_device_by_name(
        name, cb=dict(use_bdaddr=macos_use_bdaddr)
    )
    if device is None:
        print(f"could not find device with name {name}")
        return

    print(f"connecting to device {device}...")
    return device

async def read_imu(device):
    async with BleakClient(device) as client:
        global sliding_window
        while True:
            # name: player_1, characteristic: 00002101-0000-1000-8000-00805f9b34fb
            # name: player_2, characteristic: 
            data = await client.read_gatt_char("00002101-0000-1000-8000-00805f9b34fb")
            data = struct.unpack("f", data)
            sliding_window.append(data)

async def init_imu(player):
    device = await connect_arduino(player)
    await read_imu(device)

async def get_imu():
    return max(sliding_window)