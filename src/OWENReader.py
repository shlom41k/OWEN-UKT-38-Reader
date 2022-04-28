import serial.tools.list_ports
import serial


from time import sleep
from TmpToFile import WriteErrorToLog


FLAG_PORT_OPEN = False
BROADCAST_FLAG = False

tmp_act_min = -30.0
tmp_act_max = 60.0


def SearchCOMPorts():
    com_ports = {}
    ports = serial.tools.list_ports.comports()
    for port, desc, hwid in sorted(ports):
            com_ports.update({port: desc})
    return com_ports


def ROL(data, shift=1, size=8):
    shift %= size
    remains = data >> (size - shift)
    body = (data << shift) - (remains << size)
    return (body + remains)

def L_shift(b):
    x = (b << 1) & 0xFF
    y = (b >> 7) & 0xFF
    return x | y

def CRC_cnt(READ_DATA):
    CRC = 0

    for byte in READ_DATA:
        byte = int.from_bytes(byte, byteorder='big', signed=False)
        # print(byte)
        CRC = L_shift(CRC)
        CRC = (CRC + byte) & 0xFF
        # print(int.to_bytes(CRC, 1, byteorder='big', signed=False))
    return int.to_bytes(CRC, 1, byteorder='big', signed=False)

def CreateSerialPort(portname="COM4"):
    ser = serial.Serial()
    ser.port = portname
    ser.baudrate = 9600
    ser.bytesize = serial.EIGHTBITS
    ser.stopbits = serial.STOPBITS_TWO
    ser.parity = serial.PARITY_EVEN
    ser.timeout = 0
    ser.xonxoff = 0
    ser.rtscts = 0
    ser.dsrdtr = 0
    ser.writeTimeout = 2
    return ser

def ConnectToAC2(ser):
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    # ser.set_output_flow_control(True)
    # ser.set_input_flow_control(True)
    ser.xonxoff = False
    ser.rtscts = False
    ser.dsrdtr = False

    ser.flushInput()
    ser.flushOutput()

    ser.setRTS(0)
    ser.setDTR(1)
    ser.setRTS(1)
    sleep(0.01)
    ser.setRTS(0)
    sleep(0.5)

def ConnectToAC2_2(ser):
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    ser.xonxoff = False
    ser.rtscts = False
    ser.dsrdtr = False

    ser.flushInput()
    ser.flushOutput()

    ser.setRTS(1)
    ser.setDTR(1)
    ser.setRTS(0)
    sleep(0.01)
    ser.setRTS(1)
    sleep(0.01)
    ser.setDTR(0)
    sleep(0.01)
    ser.setDTR(1)
    sleep(0.5)

def IsReadyToWork(ser):
    BROADCAST_FLAG = False
    BROADCAST = bytearray([0x71])
    RESPONSE = bytearray([0x55]).hex()

    ser.write(BROADCAST)
    #print("Write data: ", BROADCAST.hex())
    sleep(0.2)
    try:
        while ser.inWaiting():
            response = ser.read().hex()
            if response == RESPONSE:
                BROADCAST_FLAG = True
                #print("Read data: " + response)
                #print("Answer from OWEN is correct")
    except:
        WriteErrorToLog("Error in reading")
        print("Error in reading")
        #ser.close()
        #exit()
    return BROADCAST_FLAG

def Read16Bytes(ser):
    READ_CORRECT = False
    READ_16_BYTES_CRC = bytearray([0x03])
    WORD_LSB = bytearray([0xA0])
    DATA_TMP = []

    ser.write(READ_16_BYTES_CRC)
    #print("Write data: ", READ_16_BYTES_CRC.hex())
    ser.write(WORD_LSB)
    #print("Write data: ", WORD_LSB.hex())
    sleep(0.1)

    try:
        while ser.inWaiting():
            res = ser.read().hex()
            #print("Read data: " + res)
            onebyte = bytes.fromhex(res)
            DATA_TMP.append(onebyte)
    except:
        WriteErrorToLog("Error reading temperature data")
        print("Error reading temperature data")
        #ser.close()
    print(DATA_TMP)


    CRC = CRC_cnt(DATA_TMP[2:18])
    if CRC == DATA_TMP[18]:
        print("CRC_OK")


    if (len(DATA_TMP) == 19) & (READ_16_BYTES_CRC == DATA_TMP[0]) & (WORD_LSB == DATA_TMP[1]):
        try:
            READ_CORRECT = True
            TMP_int_val = GetIntValues(DATA_TMP[2:-1])
            #print("Conversion to INT complete successful")
        except:
            READ_CORRECT = False
            WriteErrorToLog("Error with conversion to INT")
            print("Error with conversion to INT")

    return TMP_int_val, READ_CORRECT

def GetIntValues(Read_Data):
    TMP_int = []
    for Rdata in Read_Data:
        TMP_int.append(bytes_to_int(Rdata))
    return TMP_int

def bytes_to_int(bytes):
    result = 0
    for b in bytes:
        result = result * 256 + int(b)
    return result

def int_to_bytes(value, length):
    result = []
    for i in range(0, length):
        result.append(value >> (i * 8) & 0xFF)
    result.reverse()
    return result

def GetTMPValues(TMP_data):
    t1 = DecodeValues(TMP_data[1], TMP_data[0])
    t2 = DecodeValues(TMP_data[3], TMP_data[2])
    t3 = DecodeValues(TMP_data[5], TMP_data[4])
    t4 = DecodeValues(TMP_data[7], TMP_data[6])
    t5 = DecodeValues(TMP_data[9], TMP_data[8])
    t6 = DecodeValues(TMP_data[11], TMP_data[10])
    t7 = DecodeValues(TMP_data[13], TMP_data[12])
    t8 = DecodeValues(TMP_data[15], TMP_data[14])
    return t1, t2, t3, t4, t5, t6, t7, t8

def DecodeValues(MSB, LSB):
    res = 0
    if MSB == 170:
        return res

    if MSB == 255:
        res = (MSB * 255 + LSB) - 65535 + 255
    elif MSB > 0:
        res = MSB * 255 + LSB
    else:
        res = LSB
    return res/10

def IsValuesValid(t1, t2, t3, t4, t5, t6, t7, t8, min=tmp_act_min, max=tmp_act_max):
    Valid = False
    if (min < t1 < max) and (min < t2 < max) and (min < t3 < max) and (min < t4 < max) and \
            (min < t5 < max) and (min < t6 < max) and (min < t7 < max) and (min < t8 < max):
        Valid = True
    else:
        WriteErrorToLog("Temperature is not correct: " + str(t1) + ", " + str(t2) + ", " + str(t3) + ", " + str(t4) +
                        ", " + str(t5) + ", " + str(t6) + ", " + str(t7) + ", " + str(t8) + ", ")
        print("Temperature is not correct: ", t1, t2, t3, t4, t5, t6, t7, t8, sep=", ")
    return Valid

def MinMaxValues(mass):
    tmpmin = min(mass[0])
    tmpmax = max(mass[0])
    for m in mass:
        if min(m) < tmpmin:
            tmpmin = min(m)
        if max(m) > tmpmax:
            tmpmax = max(m)
    return tmpmin, tmpmax


#######################################################
def main(port="COM3"):
    AC_Device = True
    global FLAG_PORT_OPEN, BROADCAST_FLAG

    try:
        ser = CreateSerialPort(port)
        ser.open()
        FLAG_PORT_OPEN = True
    except:
        FLAG_PORT_OPEN = False
        print("Error open serial port")

    while True:
        if ser.isOpen():
            # try:
                # ser.reset_input_buffer()
                # ser.reset_output_buffer()
                # #ser.set_output_flow_control(True)
                # #ser.set_input_flow_control(True)
                # ser.xonxoff = False
                # ser.rtscts = False
                # ser.dsrdtr = False
                #
                # ser.flushInput()
                # ser.flushOutput()
                #
                # ser.setRTS(0)
                # ser.setDTR(1)
                # ser.setRTS(1)
                # sleep(0.01)
                # ser.setRTS(0)
                # sleep(0.5)
                if AC_Device:
                    ConnectToAC2(ser)
                else:
                    ConnectToAC2_2(ser)
                AC_Device = not AC_Device
                BROADCAST_FLAG = IsReadyToWork(ser)

                # ser.write(BROADCAST)
                # print("Write data: ", BROADCAST.hex())
                # sleep(0.2)
                #
                # try:
                #     while ser.inWaiting():
                #         response = ser.read().hex()
                #         if response == RESPONSE:
                #             BROADCAST_FLAG = True
                #             print("Read data: " + response)
                #             print("Answer from OWEN is correct")
                # except:
                #     print("Error in reading")
                #     ser.close()
                #     exit()

                if BROADCAST_FLAG:
                    # ser.write(READ_16_BYTES_CRC)
                    # print("Write data: ", READ_16_BYTES_CRC.hex())
                    # ser.write(WORD_LSB)
                    # print("Write data: ", WORD_LSB.hex())
                    # sleep(0.1)
                    #
                    # try:
                    #     while ser.inWaiting():
                    #         res = ser.read().hex()
                    #         print("Read data: " + res)
                    # except:
                    #     print("Error reading temperature data")
                    #     ser.close()
                    TMP, READ_CORRECT_FLAG = Read16Bytes(ser)

                    if READ_CORRECT_FLAG:
                        tmp_ch_1, tmp_ch_2, tmp_ch_3, tmp_ch_4, tmp_ch_5, tmp_ch_6, tmp_ch_7, tmp_ch_8 = GetTMPValues(TMP)
                        print(tmp_ch_1, tmp_ch_2, tmp_ch_3, tmp_ch_4, tmp_ch_5, tmp_ch_6, tmp_ch_7, tmp_ch_8)

                else:
                    ser.close()
                    print("OWEN no response")

            # except:
            #     print("Error communicating")
            #     ser.close()


        else:
            FLAG_PORT_OPEN = False
            print("Cannot open serial ports")
            ser.close()
        sleep(1)

if __name__ == "__main__":
    Ports = SearchCOMPorts()
    print(Ports)
    main()




