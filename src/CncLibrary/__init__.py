#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import string
import os
import json
from contextlib import contextmanager
try:
    import serial
except ImportError:
    raise CncLibraryException("pyserial needs to be installed!")
from version import VERSION

__version__ = VERSION

class CncLibrary(object):
    """ 
    Library for controlling a CNC-milling machine controlled by Arduino based motion controller using gcodes. E.g. ShapeOko 2.

    Idea here is that you can modify/build such a machine to be used for testing devices that require physical contact e.g push button on a button pad device.
    
    """

    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'
    ROBOT_LIBRARY_VERSION = VERSION

    def __init__(self, device='', baud=115200, xy_speed=10000, z_speed=800):
        """ device must be given as the device that is connected e.g. /dev/tty.usbmodem1411 """
        self.device = device
        self.baud = baud
        self._serial = None
        self.xy_speed = xy_speed
        self.z_speed = z_speed
        self.timeout = 10
        if not device or not baud:
            raise CncLibraryException('Device and baud is not set')
        self.locations = {}

    @property
    def serial(self):
        """ open serial port connection to the connected device """
        if self._serial:
            return self._serial
        else:
            self._serial = serial.Serial(self.device, self.baud)
            self._serial.write("\r\n\r\n")
            time.sleep(2)   # Wait for grbl to initialize
            self._serial.flushInput()
            return self._serial

    def _send_gcode(self, gcode_line):
        """ send gcode to serial device """
        print 'Sending: ' + gcode_line
        self.serial.write(gcode_line + '\n')
        grbl_out = self.serial.readline()    # Wait for grbl response with carriage return
        print ' : ' + grbl_out.strip()

    def _move(self, speed, xcord, ycord):
        """ move the tip of the device in xy-plane and wait for it to reach destination """
        gcode_line = "G01 " + speed + " X" + xcord + " Y" + ycord
        with self._moving(xcord, ycord):
            self._send_gcode(gcode_line)

    def _current_position(self):
        """ return current position from the device """
        self.serial.write("?")
        grbl_out = self.serial.readline()    # Wait for grbl response with carriage return
        grbl_out = grbl_out.split("MPos:", 1)[1]
        coordinates = grbl_out.split(',', 3)
        x = round(float(coordinates[0]), 1)
        y = round(float(coordinates[1]), 1)
        z = round(float(coordinates[2]), 1)
        return (x,y,z)

    #### Keywords ####

    def request_position(self):
        """ Returns current position of the device as tuple """
        position = self._current_position()
        print position
        return position

    def close_connection(self):
        """ close serial connection """
        self.serial.close()

    # Device location initializations
    def initialize_device_locations(self, conf_file_path):
        """ Initialize coordinate positions of the tested device from .json configuration file see examples """
        with open(conf_file_path) as f:
            self.locations = json.loads(f.read())
        if "device_location" not in self.locations:
            raise CncLibraryException("using 'device_location' is mandatory. This should be the highest point of your device.")

    # Calibration and home position
    def set_home(self):
        """ Set home position that will be treated as 0,0,0 for device coordinates """
        gcode = 'G92 X0 Y0 Z0'
        self._send_gcode(gcode)
        time.sleep(0.2)
        print self.locations['device_location']['x']
        print self.locations['device_location']['y']
        print self.locations['device_location']['z']

    def raise_tool(self):
        """ Raise the tooltip of the mill to its safe height defined as 'device_location' z-coordinate """
        gcode = "G01 F500 Z"+str(self.locations['device_location']['z'])
        print gcode
        with self._pressing(self.locations['device_location']['z']):
            self._send_gcode(gcode)

    def go_to_home(self):
        """ Go to home position 0,0,0 """
        # ensure up position
        self.raise_tool()
        xcord = '0.0'
        ycord = '0.0'
        with self._moving(xcord, ycord):
            self._send_gcode("G01 F"+str(self.xy_speed)+" X0.0 Y0.0")
        
    def lower_tool(self):
        """ Lower tool to 0 z-coordinate. Use this after you have moved to home position """
        # todo: combine with go_to_home?
        zcord_down = '0.0'
        with self._pressing(zcord_down):
            self._send_gcode("G01 F"+str(self.z_speed)+" Z0.0")

    def press(self, *args):
        """ 
        1. Raise the tool to safe height.

        2. Move the tool in xy-coordinate of given position defined that match definition in config file, relative to 'device_location'.

        3. Ensure that correct position is reached in 10 seconds.

        4. Lower the tool to z-coordinate of the position and ensure it's reached in 10 seconds.

        5. Raise the tool to safe height and ensure it's raised. 
        """
        for goal in args:
            self.go_to(goal)
            self.press_button(self.locations[goal]['z'])

    # Moving to buttons/camera
    def go_to(self, *args):
        """
        1. Raise the tool to safe height and ensure it's raised.

        2. Move the tool in xy-plane to position relative to 'device_location'
        """
        for goal in args:
            # ensure up position
            self.raise_tool()
            xcord = str(float(self.locations[goal]['x']) + float(self.locations['device_location']['x']))
            ycord = str(float(self.locations[goal]['y']) + float(self.locations['device_location']['y']))
            self._move("F"+str(self.xy_speed), xcord, ycord)
    
    def direct_go_to(self, position):
        """
        NOTE: USING THIS IS DANGEROUS AS THE TOOL MIGHT HIT ANYTHING THAT IS ON ITS WAY USING THIS.
        Intention here is to use this moving in xy-plane when you need to move on flat surface e.g. touch screen.
        Or to move the tool to known safe position e.g. for using a bundled camera.

        Directly move to the position. Relative to the home position not 'device_location' like the normal go_to.
        """
        x = self.locations[position]['x']
        y = self.locations[position]['y']
        z = self.locations[position]['z']
        with self._moving(x, y, z):
            self._send_gcode("G01 F"+str(self.z_speed)+" X"+str(x)+" Y"+str(y)+" Z"+str(z))

    def press_button(self, down):
        """ 
        Lower the device to z-coordinate given as argument and raise it back up.
        """
        # press down
        try:
            with self._pressing(down):
               self._send_gcode("G01 F"+str(self.z_speed)+" Z" + str(down))
        except Exception as e:
            raise e

        # raise the tip back to safe position
        finally:
            with self._pressing(self.locations['device_location']['z']):
                self._send_gcode("G01 F"+str(self.z_speed)+" Z" + str(self.locations['device_location']['z']))

    def execute_gcode_file(self, filename):
        """
        Excute gcodes directly from a file where each line is a gcode. Gcodes are sent directly to serial port without any assurance what they actually do.
        """
        with open(filename) as f:
            for line in f.readlines():
                self._send_gcode(line)  

    @contextmanager
    def _moving(self, target_x, target_y, target_z=None):
        """ 
        Context manager for moving the tool that ensures the tool moved to given position.
        if no target_z argument is given we assume safe height e.g. 'device_location' z-coodinate. 
        """
        if not target_z:
            target_z = self.locations['device_location']['z'] 
        yield
        # ensure tip is in correct x,y position
        self._ensure_position(target_x, target_y, target_z)

    @contextmanager
    def _pressing(self, target):
        """ Context manager for moving the tool that ensures the tool moved to given position """
        yield
        self._ensure_z_position(target)

    def _ensure_position(self, target_x, target_y, target_z):
        """ ensure that tool is in given coordinates """
        init_time = time.time()
        while self._current_position() != (float(target_x), float(target_y), float(target_z)):
            print self._current_position()
            print target_x, target_y, target_z
            time.sleep(0.2)
            elapsed = time.time() - init_time
            if elapsed > self.timeout:
                raise CncLibraryException('Exceeded 10s timeout.')

    def _ensure_z_position(self, target):
        """ ensure that tool is in given z-position """
        init_time = time.time()
        while (self._current_position()[2] != float(target)):
            print self._current_position()[2]
            print target
            time.sleep(0.2)
            elapsed = time.time() - init_time
            if elapsed > self.timeout:
                raise CncLibraryException('Exceeded 10s timeout.')

class CncLibraryException(Exception):
    pass
