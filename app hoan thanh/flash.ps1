$ErrorActionPreference = "Stop"
Write-Host "Downloading MicroPython Firmware..."
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
curl.exe -k -L -o firmware.bin "https://micropython.org/resources/firmware/ESP32_GENERIC_S3-20240602-v1.23.0.bin"
Write-Host "Download complete. Erasing flash..."
python -m esptool --port COM3 erase_flash
Write-Host "Flashing MicroPython..."
python -m esptool --port COM3 --baud 460800 write_flash -z 0x0 firmware.bin
Write-Host "DONE FLASHING!"
