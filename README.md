# griggs_control
Collection of tools to control a Griggs-type apparatus via a computer.

test

setup of Raspberry Pi:
1. write PI OS (via Pi Imager) onto microSD card and insert it into a RPI
2. connect the RPI to periphery devices and boot
3. follow OS setup instructions
4. when booting was completed, install openconnect to establish LAN connections to protected networks: "sudo apt install openconnect"
5. connect to VPN with your URZ username and password: "sudo openconnect -u username -b vpn-ac.urz.uni-heidelberg.de" and then enter password
6. then you can install python packages and clone the needed github repos
