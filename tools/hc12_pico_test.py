from machine import Pin, UART
import time

UART_ID = 0
TX_PIN = 0
RX_PIN = 1
BAUDRATE = 9600
SEND_INTERVAL_MS = 2000
MAX_RX_BUFFER_BYTES = 512

uart = UART(UART_ID, baudrate=BAUDRATE, tx=Pin(TX_PIN), rx=Pin(RX_PIN))
last_send = time.ticks_add(time.ticks_ms(), -SEND_INTERVAL_MS)
counter = 0
rx_buffer = bytearray()

print("HC-12 Pico test on UART{} TX=GP{} RX=GP{} baud={}".format(UART_ID, TX_PIN, RX_PIN, BAUDRATE))
print("Loop sends PING_PICO and replies ACK_PICO to complete PING_RPI lines.")

while True:
    now = time.ticks_ms()
    if time.ticks_diff(now, last_send) >= SEND_INTERVAL_MS:
        counter += 1
        message = "PING_PICO {} {}".format(counter, now)
        uart.write((message + "\n").encode())
        print("sent:", message)
        last_send = now

    if uart.any():
        chunk = uart.read()
        if chunk:
            rx_buffer.extend(chunk)

        while True:
            newline_index = rx_buffer.find(b"\n")
            if newline_index < 0:
                break

            line = bytes(rx_buffer[:newline_index])
            rx_buffer = rx_buffer[newline_index + 1 :]

            try:
                decoded = line.decode("utf-8").strip()
            except UnicodeError:
                decoded = line.decode("utf-8", "ignore").strip()

            if not decoded:
                continue

            print("received:", decoded)
            if decoded.startswith("PING_RPI"):
                response = "ACK_PICO {}".format(decoded)
                uart.write((response + "\n").encode())
                print("sent:", response)

        if len(rx_buffer) > MAX_RX_BUFFER_BYTES:
            print("discarded unterminated RX data:", len(rx_buffer), "bytes")
            rx_buffer = bytearray()

    time.sleep_ms(50)
