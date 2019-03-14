# Overview of "Back-End" System

The “back-end” sub-system consists of any number Anchor devices, one Central Hub ("CH") device, and a client machine that queries location data from the CH. These devices are all connected to a peer-to-peer Wireless Ad-Hoc network ("WADHOC").

The Anchor nodes communicate with other Anchors as well as the CH via the WADHOC using Python socket shell scripting. 

The CH will process all data incoming from the Anchors, which are constantly forwarding data regarding the Mobile Wearable Beacon ("MWB") devices. Data parsing and calculations are performed entirely by the CH. The CH will act as a single point of access for the most up-to-date location information. As such, the client machine's query program will be directly accessing the CH's database.

The client machine is a laptop ideally running the Ubuntu 18.04 64-bit operating system. This client machine needs to physically be within-range of the WADHOC in order to connect to the network. This is because the CH and Anchor devices are not actually connected to the internet; all communication between devices is entirely local via the WADHOC. The client will use a program to perform data queries. The program will be written in Python v3.0+ with an initial interface in command shell (a GUI will be implemented ina later release). Query data will be in regards to the X, Y, and Z-axis locations of the MWB devices being carried by first responders.
