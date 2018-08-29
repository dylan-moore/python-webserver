import socket
import time
import threading

# Dylan's simple python web server, I chose to write a webserver because networking is really easy in python and webservers are incredibly simple.
# I could eventually accept parameters in to the request (this would let me create dynamic web pages. So things like logins, sessions etc.)

# The run down of how my webserver works :
# 1) Server listens for client.
# 2) Client connects and sends over HTTP header. This contains things such as which page they want to visit, their user agent etc.
# 3) The server recieves the clients http header and parses it. (extracts the information from the request)
# 4) The server sends over the page that the client has requested.
# 5) Connection terminates and client is left with a fully loaded webpage on their side.

bindIp = '127.0.0.1'
httpPort = 80
bufferSize = 128 * 1024
rootFolder = "www"

def getFile(file):
        try:
                fileHandle = open(file, "r")
                fileContents = fileHandle.read()
                fileHandle.close()
                return fileContents
        except:
                return False

def serverMessage(message, colour):     #will add more formatting later on
        return "<h3><font color='{col}'>{msg}</font></h3>".format(msg=message, col=colour)

def genHeaders(responseCode):
        header = ''
        if responseCode == 200:
                header += "HTTP/1.1 200 OK\n"
        elif responseCode == 404:
                header += "HTTP/1.1 404 Not Found\n"
        elif responseCode == 501:
                header += "HTTP/1.1 501 Not Implemented\n" 

        timeNow = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
        header += 'Date: {now}\n'.format(now=timeNow)
        header += 'Server: Dylans-Python-Webserver\n'
        header += 'Connection: close\n\n'
        return header

def parseHeader(header, param):
        header_array = header.split("\r\n")
        if param == "method":
                return header_array[0].split(" ")[0]
        elif param == "page":
                return header_array[0].split(" ")[1]
        else:
                for header_line in header_array:
                        param_split = header_line.split(":")
                        if param_split[0].lower() == param:
                                return param_split[1]

def handleClient(clientConnection):
        timerStart = time.time() * 1000
        data = clientConnection.recv(bufferSize).decode()
        if not data:
            return
        
        responseHeader = ""
        responseData = ""

        requestMethod = parseHeader(data, "method")
        
        if requestMethod == "GET":
                responseHeader = genHeaders(200)
                requestedPage = parseHeader(data, "page")
                print("A client requested : {req}\r\n".format(req=requestedPage))
                if requestedPage == "/":
                        responseData = getFile(rootFolder + "/index.html")
                else:
                        responseData = getFile(rootFolder + requestedPage)
        else:
                responseHeader = genHeaders(501)
                responseData = serverMessage("Unknown request method '{reqmethod}'".format(reqmethod=requestMethod), "red")      

        if responseData == False:
                responseHeader = genHeaders(404)
                responseData = serverMessage("Error 404, the page you are looking for cannot be found.", "red")

        response = responseHeader.encode()
        responseData = responseData
        timeTook = round((time.time() * 1000)-timerStart)
        responseData += "\n\nIt took a incredible {genin}ms to generate this page".format(genin=timeTook)
        response += responseData.encode()
        
        conn.send(response)
        conn.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((bindIp, httpPort))
s.listen(5)

while True:
        conn, addr = s.accept()
        threading.Thread(target=handleClient,args=(conn,)).start()
