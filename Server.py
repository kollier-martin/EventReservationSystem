import random, socket, sys, operator, pathlib, os

## List of commands
_COMMANDS = ["Login", "Logout", "View Events", "Commands", "Help", "Purchase Tickets", "Print Records", "Display Profile", "Add Points"]

## Socket info
_LOCALIP = socket.gethostname() # Client IP
_LOCALPORT = 6789 # Port to send and listen
_BUFFERSIZE = 4096 # Size of the buffer

## List of Events
_EVENTS = []

## User Info ( User Class : User ID ) Dictionary
_USERS = {}

# Main Function
def main():
    userServer = Server(_LOCALIP, _LOCALPORT)
    userServer.Live()

## User Class
class User:
    # Constructor for User Class
    def __init__(self, username, password, points, purchasedTickets):
        self.username = username
        self.password = password
        self.points = points
        self.purchasedTickets = purchasedTickets
        self.purchaseHistory = ""

    def getName(self):
        return self.username

    # Returns current point balance
    def getPoints(self):
        return self.points

    # Prints the User Profile Data
    def printData(self):
        return("Username: " + self.username + "\nPoints: " + str(self.points) + "\nTickets Purchased: " + str(self.purchasedTickets))

    # Update points after purchase or after point addition
    def updatePoints(self, newPoints):
        tempPoints = self.points + newPoints

        # Lets user know that their balance doesn't cover the cost of the event
        if (tempPoints < 0):
            return ("Your current balance is insufficient for this purchase.")

        else:
            self.points = tempPoints
            return ("Points have been updated.")

    # Update the amount of tickets purchased
    def updatePTickets(self, newPTickets):
        self.purchasedTickets += newPTickets

    # Sets new password for current user
    def newPword(self, newPassword):
        self.password = newPassword
        return self.points

    # Returns password
    def getPassword(self):
        return self.password

    # Pass event information as argument, then add to string
    def updatePurchases(self, eventInfo):
        self.purchaseHistory += (eventInfo + "\n")

    # Returns purchase history
    def printPurchases(self):
        if (len(self.purchaseHistory) == 0):
            return "There are no past purchases on this account."

        else:
            return self.purchaseHistory

## Event Class
class Event:
    # Constructor for Event Class
    def __init__(self, name, TSeats, ASeats, cost):
        self.name = name
        self.TSeats = TSeats
        self.ASeats = ASeats
        self.cost = cost

    # Returns the event info
    def toString(self):
        return (self.name + " - Total # of Seats: " + str(self.TSeats) + " - Avaialable # of Seats: " + str(self.ASeats) + " - Cost: " + str(self.cost))

    # Returns Event Name
    def getName(self):
        return self.name

    # Returns Total Seats
    def getTSeats(self):
        return self.TSeats

    # Returns Available Seats
    def getASeats(self):
        return self.ASeats

    # Return Cost of Event
    def getCost(self):
        return self.cost

## Server Side
class Server:
    # Constructor for Server Class
    def __init__(self, host , port):
        # Connection info
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = host
        self.port = port

        ## Keeps up with the current user
        self.CurrentUser = None

        ## Store Events with File Reading, then Closes File
        with open(os.path.join(pathlib.Path(__file__).parent.absolute(), "EventInformation.txt"), 'r') as f:
            for line in f.readlines():
                info = line.strip().split()
                
                E = Event((info[0]+info[1]), int(info[6]), int(info[11]), int(info[16]))
                _EVENTS.append(E)

        f.close()

        ## Store Users with File Reading, then Closes File
        with open(os.path.join(pathlib.Path(__file__).parent.absolute(), "UserInformation.txt"), 'r') as f:
            for line in f.readlines():
                info = line.strip().split()

                U = User(info[0], info[2], int(info[4]), int(info[6]))
                _USERS.update({U:U.getName()})

        f.close()

    # Method to create a server instance
    def Live(self):
        try:
            # Socket creation and binding
            HOST = socket.gethostbyname(self.host)

            # SS = Server Socket
            self.sock.bind((HOST, self.port))

        except BaseException as e:
            # Scream for help if there's an error
            print (e)
            print ("The server failed to initialize and bind it's socket! Help me!")

        else:
            print ("Ready to receive.")
            
            # Listen for incoming data
            while True:
                # The packet receives the data from the client
                recBytes, addr = self.sock.recvfrom(_BUFFERSIZE)

                if(recBytes):
                    # The message from the Client
                    msg = recBytes.decode()
                    print("Client Message: ", msg)

                    # Indicates that the Client has connected to the server
                    if msg == "Initialized":
                        # Print Main Menu
                        self.mainMenu(addr)

                        # Prevents 'Invalid Command' message
                        recBytes, addr = self.sock.recvfrom(_BUFFERSIZE)
                        msg = recBytes.decode()

                    # Displays usable commands
                    if msg == "Commands" or msg == "Help":
                        tmp = "\n"
                        self.sock.sendto(bytes(tmp.join(_COMMANDS), "utf-8"), (addr))

                    # Prompts and handles the login process
                    if msg == "Login":
                        if len(_USERS) == 0:
                            self.sock.sendto(bytes("This database is empty. Why don't you create an account first :)", "utf-8"), (addr))

                        else:
                            self.sock.sendto(bytes("Please provide your username: ", "utf-8"), (addr))
                            username, addr = self.sock.recvfrom(_BUFFERSIZE)
                            self.ReturningUser(username.decode(), addr)

                    # Create new account
                    if msg == "Create":
                        self.NewUser(addr)

                    # Indicates which commands can be used while logged out        
                    elif (msg in _COMMANDS) and (self.CurrentUser == None) and (msg != "Login") and (msg != "Help") and (msg != "Create"):
                        self.sock.sendto(bytes("You must login to use this command.", "utf-8"), (addr))

                    # If there is a user logged in, these commands become available
                    if (self.CurrentUser != None):
                        # Prints current events
                        if msg == "View Events":
                            self.viewEvents(addr)

                        # Prompts and handles Ticket Purchases
                        if msg == "Purchase Tickets":
                            self.viewEvents(addr)
                            self.purchaseTicket(addr)

                        # Logs current user out
                        if msg == "Logout":
                            self.sock.sendto(bytes("Farewell", "utf-8"), (addr))
                            self.Logout(addr)

                        # Displays past purchases
                        if msg == "Print Records":
                            self.sock.sendto(bytes(self.CurrentUser.printPurchases(), "utf-8"), (addr))

                        # Displays user information
                        if msg == "Display Profile":
                            if (self.CurrentUser == None):
                                self.sock.sendto(bytes("You are not logged in, so there is no information to display.", "utf-8"), (addr))

                            elif (self.CurrentUser != None):
                                self.sock.sendto(bytes(self.CurrentUser.printData(), "utf-8"), (addr))
                        # Asks user how many points to add, then calls the proper function
                        if msg == "Add Points":
                            self.sock.sendto(bytes("Insert amount of points to add: ", "utf-8"), (addr))

                            tmp = self.sock.recvfrom(_BUFFERSIZE)
                            points = tmp[0].decode()

                            self.addPoints(int(points), addr)

                        # If command is invalid, let user know
                        elif (msg in _COMMANDS) == False:
                            print(msg, msg in _COMMANDS)
                            self.sock.sendto(bytes("That is an invalid command. Try again!", "utf-8"), (addr))

    
## Main Menu
    def mainMenu(self, addr):
        menuTxt = ("WELCOME TO THE ONLINE TICKET PURCHASING PROGRAM\nCommands:"+"\n\t ".join(_COMMANDS)+"\nAre you a returning user? Y/N")
        self.sock.sendto(bytes(menuTxt, "utf-8"), (addr))

        usr, addr = self.sock.recvfrom(_BUFFERSIZE)
        User_Login = usr.decode()

        # Takes user input to see how to handle the main menu login process
        if User_Login == "N" or User_Login == "n":
            self.sock.sendto(bytes("Would you like to create an account? ", "utf-8"), (addr))

            ca, addr = self.sock.recvfrom(_BUFFERSIZE)
            CreateAccount = ca.decode()

            if CreateAccount == "Y" or CreateAccount == "y":
                self.NewUser(addr)

            if CreateAccount == "N" or CreateAccount == "n":
                self.sock.sendto(bytes("No worries! Type 'Login' or 'Create' whenever you are ready", "utf-8"), (addr))

        if User_Login == "Y" or User_Login == "y":
            self.sock.sendto(bytes("Please input your username:", "utf-8"), (addr))
            User_Login, addr = self.sock.recvfrom(_BUFFERSIZE)
            self.ReturningUser(User_Login.decode(), addr)

        else:
            self.sock.sendto(bytes("You have input an invalid value. Use 'Help' for more info.", "utf-8"), (addr))

## New User Method                
    def NewUser(self, addr):
        ## Provide account username
        self.sock.sendto(bytes("Enter the username you would to register: ", "utf-8"), (addr))

        newU, addr = self.sock.recvfrom(_BUFFERSIZE)
        NewUsername = newU.decode()

        ## Provide account pword
        self.sock.sendto(bytes("Enter the password for your account: ", "utf-8"), (addr))

        newP, addr = self.sock.recvfrom(_BUFFERSIZE)
        NewPassword = newP.decode()

        with open(os.path.join(pathlib.Path(__file__).parent.absolute(), "UserInformation.txt"), 'a+') as f:
            f.write("\n" + NewUsername + " | " + NewPassword + " | " + "500 | 0")
        f.close

        ## Initialize User
        NewUser = User(NewUsername, NewPassword, 500, 0)

        ## add user to dictionary with their name as an indicator to their data
        _USERS[NewUser] = NewUsername

        self.sock.sendto(bytes("Account Creation Successful. Type 'Login' to login.", "utf-8"), (addr))

        ## WILL BE USING FILES FOR USERS INSTEAD

## Returning User Method
    def ReturningUser(self, string, addr):
        # Parses the list containing
        match = False
        if len(_USERS) > 0:
            for usr, name in _USERS.items():
                if name == string:
                    self.sock.sendto(bytes("Please enter your password: ", "utf-8"), (addr))
                    password = self.sock.recvfrom(_BUFFERSIZE)
                    password = password[0].decode()

                    match = (password == usr.getPassword())

                    while (not (match)):
                        match = (password == usr.getPassword())
                        if (match == True):
                            self.sock.sendto(bytes("Login successful!", "utf-8"), (addr))
                            self.CurrentUser = usr
                            break
                        
                        self.sock.sendto(bytes("This password is incorrect! Try again.", "utf-8"), (addr))
                        password, addr = self.sock.recvfrom(_BUFFERSIZE)
                        password = password.decode()

                    else:
                        self.sock.sendto(bytes("Login successful!", "utf-8"), (addr))
                        self.CurrentUser = usr
                        
                elif name != string and match != True:
                    self.sock.sendto(bytes("This username is not in the database.\nMain Menu.", "utf-8"), (addr))
                    break
## View Events Function
    def viewEvents(self, addr):
        Events = []
        for i in range(len(_EVENTS)):
            Events += (_EVENTS[i].toString() + "\n")
            
        self.sock.sendto(bytes("".join(Events), "utf-8"), (addr))

## Add points to current user's account
    def addPoints(self, numPoints, addr):
        # Store old points
        oldPoints = self.CurrentUser.points

        # Inform server of user point increase
        self.CurrentUser.updatePoints(numPoints)

        # Display new user point total
        newPoints = self.CurrentUser.points
        self.sock.sendto(bytes(("Old: " + str(oldPoints) + "\nNew: " + str(newPoints)), "utf-8"), (addr))

## Purchase Tickets
    def purchaseTicket(self, addr):
        # Dependent on tickets the user decides to purchase
        self.sock.sendto(bytes("What event would you like to purchase a ticket for?", "utf-8"), (addr))

        event, addr = self.sock.recvfrom(_BUFFERSIZE)
        cEvent = event.decode()

        for i in range(len(_EVENTS)):
            if (cEvent == _EVENTS[i].getName()):
                self.CurrentUser.updatePoints(self.CurrentUser.getPoints() - _EVENTS[i].getPoints())
                self.CurrentUser.updatePTickets(1)
                self.CurrentUser.updatePurchases(_EVENTS[i].toString())

                self.sock.sendto(bytes("Purchase complete. Use 'Print Records' to view purchase", "utf-8"), (addr))
            else:
                self.sock.sendto(bytes("That is an invalid option.\nMain Menu.", "utf-8"), (addr))
            

## Logout
    def Logout(self, addr):
        # Query
        self.sock.sendto(bytes("Are you sure you want to logout? ", "utf-8"), (addr))
        
        # Server recieves client farewell
        self.CurrentUser = None

## Initiates script
if __name__ == "__main__":
    main()
