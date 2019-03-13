**Raspbian Stretch changed much of the networking setups and protocols that were used in previous builds "Wheezy" and "Jessie", so in order to actually set up an AD-HOC network, a few of those things had to be disabled.**

The /etc/network/interfaces file has been made obsolete in favor of dhcpcd.conf, found in /etc. However, for a simple Ad-hoc network, we have no need to utilize a DHCP server, since the Pis only need to be able to talk to each other. We need to stop the Pi from automatically configuring its wireless interface to its default value. We do that by adding the following command to the top of /etc/dhcpcd.conf:

```
denyinterfaces eth0 wlan0
```

*Note: This is assuming the only network interfaces active on the RPi are eth0 and wlan0. If there are more, they must be appended to this command. It is crucial that the wireless interface eing used to configure the ad-hoc connection is blocked (in this case, wlan0).*

The above command tells the RPi that it shouldn’t configure its own wireless interfaces (using  and it should instead configure via /etc/network/interfaces.

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
  
The value for the address will change depending on what node is being configured. 10.0.0.1 will always belong to the Central Hub, however for each Anchor the address needs to be incremented in the /24 subnet (so Anchor_1 = 10.0.0.2, A_2 = 10.0.0.3, etc.).

After saving the file, it’s likely that you can just restart the wireless interface and everything should be working correctly. However, to ensure proper operability, it’s better to just reboot the system.
