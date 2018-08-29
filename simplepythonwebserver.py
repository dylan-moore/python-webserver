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

# This webserver is vulnerable to the SlowLoris attack that Apache webservers are also vulnerable to.
# Basially, if you just send the webserver half a http request then one byte every so often (just to keep the connection alive) it will keep the handling _
# thread open which will eventually cause the webserver to not be able to handle any more clients.

bindIp = '127.0.0.1'
httpPort = 80
bufferSize = 128 * 1024
rootFolder = "www"

def getFile(file):
        fileHandle = open(file, "r")
        fileContents = fileHandle.read()
        fileHandle.close()
        return fileContents

def genHeaders(responseCode):
        header = ''
        if responseCode == 200:
            header += 'HTTP/1.1 200 OK\n'
        elif responseCode == 404:
            header += 'HTTP/1.1 404 Not Found\n'

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
        timerStart = int(time.time() * 1000)
        data = clientConnection.recv(bufferSize).decode()
        if not data:
            return
        
        responseHeader = ""
        responseData = ""

        requestMethod = parseHeader(data, "method")
        
        if requestMethod == "GET":
                responseHeader = genHeaders(200)
                requestedPage = parseHeader(data, "page")
                if requestedPage == "/":
                        responseData = getFile(rootFolder + "/index.html")
                else:
                        responseData = getFile(rootFolder + requestedPage)

        response = responseHeader.encode()
        if requestMethod == "GET":
                responseData = responseData
                responseData += "\n\nIt took a incredible " + str((time.time() * 1000)-timerStart) + "ms to generate this page"
                response += responseData.encode()
        conn.send(response)        
        conn.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((bindIp, httpPort))
s.listen(5)

while True:
        conn, addr = s.accept()
        threading.Thread(target=handleClient,args=(conn,)).start()

