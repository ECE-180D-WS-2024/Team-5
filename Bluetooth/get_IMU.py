import argparse
import asyncio
import logging
import time
import struct
from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic
from collections import deque
import socket
import threading
import argparse

# Set up argument parsing
parser = argparse.ArgumentParser(description="Process player argument.")
parser.add_argument(
    "--player",
    type=str,
    choices=["p1", "p2"],
    required=True,
    help="Player identifier (p1 or p2)",
)
args = parser.parse_args()

# Now you can use args.player to access the "player" variable
player = args.player
print(f"Player set to: {player}")

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

if player == "p1":
    # Server address and port
    server_address = ("127.0.0.1", 5000)  # Example port, change as needed
else:
    # Server address and port
    server_address = ("127.0.0.1", 6000)  # Example port, change as needed

sliding_window = deque(maxlen=20)

async def connect_arduino(name="player_1", macos_use_bdaddr=False):
    print("starting scan...")

    device = await BleakScanner.find_device_by_name(
        name, cb=dict(use_bdaddr=macos_use_bdaddr)
    )
    if device is None:
        print("could not find device with name '%s'", name)
        return

    print("connecting to device...")
    print(device)
    return device

async def read_imu(user_input, device):
    async with BleakClient(device) as client:
        global sliding_window
        while True:
            # name: player_1, characteristic: 00002101-0000-1000-8000-00805f9b34fb
            # 
            data = await client.read_gatt_char("00002101-0000-1000-8000-00805f9b34fb")
            data = struct.unpack("f", data)
            user_input = data
            sliding_window.append(user_input)
            #await asyncio.sleep(0.1)

def send_message(message):
    message = f"{player}-{message}"
    try:
        print(f"Sending: {message}")
        sent = sock.sendto(message.encode(), server_address)
    except Exception as e:
        print(e)

async def run():
    user_input = 0
    device = await connect_arduino()
    await read_imu(user_input, device)
    
    print(sliding_window)
    max_value = max(sliding_window)
    
    #message = "maxAcc" + max_value
    #send_message(message)
    

if __name__ == "__main__":
    while True:
        try:
            asyncio.run(run())
        except:
            pass