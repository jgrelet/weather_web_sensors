import machine
import sys
import time
import web_app

# Keep USB serial stable on fatal errors while debugging.
AUTO_RESET_ON_FATAL = False

try:
    web_app.main()
except KeyboardInterrupt:
    print("Stopped by user (KeyboardInterrupt).")
except Exception as e:
    print("Fatal error in main:")
    sys.print_exception(e)
    if AUTO_RESET_ON_FATAL:
        time.sleep(2)
        machine.reset()
else:
    # main() is expected to run forever. If it exits normally, restart the board.
    machine.reset()
