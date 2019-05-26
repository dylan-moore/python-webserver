import socket
import time
import json
import os
import re

class webserver:
    def __init__(self, configLocation):
        try:
            with open(configLocation) as cfg:
                self.config = json.load(cfg)
        except:
            print(f"Could not load the config, are you sure {configLocation} exists?")
            exit()
        self.parsedHeaders = {}
        self.cache = {}
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(("localhost", self.config["port"]))
        self.s.listen(5)

    def handleClient(self):
        bufSize = self.config["buffersize"]*1024
        data = self.conn.recv(bufSize).decode(errors="ignore")
        if not data:
            return
        self.parseHeaders(data)
        if self.parsedHeaders["method"] == "GET":
            response = self.genHeaders(200)
            route = self.getRoute()
            if not route:
                self.conn.close()
                return
            response += route
            #self.logMessage("Handled {} : {}".format(self.addr, requestedPage))

        self.conn.send(response)
        self.conn.close()

    def getRoute(self):
        route = self.parsedHeaders["route"]
        if route in self.config["redirects"].keys():
            route = self.config["redirects"][route]
        path = os.path.join(self.config["fileslocation"], route)
        if self.config["scripting"]:
            routeContents = self.readFile(path, False)
            if routeContents:
                local = {}
                pattern = re.compile(r"(<py>(.*?)</py>)", flags=(re.S | re.M | re.I))
                for (m1,m2) in re.findall(pattern, routeContents):
                    exec(m2.strip(),{"headers":self.parsedHeaders},local)
                    if "res" in local.keys():
                        routeContents = routeContents.replace(m1, str(local["res"]) )
                    local["res"] = None
                return routeContents.encode()
            else:
                return None
        else:
            return self.readFile(path, True)

    def readFile(self, file, raw=True):
        try:
            with open(file, "rb") as fileHandle:
                file = fileHandle.read()
                if raw:
                    return file
                else:
                    return file.decode()
        except:
            return None

    def logMessage(self, message, error=False, fatal=False):
        formattedMessage = "[{}][{}] {}\n".format(error and "ERROR" or "MESSAGE", self.timeNow, message)
        print(formattedMessage.strip())
        if fatal and not self.config["logging"]["onlyfatal"]:
            try:
                with open(self.config["logging"]["logfile"],"a") as fileHandle:
                    fileHandle.write(formattedMessage)
            except:
                print("Failed to log to file.")
        if fatal: exit()

    def genHeaders(self, responseCode):
        return f"HTTP/1.1 {responseCode}\nDate: {self.timeNow()}\nServer: DSS\nConnection: close\n\n".encode()

    def parseHeaders(self, data):
        headersSplit = data.split("\r\n")
        routeSplit = headersSplit[0].split(" ")
        self.parsedHeaders["method"] = routeSplit[0]
        self.parsedHeaders["route"] = routeSplit[1]
        if self.config["scripting"]: # we only really need the other headers if we are scripting...
            for header in headersSplit[1:]:
                if header: # Dont do this....
                    headerSplit = header.split(":")
                    self.parsedHeaders[headerSplit[0].lower().replace('-',"_")] = headerSplit[1].strip()

    def timeNow(self):
        return time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

    def clientLoop(self):
        self.conn, self.addr = self.s.accept()
        self.handleClient()

ws = webserver("config.json")

while True:
    ws.clientLoop()
			