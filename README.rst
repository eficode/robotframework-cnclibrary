CncLibrary
==========

This is a Robot Framework library for driving a CNC milling machine. Idea here is that the mill is modified/built so that the cutter is replaced by a tool tip that can be used to touch physical device e.g. device with numpad. With this library you can move the tool tip to predefined locations and use it to press (buttons). This is useful for auomating acceptance testing for devices that can only be accessed physically. Library only contains keywords for driving the tool. Assertions needs to be done with some other way depending on the device under test e.g. camera+image recognition.

In our case we used ShapeOko 2 CNC-milling machine controlled by Arduino based motion controller with and Raspberry Pi 2 with camera module is connected. The device under test in example is iZettle payment terminal. 

Image Recognition library we used with camera for assertions is not included in this library. 

Prerequisities
--------------

- `Python 2.7`
- `pip`
- `Robot Framework`

Installation
------------

If you have pip, installation is straightforward

::

    $ pip install robotframework-cnclibrary

This will automatically install dependencies as well as their dependencies.

Note: if pip install does not find the package, 
download, extract and pip install the folder



Configuration file format
-------------------------

Configuration uses simple json format where you define positions in 3D-space. 

There is a special location called 'device_location' that needs to exist in the configuration. The 'device_location' is relative to the home location where you always start the test cases. This 'device_location' is also special location in a sense that it must the highest location in Z-coordinates. This location is used as safe height when raising and moving the tool -- ie. no other location can be above the 'device_location' - otherwise the tool might collide to the device under test.

Button locations are relative are to 'device_location' in xy-plane to make it more simple to map the location of the buttons. Z-coodinate is however always relative to the home location ie. Z should never have negative value.

You can also define special locations that are not buttons. e.g. for example location where the tool should go to take a photo if you have a camera attached. You can use 'Go To' keyword to move the tool to such location without lowering/pressing.

See example config in examples/test_device.json.

Keyword documentation
---------------------

`Keyword Documentation`__

__ http://eficode.github.io/robotframework-cnclibrary/doc/CncLibrary.html

Running tests
-------------

To run tests:

::

    $ cd tests/itest/
    $ python test_cnclibrary.py



