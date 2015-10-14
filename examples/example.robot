*** Settings ***

# assumes device is connected as tty.usbmodem1411
Library    ../src/CncLibrary/    device=/dev/tty.usbmodem1411
Test Teardown    Go Home And Close Connection

*** Test Cases ****

# Make sure tool is in home position before running
# Make sure device under test is in correct position
# Test pressing predefined button positions 1,2,3 and rollback tool to home location
Test Button Sequence
    Set Home And Initialize
    Press   1
    Press   2
    Press   3

*** Keywords ***

Go Home And Close Connection
    Go To Home
    Lower Tool
    Close Connection

Set Home And Initialize
    Initialize Device Locations     test_device.json
    Set Home
    Raise Tool
    Go To Home