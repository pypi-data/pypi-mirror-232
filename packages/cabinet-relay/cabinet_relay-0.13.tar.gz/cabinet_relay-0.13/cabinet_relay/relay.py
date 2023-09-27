import time

import serial
from umodbus import conf
from umodbus.client.serial import rtu
from relay_attribute import *


def __set_bits(n, bits_to_set):
    for index, is_set in bits_to_set.items():
        if is_set:
            n |= 1 << index
        else:
            n &= ~(1 << index)
    return n


def __int_to_bools(n, num_bools=16):
    bools = []
    for i in range(num_bools):
        bools.append(bool(n & (1 << i)))
    return bools


def __update_and_return_bools(bits_to_set, current_n=0):
    """
    :param bits_to_set: {0: True, 3: True, 5: True}
    :param current_n:0
    :return:[True, False, False, True, False, True, False, False, False, False, False, False, False, False, False, False]
    """
    updated_n = __set_bits(current_n, bits_to_set)
    return __int_to_bools(updated_n)


def __get_attribute_value(attribute_name):
    """
    Find the full name of the attribute in the class where it is found.
    :param attribute_name: The name of the attribute to look up in the classes.
    :return: The full name of the matching attribute.
    """
    for name, obj in globals().items():
        if isinstance(obj, type) and hasattr(obj, attribute_name):
            return eval(f'{name}().{attribute_name}')
    raise ValueError(f"{attribute_name} not found in classes defined in the global scope.")


def __get_full_attribute(attribute_name):
    """
    Get the name and value of the second attribute in the same class as the given attribute.
    :param attribute_name: The name of one attribute in the class.
    :return: The name of the second attribute in the same class.
    """
    for name, obj in globals().items():
        if isinstance(obj, type) and hasattr(obj, attribute_name):
            attributes = [attr for attr in obj._fields]
            if len(attributes) < 2:
                raise ValueError(f"{name} does not have a second attribute.")
            return f'{name}.{attributes[1]}'
    raise ValueError(f"{attribute_name} not found in classes defined in the global scope.")


def __get_slave_id(attribute_name):
    return eval(f"{__get_full_attribute(attribute_name).split('.')[0]}().slave_address")


def check_connection(func):
    def wrapper(self, *args, **kwargs):
        if not self.serial_port.is_open:
            print("Port is not open. Attempting to reconnect...")
            try:
                self.serial_port.open()
                print("Reconnected successfully.")
            except Exception as e:
                raise Exception("Failed to reopen the port.") from e
        return func(self, *args, **kwargs)

    return wrapper


def analysis_relay(func):
    def wrapper(self, *args, **kwargs):
        attribute_name = args[0]
        values = __update_and_return_bools({__get_attribute_value(i): True for i in attribute_name})
        slave_id = __get_slave_id(attribute_name[0])
        return func(self, (slave_id, 0, values))

    return wrapper


class ModbusClient:
    def __init__(self, port='COM3', baudrate=115200, parity='N', stopbits=1, bytesize=8, timeout=1):
        conf.SIGNED_VALUES = True
        self.serial_port = serial.Serial(port=port, baudrate=baudrate, parity=parity, stopbits=stopbits,
                                         bytesize=bytesize, timeout=timeout)

    @check_connection
    def write_single_coil(self, slave_id, address, value):
        message = rtu.write_single_coil(slave_id=slave_id, address=address, value=value)
        response = rtu.send_message(message, self.serial_port)
        print(response)
        return response

    @check_connection
    def write_multiple_coils(self, slave_id, starting_address, values):
        message = rtu.write_multiple_coils(slave_id=slave_id, starting_address=starting_address, values=values)
        response = rtu.send_message(message, self.serial_port)
        print(response)
        return response

    @check_connection
    def read_coils(self, slave_id, starting_address, quantity):
        message = rtu.read_coils(slave_id=slave_id, starting_address=starting_address, quantity=quantity)
        response = rtu.send_message(message, self.serial_port)
        return response


class RelayController(ModbusClient):
    def __init__(self, port='COM3', baudrate=115200, parity='N', stopbits=1, bytesize=8, timeout=1):
        super().__init__(port, baudrate, parity, stopbits, bytesize, timeout)

    @analysis_relay
    def write_coils(self, address: list):
        self.write_multiple_coils(*address)

    def initialization(self, slave_id):
        """
        8,9,10,11
        :param slave_id:
        :return:
        """
        self.write_multiple_coils(slave_id, 0, [False] * 16)

    def resistance_initialization(self):
        """
        所有电阻继电器初始化
        """
        for i in range(8, 12):
            self.initialization(slave_id=i)
            time.sleep(0.1)

    def batt(self, status=True):
        """
        前置面板电源导通
        """
        self.write_single_coil(2, 1, status)

    def DMM_I(self):
        """
        DMM电流档（最大3A）串入产品供电线，并且将主电源导通，接口箱Power口被接通，与K2/K3互斥
        """
        self.write_coils(['DMM_I'])

    def AO_ON(self, AO):
        """
        将AP525的AO0接通，配合K9~K12，可将AP525的AO0接到接口箱的AO口
        """
        AO_list = [f'AO_{i}' for i in range(1, 5)]
        if AO not in AO_list:
            raise ValueError(f'AO not in {AO_list}')
        self.write_coils(['AO_ON', AO])

    def Check_AO(self):
        """
        检测Analog Output输出的信号值，将AP的Analog Input0和Analog Output0接到一起，进行自发和自收，与其他接入AI0和AO0的继电器互斥
        """
        pass


if __name__ == '__main__':
    client = RelayController()
    client.write_coils(['CH3_Res4', 'CH4_Res4'])
    client.write_coils(['CH3_AI_0', 'CH4_AI_1'])
