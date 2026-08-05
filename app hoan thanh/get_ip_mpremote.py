import network
print(network.WLAN(network.STA_IF).ifconfig()[0])
