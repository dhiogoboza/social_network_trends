import charts

import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from urllib.parse import urlparse

client_dir = "../client/"

mime_types = {
    "jpg" : "image/jpg",
    "svg" : "image/svg+xml",
    "png" : "image/png",
    "ico" : "image/x-icon",
    "html": "text/html",
    "js"  : "text/javascript",
    "css" : "text/css"
}

class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        print("do_get")
        
        '''
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        response = {"teste" : "asdasd", "a": False}
        self.wfile.write(bytes(str(response), "utf-8"))
        '''
        
        page = self.path
        if (page == "/"):
            page = "index.html"

        page_array = page.split(".")
        ext = page_array[len(page_array) - 1]
        
        f = open(client_dir + page, "rb")
        self.send_response(200)
        self.send_header('Content-type', mime_types[ext])
        self.end_headers()
        self.wfile.write(f.read())
        f.close()

        return
        
    def do_POST(self):
        print("do_post")
        
        content_length = self.headers.get('content-length')
        length = int(content_length[0]) if content_length else 0
        data = self.rfile.read(length)

        print("Data received: " + str(data))


        #self.send_response(200)
        #self.send_header('Access-Control-Allow-Origin', '*')
        #self.end_headers()
        #self.wfile.write(bytes("teste", "utf-8"))
        
        #f = open("zne_icon.png", "rb")
        self.send_response(200)
        self.send_header('Content-type', 'image/png')
        self.end_headers()
        #self.wfile.write(base64.b64encode(f.read()))
        self.wfile.write(charts.get_chart(data))
        f.close()
        
        #self.wfile.close()
    
        
def main():
    if (len(sys.argv) > 1):
        port = int(sys.argv[1])
    else:
        port = 8080

    print('Listening on localhost: '  + str(port))

    server = HTTPServer(('', port), RequestHandler)
    server.serve_forever()

        
if __name__ == "__main__":
    main()
