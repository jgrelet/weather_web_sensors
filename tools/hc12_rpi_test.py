#!/usr/bin/env python3
import argparse
import time

import serial


def parse_args():
    parser = argparse.ArgumentParser(
        description="HC-12 test script for Raspberry Pi side. Sends PING_RPI and replies to PING_PICO."
    )
    parser.add_argument("--port", required=True, help="Serial device for HC-12, e.g. /dev/serial0 or /dev/ttyUSB0")
    parser.add_argument("--baudrate", type=int, default=9600, help="Baud rate for the HC-12 link")
    parser.add_argument("--interval", type=float, default=2.0, help="Seconds between outgoing PING_RPI messages")
    return parser.parse_args()


def main():
    args = parse_args()
    counter = 0
    next_send = time.monotonic()

    with serial.Serial(args.port, args.baudrate, timeout=0.1) as ser:
        print(f"HC-12 RPi test on {args.port} @ {args.baudrate} baud")
        print("Loop sends PING_RPI and replies ACK_RPI to Pico ping messages.")

        while True:
            now = time.monotonic()
            if now >= next_send:
                counter += 1
                message = f"PING_RPI {counter} {int(now * 1000)}"
                ser.write((message + "\n").encode())
                print("sent:", message)
                next_send = now + args.interval

            line = ser.readline()
            if not line:
                time.sleep(0.05)
                continue

            decoded = line.decode("utf-8", "replace").strip()
            if not decoded:
                continue

            if decoded.startswith("PING_PICO"):
                print("received from Pico:", decoded)
                response = f"ACK_RPI {decoded}"
                ser.write((response + "\n").encode())
                print("sent:", response)
            elif decoded.startswith("ACK_PICO"):
                print("received ACK from Pico:", decoded)
            else:
                print("received other:", decoded)


if __name__ == "__main__":
    main()
