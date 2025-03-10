from bleak import BleakClient, BleakScanner
import asyncio

class BLEDevice:
    def __init__(self, device_name):
        """
        :param device_name: Name of the BLE device to connect to
        """
        self.device_name = device_name
        self.char_read_uuid = "87654321-4321-8765-4321-abcdef987654"
        self.client = None
        self.message_queue = asyncio.Queue()

    async def notification_handler(self, sender, data):
        """
        This function is called whenever a notification is received.
        :param sender: The handle of the characteristic that sent the notification
        :param data: The data received as bytes
        """
        print(f"Received Data from {sender}: {data.decode('utf-8')}")

    async def connect(self):
        """
        Connect to the BLE device and start listening for notifications.
        """
        # Scan for devices
        print("Scanning for devices...")
        devices = await BleakScanner.discover()
        target_device = None

        for device in devices:
            print(device.name)
            if device.name == self.device_name:
                target_device = device
                print(f"Found {self.device_name}: {device.address}")
                break

        if not target_device:
            print(f"{self.device_name} not found. Exiting.")
            return None

        # Connect to the device
        client = BleakClient(target_device.address)
        await client.connect()

        if client.is_connected:
            print(f"Connected to {self.device_name} ({target_device.address})")
            self.client = client
            return client
        else:
            print("Failed to connect.")
            return None

    async def listen_and_send(self):
        """
        Maintain connection and handle sending messages in a queue.
        """
        client = await self.connect()
        if not client:
            return

        try:
            print("Subscribing to notifications...")
            await client.start_notify(self.char_read_uuid, self.notification_handler)

            print("Discovering services and characteristics...")
            for service in client.services:
                print(f"Service: {service.uuid}")
                for char in service.characteristics:
                    print(f"Characteristic: {char.uuid}, Properties: {char.properties}")

            while True:
                message = await self.message_queue.get()
                if message is None:
                    break

                print(f"Sending data: {message}")
                await client.write_gatt_char(self.char_read_uuid, message.encode('utf-8'))
                self.message_queue.task_done()

        finally:
            await client.disconnect()
            print("Disconnected from device.")

    def send(self, message):
        """
        Add a message to the queue to be sent to the device.
        :param message: The message to send.
        """
        self.message_queue.put_nowait(message)

    def run(self):
        """
        Start the event loop to maintain connection and process messages.
        """
        asyncio.run(self.listen_and_send())

