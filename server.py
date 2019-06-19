import socket
import time
import json
import os
import re
import sys
import asyncio
import gzip

class webserver:
    # Init method, for OOP variable declaration and config loading.
    def __init__(self, configLocation):
        # Load in config
        try:
            with open(configLocation) as cfg:
                self.config = json.load(cfg)
        except:
            print(f"Could not load the config, are you sure {configLocation} exists?")
            exit()

        # Declerations
        self.cache = {}
        self.inlinePattern = re.compile(r"<py>((.|\n)*?)</py>", flags=(re.S | re.M | re.I))

        # Start server
        asyncio.run(self.startListener())

    # This method contains the limitless loop that will handle incoming connections.
    async def startListener(self):
        # Definition
        ssl = None

        # Create SSL context if required
        if self.config["ssl_enable"]:
            ssl = ssl.SSLContext()
            ssl.verify_mode = ssl.CERT_REQUIRED
            ssl.check_hostname = True
            ssl.load_verify_locations(self.config["ssl_cert"])

        # Create the async listener
        server = await asyncio.start_server(self.handleClient, '127.0.0.1', 8888, ssl=ssl)
        addr = server.sockets[0].getsockname()
        async with server:
            await server.serve_forever()

    # This method handles the client as it is received from the server.
    async def handleClient(self, reader, writer):
        # Declerations
        result = bytearray()
        resultHeader = bytearray()
        resultCode = 200
        resultHeaderextras = ""

        # Parsing
        readData = await reader.read(self.config["buffer_size"]*1024)
        decodedData = readData.decode(errors="ignore")
        parsedHeaders = await self.parseHeaders(decodedData)
        readAddr = writer.get_extra_info("peername")

        # Handling the route
        resultCode, result = await self.handleRoute(decodedData, parsedHeaders)

        # Compress if needed
        if self.config["gzip_compress"] and "gzip" in parsedHeaders["accept-encoding"]:
            result = gzip.compress(result)
            resultHeaderextras += "Content-Encoding: gzip\n"

        # Build header
        resultHeader = f"HTTP/1.1 {resultCode}\nDate: {await self.timeNow()}\nServer: Dylan's simple web server\n{resultHeaderextras}Connection: close\n\n".encode()

        # Return data and close writer
        writer.write(resultHeader + result)
        await writer.drain()
        writer.close()

    # This method handles specific routes, returns the responce code and responce body.
    async def handleRoute(self, data, headers):
        # Declerations
        fileContents = bytearray()
        route = headers["route"]

        # Handling redirects        
        if route in self.config["files_redirect"].keys():
            route = self.config["files_redirect"][route]

        # path join does not seem to like '/file'
        if route[0] == "/": route = route[1:]

        # Getting routes filepath
        path = os.path.join(self.config["files_location"], route)

        # Trying to read route contents
        fileContents = await self.handleCache(path)
        if not fileContents:
            return await self.raiseError(404, route)

        # If we whave scripting set to false or loading a non html file
        if not self.config["scripting_enable"] or not route.endswith("html"):
            return 200, fileContents

        decodedContents = fileContents.decode()
            
        # Running scripting
        local = {}
        script = ""
        for (m1,m2) in re.findall(self.inlinePattern, decodedContents):
            script += f"{m1}\n"
    
        try:
            exec(script, {"headers": headers}, local)
        except SyntaxError as err:
            return await self.raiseError(502, route, err)
        decodedContents = decodedContents.replace(m1, str(local["res"]) if "res" in local.keys() else "")

        return 200, decodedContents.encode()

    # This method checks to see if something exists in the cache, if it does not it reads, stores and returns what the caller was looking for.
    async def handleCache(self, location):
        # For shorthanding.
        ce = self.config["cache_enable"]

        # Check if already exists, if so return it.
        if location in self.cache.keys() and ce:
            return self.cache[location]

        try:
            with open(location, "rb") as file:
                contents = file.read()
                if ce: self.cache[location] = contents
                return contents
        except (FileNotFoundError, IOError):
            return None

    # This method is for parsing the header into a dictionary.
    # There is probably a more efficient way of doing this, so it will need to be looked into in the future.
    async def parseHeaders(self, data):
        headers = {}
        headersSplit = data.split("\r\n")
        routeSplit = headersSplit[0].split(" ")
        headers["method"] = routeSplit[0]
        headers["route"] = routeSplit[1]
        if self.config["scripting_enable"]:
            for header in headersSplit[1:]:
                if header:
                    headerSplit = header.split(":")
                    headers[headerSplit[0].lower()] = headerSplit[1].strip()
        return headers

    # This method is for raise errors, allows for shorthand error handing.
    async def raiseError(self, errorCode, route, errorContents='Route not found.'):
        return errorCode, f"<h1>Error {errorCode}</h1>Route: <p>{route}</p><p>Error: {errorContents}</p>".encode()

    # This method allows for safe error logging to file and console.
    # Needs some fixing and cleaning up.
    async def logMessage(self, message, error=False, fatal=False):
        formattedMessage = "[{}][{}] {}\n".format("ERROR" if error else "MESSAGE", await self.timeNow(), message)
        print(formattedMessage.strip())
        if fatal and not self.config["logging"]["onlyfatal"]:
            try:
                with open(self.config["logging"]["logfile"], "a") as fileHandle:
                    fileHandle.write(formattedMessage)
            except:
                print("Failed to log to file.")
        if fatal: exit()

    # This method returns a nicely formatted date and time.
    async def timeNow(self):
        return time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

if __name__ == '__main__':
    webserver(sys.argv[1] if len(sys.argv) > 1 else "config.json")