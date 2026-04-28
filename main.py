from machine import Pin, RTC
import time
import network
import usocket as socket
import ustruct as struct

# ======================
# Wi-Fi credentials
# ======================
ssid = "{your WIFI Network ID}"
password = "{Password}"

# ======================
# Constants
# ======================
NTP_HOST = "pool.ntp.org"
NTP_DELTA = 2208988800
RESYNC_INTERVAL = 12 * 60 * 60  # 12 hours in seconds

# ======================
# RTC
# ======================
rtc = RTC()

# ======================
# Wi-Fi setup
# ======================
def connect_wifi(timeout=15):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if wlan.isconnected():
        return wlan

    wlan.connect(ssid, password)
    start = time.time()

    while not wlan.isconnected():
        if time.time() - start > timeout:
            print("Wi-Fi connection failed")
            return None
        time.sleep(0.5)

    print("Wi-Fi connected:", wlan.ifconfig()[0])
    return wlan

# ======================
# NTP time fetch
# ======================
def getTimeNTP():
    query = bytearray(48)
    query[0] = 0x1B
    addr = socket.getaddrinfo(NTP_HOST, 123)[0][-1]

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.settimeout(2)
        s.sendto(query, addr)
        msg = s.recv(48)
    finally:
        s.close()

    ntp_time = struct.unpack("!I", msg[40:44])[0]
    return time.gmtime(ntp_time - NTP_DELTA)

# ======================
# Set RTC from NTP
# ======================
def sync_rtc_from_ntp():
    try:
        tm = getTimeNTP()
        rtc.datetime((tm[0], tm[1], tm[2], tm[6] + 1,
                      tm[3], tm[4], tm[5], 0))
        print("RTC synced from NTP")
        return True
    except Exception as e:
        print("NTP sync failed:", e)
        return False

# ======================
# Initial sync attempt
# ======================
wlan = connect_wifi()
if wlan:
    sync_rtc_from_ntp()

last_sync_time = time.time()

# ======================
# LED pin setup
# ======================
hour_pins   = [Pin(pin, Pin.OUT) for pin in [15,14,13,12,11]]
minute_pins = [Pin(pin, Pin.OUT) for pin in [10,9,8,7,6,5]]
second_pins = [Pin(pin, Pin.OUT) for pin in [16,17,18,19,20,21]]

def testallleds():
    pins = [21,20,19,18,17,16,5,6,7,8,9,10,11,12,13,14,15]
    for p in pins:
        led = Pin(p, Pin.OUT)
        led.value(1)
        time.sleep(0.5)
        led.value(0)

# ======================
# DST logic (US rules)
# ======================
def is_dst_us(year, month, day, hour):
    if month == 3:
        first_weekday = time.gmtime(time.mktime((year,3,1,0,0,0,0,0)))[6]
        second_sunday = 14 - first_weekday
        return day > second_sunday or (day == second_sunday and hour >= 2)

    elif month == 11:
        first_weekday = time.gmtime(time.mktime((year,11,1,0,0,0,0,0)))[6]
        first_sunday = 7 - first_weekday
        return day < first_sunday or (day == first_sunday and hour < 2)

    return 3 < month < 11

# ======================
# LED update
# ======================
def update_leds():
    Y, MO, D, W, H_UTC, MI, S, SS = rtc.datetime()

    if is_dst_us(Y, MO, D, H_UTC):
        H_local = (H_UTC - 4) % 24
    else:
        H_local = (H_UTC - 5) % 24

    hour_bin   = f"{H_local:05b}"
    minute_bin = f"{MI:06b}"
    second_bin = f"{S:06b}"

    print(f"Time: {H_local:02d}:{MI:02d}:{S:02d}")

    for i in range(5):
        hour_pins[i].value(int(hour_bin[i]))
    for i in range(6):
        minute_pins[i].value(int(minute_bin[i]))
    for i in range(6):
        second_pins[i].value(int(second_bin[i]))

# ======================
# Main loop
# ======================
testallleds()

while True:
    update_leds()

    # 12-hour resync check
    if time.time() - last_sync_time >= RESYNC_INTERVAL:
        wlan = connect_wifi(timeout=5)
        if wlan and sync_rtc_from_ntp():
            last_sync_time = time.time()

    time.sleep(1)
