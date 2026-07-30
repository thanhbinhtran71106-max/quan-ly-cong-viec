import requests
import re

url = "https://micropython.org/download/ESP32_GENERIC_S3/"
print("Fetching page:", url)
response = requests.get(url)

# Find the first .bin link
matches = re.findall(r'href="(/resources/firmware/[^"]+\.bin)"', response.text)
if matches:
    fw_url = "https://micropython.org" + matches[0]
    print("Found firmware:", fw_url)
    print("Downloading...")
    fw_response = requests.get(fw_url)
    with open("firmware.bin", "wb") as f:
        f.write(fw_response.content)
    print("Download complete.")
else:
    print("Firmware not found.")
