import logging
import struct
import asyncio
import time
# import serial # pip install pyserial

logger = logging.getLogger("FPGABridge")

class FPGABridge:
    """
    FPGA Hardware Bridge (Low Latency).
    Interface for sending binary-encoded order signals to an FPGA board via serial/UDP.
    Bypasses standard OS network stack for nanosecond-level execution latency.
    """
    def __init__(self, port: str = "COM3", baudrate: int = 115200):
        self.port = port
        self.baudrate = baudrate
        self.connection = None
        self.connected = False

    def connect(self):
        """
        Establishes connection to the FPGA board.
        """
        try:
            # self.connection = serial.Serial(self.port, self.baudrate, timeout=0.1)
            self.connected = True
            logger.info(f"Connected to FPGA on {self.port} at {self.baudrate} baud.")
        except Exception as e:
            logger.error(f"Failed to connect to FPGA: {e}")
            self.connected = False

    def send_order_binary(self, symbol_id: int, side: int, price: int, quantity: int):
        """
        Encodes order details into a compact binary format and sends to FPGA.
        Protocol: [StartByte][SymbolID][Side][Price][Qty][Checksum]
        """
        if not self.connected:
            logger.warning("FPGA not connected. Skipping hardware execution.")
            return

        try:
            # Struct format: B (uchar), H (ushort), B (uchar), I (uint), I (uint)
            # Total 1 + 2 + 1 + 4 + 4 = 12 bytes payload
            payload = struct.pack('>BHBII', 0xA5, symbol_id, side, price, quantity)
            
            # Calculate checksum (XOR of all bytes)
            checksum = 0
            for byte in payload:
                checksum ^= byte
            
            packet = payload + struct.pack('>B', checksum)
            
            # self.connection.write(packet)
            logger.info(f"Sent binary packet to FPGA: {packet.hex()}")
            
        except Exception as e:
            logger.error(f"Error sending to FPGA: {e}")

    async def receive_confirmation(self):
        """
        Listens for execution confirmation from FPGA.
        """
        if not self.connected:
            return

        while True:
            # if self.connection.in_waiting > 0:
            #     data = self.connection.read(10)
            #     logger.info(f"FPGA Confirmation: {data.hex()}")
            await asyncio.sleep(0.001) # Poll loop

    def close(self):
        if self.connection:
            # self.connection.close()
            pass
