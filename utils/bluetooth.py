import glob
import subprocess
import threading
import time
from enum import Enum
import serial

class ConnectionStatus(Enum):
    """Connection status:
    CONNECTED: When the Odroid can be pinged via SSH.
    OFFLINE: Otherwise."""
    DISCONNECTED = 0
    CONNECTING = 1
    CONNECTED = 2
    ACQUIRING = 3

def hard_bt_reconnect(user_parameters):
    # step one, get the MAC address of the device
    mac_address = get_MAC_address_from_COM_port(user_parameters['address'])

    # step two, forget that MAC address
    forget_bluetooth_device(mac_address)
    time.sleep(0.5)

    connected = False

    while not connected:
        connected = connect_to_device(mac_address)
def get_available_ports(os_type: str):
    # Returns a list of available COM ports
    available_ports = []

    # Windows
    if os_type == 'Windows':
        for i in range(256):
            try:
                ser = serial.Serial("COM{}".format(i))
                if 'ScientISST' in ser.portstr:  # Check if 'ScientISST' is in the port name
                    available_ports.append(ser.portstr)
                ser.close()
            except serial.SerialException:
                pass

    # Linux and MacOS
    elif os_type in ["MacOS", "Linux"]:
        # List all the available serial ports
        ports = glob.glob('/dev/tty.*')
        # + glob.glob('/dev/cu.*')

        for port in ports:
            try:
                ser = serial.Serial(port)
                if 'ScientISST' in ser.portstr:  # Check if 'ScientISST' is in the port name
                    available_ports.append(ser.portstr)
                ser.close()
            except serial.SerialException:
                pass

    # TODO: If something goes wrong, manually add the COM Ports here
    # available_ports.append("my-com-port")

    return available_ports

def reset_BT():
    bt_reset = threading.Thread(target=_reset_BT)
    bt_reset.start()

def _reset_BT():

    # 1) kill BT process and make it come back
    bt_is_back = False

    try:
        kill_bt(password='7734')
        while not bt_is_back:
            time.sleep(0.5)
            bt_is_back = check_bt()
        print("Bluetooth service restarted successfully.")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

def kill_bt(password):
    # This will prompt for the sudo password if not already authenticated
    command = ['pkill', 'bluetoothd']

    p = subprocess.Popen(['sudo', '-S'] + command, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                         universal_newlines=True)

    p.communicate(password + '\n')[1]


def check_bt():
    # Run the command using subprocess
    result = subprocess.run(['system_profiler', 'SPBluetoothDataType'], capture_output=True, text=True)

    # Print the output
    bt_result = result.stdout

    result_index = bt_result.find("State:")

    result_str = bt_result[result_index:result_index + 10].split(": ")[1].strip()

    if result_str == 'Off':
        return False
    else:
        # elif result_str == 'On':
        return True

def scan_BT_devices():
    # Scan for devices, both paired and unpaired
    devices = _scan_BT_devices()

    if not devices:
        print("No Bluetooth devices found.")

    # List all found devices by their names and addresses
    print("Found Bluetooth devices:")

    list_bt_devs = []

    for i in range(2, len(devices)):
        device = devices[i]
        device_info = device.split()
        if len(device_info) >= 2:
            address = device_info[device_info.index("address:") + 1].replace(",", "").replace("\"", "")
            name = device_info[device_info.index("name:") + 1].replace(",", "").replace("\"", "")

            list_bt_devs.append([address, name])

    return list_bt_devs
def _scan_BT_devices():
    print("Scanning for nearby Bluetooth devices...")
    try:
        output = subprocess.check_output(["blueutil", "--inquiry"], stderr=subprocess.STDOUT)
        devices = output.decode().strip().splitlines()
        print(devices)
        return devices
    except subprocess.CalledProcessError as e:
        print(f"Error scanning for devices: {e.output.decode()}")
        return []

def connect_to_device(device_address):
    print(f"Connecting to device with address: {device_address}")
    try:
        subprocess.check_output(["blueutil", "--connect", device_address], stderr=subprocess.STDOUT)
        print("Connection successful!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error connecting to device: {e.output.decode()}")
        return False


def forget_bluetooth_device(device_address):
    try:
        # Run the blueutil command to remove the device
        result = subprocess.run(['blueutil', '--remove', device_address], capture_output=True, text=True)

        # Check the result
        if result.returncode == 0:
            print(f"Successfully forgot Bluetooth device {device_address}.")
        else:
            print(f"Failed to forget Bluetooth device {device_address}. Error: {result.stderr}")
    except Exception as e:
        print(f"Error: {str(e)}")

def get_MAC_address_from_COM_port(port_tty):
    """Only in MAC"""
    nearby_BT_devs = scan_BT_devices()

    for i in range(len(nearby_BT_devs)):
        dev_name = nearby_BT_devs[i][1]
        print(dev_name)
        print(nearby_BT_devs[i][0])
        if dev_name == port_tty.split("tty.")[1]:
            dev_mac_address = nearby_BT_devs[i][0]

    return dev_mac_address
