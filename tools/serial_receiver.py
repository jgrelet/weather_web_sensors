#!/usr/bin/env python3
import argparse
import json
import sys

import serial


def parse_args():
    parser = argparse.ArgumentParser(description="Receive JSON payloads from Pico serial output")
    parser.add_argument("--port", required=True, help="Serial port (example: COM5)")
    parser.add_argument("--baudrate", type=int, default=115200, help="Serial baudrate")
    parser.add_argument(
        "--prefix",
        default="JSON ",
        help='Expected line prefix before JSON payload (use "" for raw JSON lines)',
    )
    return parser.parse_args()


def main():
    args = parse_args()
    with serial.Serial(args.port, args.baudrate, timeout=1) as ser:
        print("Listening on {} @ {}...".format(args.port, args.baudrate))
        while True:
            line = ser.readline()
            if not line:
                continue
            text = line.decode("utf-8", errors="replace").strip()
            if not text:
                continue
            if args.prefix and not text.startswith(args.prefix):
                continue
            payload_text = text[len(args.prefix) :] if args.prefix else text
            try:
                payload = json.loads(payload_text)
                print(json.dumps(payload, ensure_ascii=False))
            except Exception as exc:
                print("Invalid JSON line: {} ({})".format(payload_text, exc), file=sys.stderr)


if __name__ == "__main__":
    main()
