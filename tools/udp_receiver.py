#!/usr/bin/env python3
import argparse
import json
import socket
import sys


def parse_args():
    parser = argparse.ArgumentParser(description="Receive JSON payloads over UDP")
    parser.add_argument("--host", default="0.0.0.0", help="Bind host")
    parser.add_argument("--port", type=int, default=9999, help="Bind UDP port")
    return parser.parse_args()


def main():
    args = parse_args()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((args.host, args.port))
    print("Listening on udp://{}:{}...".format(args.host, args.port))

    while True:
        data, addr = sock.recvfrom(65535)
        text = data.decode("utf-8", errors="replace")
        try:
            payload = json.loads(text)
            print("{} -> {}".format(addr, json.dumps(payload, ensure_ascii=False)))
        except Exception as exc:
            print("{} -> Invalid JSON: {} ({})".format(addr, text, exc), file=sys.stderr)


if __name__ == "__main__":
    main()
