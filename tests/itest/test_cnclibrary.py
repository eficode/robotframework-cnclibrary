import unittest
from fake_device import FakeDevice
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from CncLibrary import CncLibrary
from CncLibrary import CncLibraryException
from StringIO import StringIO

class TestCncLibrary(unittest.TestCase):

    def setUp(self):
        self.cnc_library = CncLibrary(device="invalid")
        self.cnc_library._serial = FakeDevice()
        self.device = self.cnc_library._serial
        self.cnc_library.initialize_device_locations(os.path.join("..", "..", "examples", "test_device.json"))
        self.cnc_library.timeout = 1

    def test_close_connection(self):
        self.assertTrue(self.device.connected)
        self.cnc_library.close_connection()
        self.assertFalse(self.device.connected)

    def test_init_without_device_location(self):
        self.assertRaises(CncLibraryException, self.cnc_library.initialize_device_locations, "without_device_location.json")

    def test_send_g_code(self):
        # fake object loops back commands that are not recognized
        # test that gcode is passed to loopback device and printed to log by CncLibrary
        code = "G02 F1000 X1 Y1 Z3"
        output = StringIO()
        normal_output =  sys.stdout
        sys.stdout = output
        self.cnc_library._send_gcode(code) 
        sys.stdout = normal_output      
        self.assertIn(code, output.getvalue())

    def test_move(self):
        self.cnc_library.set_home()
        self.cnc_library.raise_tool()
        self.cnc_library._move("F1000", "1.0", "1.0")
        position = self.cnc_library.request_position()
        self.assertEqual(position, (1.0, 1.0, 14))

    def test_set_home(self):
        self.cnc_library.set_home()
        self.assertIsNotNone(self.device.home)

    def test_go_to_flows(self):
        # test that moving the tool works
        # Fake object updates its location so that ensuring functionality in the CncLibrary can be tested
        self.cnc_library.set_home()
        self.cnc_library.press("2")
        self.cnc_library.direct_go_to("Camera")
        self.cnc_library.go_to_home()
        self.cnc_library.lower_tool()

    def test_g_code_file(self):
        self.cnc_library.set_home()
        self.cnc_library.execute_gcode_file("gcodes.txt")
        position = self.cnc_library.request_position()
        self.assertEqual(position, (3.0, 4.0, 5.0))

if __name__ == '__main__':
    unittest.main()