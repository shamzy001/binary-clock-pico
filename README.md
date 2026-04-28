# Binary Clock — Raspberry Pi Pico W

A binary clock running on a Raspberry Pi Pico W using MicroPython.

## Features
- Displays hours, minutes, and seconds in binary across 17 LEDs (5H + 6M + 6S)
- Syncs time on boot via NTP over a raw UDP socket
- Re-syncs every 12 hours
- US Daylight Saving Time handled automatically
- 3D printed enclosure

## Hardware
- Raspberry Pi Pico W
- 17 LEDs (blue = hours, green = minutes, red = seconds)
- 3D printed enclosure

## Setup
1. Edit `main.py` and fill in your Wi-Fi credentials
2. Flash MicroPython to your Pico W
3. Copy `main.py` to the Pico
