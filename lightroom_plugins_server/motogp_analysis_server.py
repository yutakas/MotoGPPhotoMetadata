import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import analyze_motogp_image

class Path:
    PORCESSIMG = "/processimg"
    XML = "/xml"
    HEALTH = "/health"

class Server(HTTPServer):
    def __init__(self, address, request_handler):
        super().__init__(address, request_handler)
        self.path = Path()


class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server_class):
        self.server_class = server_class
        super().__init__(request, client_address, server_class)

    def do_GET(self):
        response = {"message": "Hello world"}
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Content-Length", str(len(json.dumps(response))))
        self.end_headers()
        self.wfile.write(str(response).encode('utf8'))

    def do_POST(self):
        if self.path == self.server_class.path.PORCESSIMG:
            print("Post Request Received")
            return self.process_img()

        # if self.path == self.server_class.path.XML:
        #     return self.store_xml_test_data()

        response = {"message": "Hello world"}
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Content-Length", str(len(json.dumps(response))))
        self.end_headers()
        self.wfile.write(str(response).encode('utf8'))

    def process_img(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        result = analyze_motogp_image.analyze_image_from_bytes(post_data)
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Content-Length", str(len(json.dumps(result))))
        self.end_headers()
        print("Response data: " + json.dumps(result))
        self.wfile.write(json.dumps(result).encode('utf8'))

def main():
    addr = "0.0.0.0"
    port = 8500
    http_server = Server((addr, port), RequestHandler)
    print(f"Starting server on {addr}:{port}")
    http_server.serve_forever()


if __name__ == "__main__":
    main()        