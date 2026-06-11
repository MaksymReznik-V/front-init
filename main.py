import urllib.parse
import mimetypes
import pathlib
import socket
import threading
import json

from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler


HTTP_PORT = 3000
UDP_PORT = 5000


class HttpHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)

        if pr_url.path == '/':
            self.send_html_file('index.html')

        elif pr_url.path == '/message':
            self.send_html_file('message.html')

        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html',404)

    def do_POST(self):
        data = self.rfile.read(
            int(self.headers['Content-Length'])
        )

        sock = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM
        )

        sock.sendto(data, ("localhost", UDP_PORT))

        self.send_response(302)
        self.send_header('Location','/')
        self.end_headers()

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type','text/html')
        self.end_headers()

        with open(filename, 'rb') as fb:
            self.wfile.write(fb.read())

    def send_static(self):
        self.send_response(200)

        _, mt = mimetypes.guess_type(self.path)

        if mt:
            self.send_header('Content-type', mt)
        else:
            self.send_header('Content-type','text/plain')

        self.end_headers()

        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', HTTP_PORT)

    http = server_class(
        server_address,
        handler_class
    )

    try:
        http.serve_forever()

    except KeyboardInterrupt:
        http.server_close()


def run_socket_server():
    print("UDP server started on 5000")
    STORAGE_FILE = pathlib.Path('storage/data.json')

    sock = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    sock.bind(('localhost', UDP_PORT))

    while True:
        data, address = sock.recvfrom(1024)

        current_time = str(datetime.now())

        decode_data = urllib.parse.unquote_plus(
            data.decode()
        )

        sock_dict = {
            key:value
            for key, value in (
                el.split('=')
                for el in decode_data.split('&')
            )
        }

        with open(STORAGE_FILE, 'r') as fh:
            data = json.load(fh)

        data[current_time] = sock_dict

        with open(STORAGE_FILE, 'w', encoding='utf-8') as file_w:
            json.dump(
                data,
                file_w,
                ensure_ascii=False,
                indent=4
            )


if __name__ == '__main__':
    http_thread = threading.Thread(target=run)
    socket_thread = threading.Thread(target=run_socket_server)

    http_thread.start()
    socket_thread.start()
