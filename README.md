# usb-mapping

This is a utility for mapping physical USB ports to device nodes.

After running the script, enter the name you want to give the port, 
e.g. USB0, and then plug a mass storage device into the port. The
utility will detect the udev event and extract the device node identifier
and assign it to a dictionary.

When you're done, hit 'q', and the utility will pickle the dictionary
and write it to disk.

The pickled dictionary is meant to be used with the usb-pyromaniac 
utility that performs mass firmware image burns, and helps the utility 
notify the operator exactly which physical USB port has a fault.

Check out usb-pyromaniac for the associated tool this was written
to support.
