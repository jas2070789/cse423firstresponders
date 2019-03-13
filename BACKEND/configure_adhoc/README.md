Raspbian Stretch changed much of the networking setups that were used in previous builds, so in order to actually set up an AD-HOC network, a few of those things had to be disabled.

The /etc/network/interfaces file has been made obsolete in favor of dhcpcd.conf, found in /etc. However, for a simple Ad-hoc network, we have no need to utilize a DHCP server, since the Pis only need to be able to talk to each other. We need to stop the Pi from automatically configuring its wireless interface to its default value. We do that by going into the dhcpcd.conf file and adding “denyinterfaces eth0 wlan0” to the top of the file.

That command tells the Pi that it shouldn’t configure its own wireless interfaces, and we will then have to configure it ourselves by going back into /etc/network/interfaces. We can do so by adding the following into the interfaces file: 

auto wlan0
Iface wlan0 inet static
  Address 10.0.0.1
  Netmask 255.255.255.0
  Wireless-channel 1
  Wireless-essid ADHOCTEST
  Wireless-mode ad-hoc

After saving the file, it’s likely that you can just restart the wireless interface and everything should be working correctly. However, to ensure proper operability, it’s better to just reboot the system.
