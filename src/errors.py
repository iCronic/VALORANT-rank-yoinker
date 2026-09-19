import socket
import os.path
import time
import os

class Error:
    
    def __init__(self, log, acc_manager):
        self.log = log
        self.acc_manager = acc_manager

    def PortError(self, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind(("127.0.0.1", port))
        except:
            print("""vRY is being blocked by the firewall!!
            - Check your firewall settings and whitelist the program / disable firewall
            - Try Restarting vRY and/or VALORANT, if non works try restarting your computer
            - If you have a slower internet connection, changing the value of cooldown located in config.json to 0 or any number greater than 1 may help.
            - If that doesn't work then changing the port number located in config.json file may work.
            - If all the above mentioned steps does not work, please join the support server!. 
            """)
            self.log("Port is being blocked by the firewall or in use by another application")
        sock.close()

    def ServerError(self, server_type, port, error):
        address_in_use = getattr(error, "winerror", None) == 10048 or getattr(
            error, "errno", None
        ) in (48, 98, 10048)
        reason = "the port is already in use" if address_in_use else str(error)
        print(
            f"Unable to start the {server_type} server on port {port}: {reason}"
        )
        self.log(
            f"Failed to start {server_type} server on port {port}: "
            f"{type(error).__name__}: {error}"
        )

    def LockfileError(self, path, ignoreLockfile=False):
        #ignoring lockfile is for when lockfile exists but it's not really valid, (local endpoints are not initialized yet)
        if os.path.exists(path) and ignoreLockfile == False:
            return True
        else:
            self.log("Lockfile does not exist, VALORANT is not open")
            self.acc_manager.start_valorant()
            
            while not os.path.exists(path):
                time.sleep(1)
            os.system('cls')
            return True
