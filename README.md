# griggs_control
Collection of tools to control a Griggs-type apparatus via a computer.

test

setup of Raspberry Pi:
1. write PI OS (via Pi Imager) onto microSD card and insert it into a RPI
2. connect the RPI to periphery devices and boot
3. follow OS setup instructions
4. when booting was completed, establish a temporary internet connection (e.g. via smartphone hotspot)
5. install openconnect to establish LAN connections to the protected uni network: "sudo apt install openconnect"
6. connect to VPN with your URZ username and password: "sudo openconnect -u username -b vpn-ac.urz.uni-heidelberg.de" and then enter password
7. now switch to the permanent network connection (e.g. disable personal hotspot)
8. then you can install python packages and clone the needed github repos
9. after reboot, you need to reconnect to the vpn to have an internet connection
