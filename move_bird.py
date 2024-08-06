#!/usr/bin/env python

import os
from scservo_sdk import *  # Uses SCServo SDK library

# Control table address
ADDR_SCS_TORQUE_ENABLE = 40
ADDR_SCS_GOAL_ACC = 41
ADDR_SCS_GOAL_POSITION = 42
ADDR_SCS_GOAL_SPEED = 46
ADDR_SCS_PRESENT_POSITION = 56

# Default setting
SCS_ID = 1  # SCServo ID : 1
BAUDRATE = 1000000  # Driver board default baudrate : 1000000
DEVICENAME = '/dev/tty.usbmodem578E0213011' 

SCS_MINIMUM_POSITION_VALUE = 100  # SCServo will rotate between this value
SCS_MAXIMUM_POSITION_VALUE = 4000  # and this value
SCS_MOVING_STATUS_THRESHOLD = 20  # SCServo moving status threshold
SCS_MOVING_SPEED = 300  # SCServo moving speed
SCS_MOVING_ACC = 0  # SCServo moving acc
protocol_end = 1  # SCServo bit end(STS/SMS=0, SCS=1)

TARGET_POSITION_MIN = 500
TARGET_POSITION_MAX = 680
NEUTRAL_POSITION = 520

# Initialize PortHandler instance
portHandler = PortHandler(DEVICENAME)

# Initialize PacketHandler instance
packetHandler = PacketHandler(protocol_end)

# Open port
if not portHandler.openPort():
    print("Failed to open the port")
    quit()

# Set port baudrate
if not portHandler.setBaudRate(BAUDRATE):
    print("Failed to change the baudrate")
    quit()

# Write SCServo acc
scs_comm_result, scs_error = packetHandler.write1ByteTxRx(portHandler, SCS_ID, ADDR_SCS_GOAL_ACC, SCS_MOVING_ACC)
if scs_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(scs_comm_result))
elif scs_error != 0:
    print("%s" % packetHandler.getRxPacketError(scs_error))

# Write SCServo speed
scs_comm_result, scs_error = packetHandler.write2ByteTxRx(portHandler, SCS_ID, ADDR_SCS_GOAL_SPEED, SCS_MOVING_SPEED)
if scs_comm_result != COMM_SUCCESS:
    print("%s" % packetHandler.getTxRxResult(scs_comm_result))
elif scs_error != 0:
    print("%s" % packetHandler.getRxPacketError(scs_error))

def move_servo(goal_position):
    """Move the servo motor to a specified angle"""
    position = goal_position
    # print(f"Moving to: {position}")

    # Write SCServo goal position
    scs_comm_result, scs_error = packetHandler.write2ByteTxRx(portHandler, SCS_ID, ADDR_SCS_GOAL_POSITION, position)
    if scs_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(scs_comm_result))
    elif scs_error != 0:
        print("%s" % packetHandler.getRxPacketError(scs_error))

    while True:
        # Read SCServo present position
        scs_present_position_speed, scs_comm_result, scs_error = packetHandler.read4ByteTxRx(portHandler, SCS_ID, ADDR_SCS_PRESENT_POSITION)
        if scs_comm_result != COMM_SUCCESS:
            print(packetHandler.getTxRxResult(scs_comm_result))
            break
        elif scs_error != 0:
            print(packetHandler.getRxPacketError(scs_error))
            break

        scs_present_position = SCS_LOWORD(scs_present_position_speed)
        scs_present_speed = SCS_HIWORD(scs_present_position_speed)
        # print("[ID:%03d] GoalPos:%03d PresPos:%03d PresSpd:%03d" % (SCS_ID, position, scs_present_position, SCS_TOHOST(scs_present_speed, 15)))

        if not (abs(position - scs_present_position) > SCS_MOVING_STATUS_THRESHOLD):
            break

    # Disable torque
    scs_comm_result, scs_error = packetHandler.write1ByteTxRx(portHandler, SCS_ID, ADDR_SCS_TORQUE_ENABLE, 0)
    if scs_comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(scs_comm_result))
    elif scs_error != 0:
        print("%s" % packetHandler.getRxPacketError(scs_error))
        
def move_bird():
    move_servo(NEUTRAL_POSITION)
    move_servo(TARGET_POSITION_MIN)
    move_servo(TARGET_POSITION_MAX)
    move_servo(TARGET_POSITION_MIN)
    move_servo(TARGET_POSITION_MAX)
    move_servo(TARGET_POSITION_MIN)
    move_servo(TARGET_POSITION_MAX)
    move_servo(NEUTRAL_POSITION)

# Close port when done
def close_port():
    portHandler.closePort()