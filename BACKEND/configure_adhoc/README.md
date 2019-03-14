# Configuring a Raspberry Pi's Wireless Network Interface to Connect to WADHOC Network

###### Target Operating System: Raspbian Stretch (Full) v.2018-11-13

**Raspbian Stretch changed much of the networking setups and protocols that were used in previous builds "Wheezy" and "Jessie". As a result, in order to actually set up a Wireless AD-HOC ("WADHOC") network, a few of those changes will need to be bypassed. This README details how to accomplish this.**

For each device that needs to connect to the WADHOC network, /etc/dhcpcd.conf and /etc/network/interfaces must be modified. The following information represents what would have to be done to configure the Central Hub device. When configuring the WADHOC on subsequent devices, the values for certain parameters will need to be changed accordingly. These changes will be discussed in detail further in this document.

The /etc/network/interfaces file has been made obsolete in favor of dhcpcd.conf, found in /etc. However, for a simple ad-hoc network, we have no need to utilize a DHCP server, since the Pis only need to be able to talk to each other. We need to stop the Pi from automatically configuring its wireless interface to its default value. We do that by adding the following command to the top of /etc/dhcpcd.conf:

```
denyinterfaces eth0 wlan0
```

*Note: This is assuming the only network interfaces active on the RPi are eth0 and wlan0. If there are more, they must be appended to this command. It is crucial that the wireless interface being used to configure the ad-hoc connection is denied (in this case, wlan0). Use `sudo iwconfig` to query a list of the device's network interfaces.*

The above command tells the RPi that it shouldn’t configure its network interfaces via /etc/dhcpcd.config and it should instead configure via /etc/network/interfaces.

We then add the following parameters to the /etc/network/interfaces file:

```
auto wlan0
iface wlan0 inet static
  address 10.0.0.1
  netmask 255.255.255.0
  wireless-channel 1
  wireless-essid ADHOCTEST
  wireless-mode ad-hoc
```
  
The value for the address will change depending on what node is being configured. 10.0.0.1 will always belong to the Central Hub, however for each Anchor the address needs to be incremented in the /24 subnet (so Anchor1 = 10.0.0.2, A2 = 10.0.0.3, etc.). The netmask, wireless-channel, essid, and mode all remain the same.

After saving the file, restart the device for changes to take full effect. Upon next boot, the device's wlan0 interface will be connected to the "ADHOCTEST" network.

**This process must be repeated for every other node that wants to connect to the WADHOC. The address and (if necessary) the target interface are to be modified, however most other values MUST remain the same (ESSID, channel, netmask, and mode).**

For example, this is what an Anchor device must modify in the two files:

- In /etc/dhcpcd.config:
```
denyinterfaces eth0 wlan0
```

- In /etc/network/interfaces (*note the different address*):
```
auto wlan0
iface wlan0 inet static
  address 10.0.0.2
  netmask 255.255.255.0
  wireless-channel 1
  wireless-essid ADHOCTEST
  wireless-mode ad-hoc
```


