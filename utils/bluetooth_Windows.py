import wmi
import re


def list_bluetooth_devices():
    """List all Bluetooth devices and attempt to find the SPP UUID."""
    c = wmi.WMI()
    bluetooth_devices = c.query("SELECT * FROM Win32_PnPEntity WHERE PNPClass = 'Bluetooth'")
    print("Bluetooth Devices:")
    for device in bluetooth_devices:
        print(f"Name: {device.Name}, PNPDeviceID: {device.PNPDeviceID}")
    return bluetooth_devices


def list_com_ports():
    """List all COM ports."""
    c = wmi.WMI()
    com_ports = c.query("SELECT * FROM Win32_PnPEntity WHERE Name LIKE '%(COM%'")
    print("\nCOM Ports:")
    for port in com_ports:
        print(f"Name: {port.Name}, PNPDeviceID: {port.PNPDeviceID}")
    return com_ports

def get_COMNo_from_PNPDeviceID(port):
    # Use regular expression to find the COM port number
    match = re.search(r'COM\d+', port.Name)
    if match:
        com_number = match.group(0)  # Extract the COM number
        print(f"COM Port: {com_number}, PNPDeviceID: {port.PNPDeviceID}")
        return com_number

    return None
def extract_BT_ID(pnp_device_id):
    """Extract the code after 'DEV_' from the section of PNPDeviceID that contains 'DEV_'."""
    # Split the PNPDeviceID by "/"
    parts = pnp_device_id.split("/")
    for part in parts:
        # Look for a section that contains "DEV_"
        if "DEV_" in part:
            # Extract everything after "DEV_" in this specific section
            match = re.search(r'DEV_([A-Fa-f0-9]+)', part)
            if match:
                print(match)
                return match.group(1)
    return None


def extract_uuid_from_com_port(pnp_device_id):
    """Extract UUID from COM port PNPDeviceID."""
    match = re.search(r'\{([0-9A-Fa-f-]+)\}', pnp_device_id)
    if match:
        return match.group(1)
    return None


def get_matching_com_port(all_com_ports, dev_BT_ID):
    matched_com_port = None

    # Iterate through ports (looking for SPP port)
    for port_1_info in all_com_ports:

        # Find SPP port, contains the ID segment of the ScientISST BT device
        if dev_BT_ID in port_1_info.PNPDeviceID:

            # Extract the UUID from the COM port's PNPDeviceID
            port_1_uuid = extract_uuid_from_com_port(port_1_info.PNPDeviceID)

            for port_2_info in all_com_ports:
                port_2_uuid = extract_uuid_from_com_port(port_2_info.PNPDeviceID)

                if port_2_uuid == port_1_uuid:
                    port2_name = get_COMNo_from_PNPDeviceID(port_2_info)

                    matched_com_port = port2_name
                    break

    return matched_com_port


def get_COM_ports_Windows():
    """Attempt to correlate Bluetooth devices with COM ports using partial ID matching."""
    all_com_ports = list_com_ports()

    bluetooth_devices = list_bluetooth_devices()

    avail_com_ports_pairs = {}

    # Apply the COM Port search for all avail. BT devices
    for bt_device in bluetooth_devices:

        bt_dev_ID = extract_BT_ID(bt_device.PNPDeviceID)
        bt_dev_name = bt_device.Name

        # continue only if there is an ID
        if bt_dev_ID:

            matched_com_port = get_matching_com_port(all_com_ports, bt_dev_ID)

            if matched_com_port is not None:
                avail_com_ports_pairs[bt_dev_name] = matched_com_port

    return avail_com_ports_pairs
