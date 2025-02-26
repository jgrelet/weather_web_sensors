import machine, sys
import web_app
try:
    web_app.main()
except Exception as e:
    print("Fatal error in main:")
    sys.print_exception(e)

# Following a normal Exception or main() exiting, reset the board.
# Following a non-Exception error such as KeyboardInterrupt (Ctrl-C),
# this code will drop to a REPL. Place machine.reset() in a finally
# block to always reset, instead.
machine.reset()