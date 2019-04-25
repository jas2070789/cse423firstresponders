# Overview of "CLIENT" Sub-System

*Note: By default, the Client device needs to use an IPv4 address of ```10.0.2.255``` unless altered otherwise in source code.*

This sub-system encompasses everything required to develop a software program that can 1) join the WADHOC network, 2) query up-to-date location data, and 3) present queried data to a user via a terminal.

After configuring the device to communicate with the WADHOC network, a user will run a custom program that accesses the Central Hub's database. This program utilizes Python socket-level network programming to communicate with the Central Hub and perform database queries via a custom API interface.
