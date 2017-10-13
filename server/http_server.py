import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from urllib.parse import urlparse

class RequestHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        print("do_get")
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        response = {"teste" : "asdasd", "a": False}
        self.wfile.write(bytes(str(response), "utf-8"))

        return
        
    def do_POST(self):
        print("do_post")
        content_length = self.headers.get('content-length')
        length = int(content_length[0]) if content_length else 0
        data = self.rfile.read(length)

        print("Data received: " + str(data))


        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(bytes("teste", "utf-8"))
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
