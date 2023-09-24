


from time import sleep


def test_k_device():
    ## Test expects one kelvin device connected using usb
    from k_lights_interface.k_serial_manager import KSerialManager
    dev_manager = KSerialManager()
    all_connected_devices = dev_manager.connect_to_all()
    [print(dev) for dev in all_connected_devices]
    assert(len(all_connected_devices) > 0)
    device = all_connected_devices[0]
    print(f"Chosen device for tests: {device}")

    print(f"mcumgr_conn_string: {device.mcumgr_conn_string}")

    ret, temp = device.get_emitter_temperature()
    assert(ret == True)
    ret, device_stats = device.get_device_stats()
    assert(ret == True)
    ret, device_id = device.get_device_name()
    assert(ret == True)
    ret, serial_nr = device.get_serial_number()
    assert(ret == True)
    print(f"serial_nr: {serial_nr}")



def test_set_channels():
    from k_lights_interface.k_serial_manager import KSerialManager
    dev_manager = KSerialManager()
    all_connected_devices = dev_manager.connect_to_all()
    [print(dev) for dev in all_connected_devices]
    assert(len(all_connected_devices) > 0)
    device = all_connected_devices[0]
    print(f"Chosen device for tests: {device}")
    for i in range(6):
        test_list = [0]*6
        test_list[i] = 10
        device.set_rgbacl_emitter_channels_without_compensation_unsafe(test_list)
        sleep(0.4)
    sleep(0.4) 
    device.set_rgbacl_emitter_channels_without_compensation_unsafe([0,0,0,0,0,0])


def test_get_version():
    from k_lights_interface.k_serial_manager import KSerialManager
    dev_manager = KSerialManager()
    all_connected_devices = dev_manager.connect_to_all()
    [print(dev) for dev in all_connected_devices]
    assert(len(all_connected_devices) > 0)
    device = all_connected_devices[0]
    ret, fw = device.get_firmware_version()
    assert(ret == True)
    print(f"fw_version: {fw}")

def test_set_intensity():
    from k_lights_interface.k_serial_manager import KSerialManager
    import k_lights_interface.proto_protocol as kprot
    dev_manager = KSerialManager()
    all_connected_devices = dev_manager.connect_to_all()
    [print(dev) for dev in all_connected_devices]
    assert(len(all_connected_devices) > 0)
    device = all_connected_devices[0]

    ret = device.set_cct(5500,0)
    assert(ret == True)
    ret = device.set_intensity(0,kprot.IntensityMessageLightOutputType.MAXIMUM)
    assert(ret == True)
    # sleep(0.5)
    # while True:
    #     ret, current_light_output = device.get_current_light_output_data()
    #     #assert(ret == True)
    #     if not ret:
    #         continue
    #     current_light_output.estimated_watt_draw
    #     print(f"Estimated watt draw: {current_light_output.estimated_watt_draw}")
    #     sleep(1)

