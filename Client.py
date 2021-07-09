import socket, sys

## Socket info
_LOCALIP = socket.gethostname() # Client IP
_LOCALPORT = 6789 # Port to send and listen
_BUFFERSIZE = 4096 # Size of the buffer, might need to be an array

def main():
    userClient = Client(_LOCALIP, _LOCALPORT)
    userClient.LiveUser()

## Client Side
class Client:
    # See this as a private/protected initialization
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def LiveUser(self):

        self.sock.sendto(bytes("Initialized", "utf-8"), (_LOCALIP, _LOCALPORT))
            
        while(True):
            
            data, addr = self.sock.recvfrom(_BUFFERSIZE)

            dData = data.decode()
            print(data.decode())
            
            msg = input("-> ")

            self.sock.sendto(bytes(msg, "utf-8"), (_LOCALIP, _LOCALPORT))

            if (msg == "Logout"):
                logout = True
                
                data, addr = self.sock.recvfrom(_BUFFERSIZE)

                dData = data.decode()
                
                if (logout == True and dData == "Farewell"):
                    self.sock.close()
                    sys.exit(0)
        
if __name__ == "__main__":
    main()
