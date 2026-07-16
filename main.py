import machine
import sys
import time

# An autonomous station must recover from transient sensor or bus startup failures.
AUTO_RESET_ON_FATAL = True
FATAL_RESET_DELAY_SECONDS = 10

try:
    import web_app

    web_app.main()
except KeyboardInterrupt:
    print("Stopped by user (KeyboardInterrupt).")
except Exception as e:
    print("Fatal error in main:")
    sys.print_exception(e) # pylint: disable=no-member
    if AUTO_RESET_ON_FATAL:
        print("Automatic reset in", FATAL_RESET_DELAY_SECONDS, "seconds")
        time.sleep(FATAL_RESET_DELAY_SECONDS)
        machine.reset()
else:
    # main() is expected to run forever. If it exits normally, restart the board.
    machine.reset()
