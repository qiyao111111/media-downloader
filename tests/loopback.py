"""Test-only forwarding proxies and Cookie-gated media server; no production service."""

import base64
import contextlib
import http.server
import select
import socket
import socketserver
import struct
import threading
from urllib.parse import urlsplit

USER, PASSWORD = b'audit-user', b'local-test-only'


def read_exact(sock, count):
    data = b''
    while len(data) < count:
        chunk = sock.recv(count-len(data))
        if not chunk:
            raise EOFError()
        data += chunk
    return data


def relay(left, right):
    with right:
        while True:
            readable, _, _ = select.select([left, right], [], [], 30)
            if not readable:
                return
            for source in readable:
                chunk = source.recv(65536)
                if not chunk:
                    return
                (right if source is left else left).sendall(chunk)


class Proxy(socketserver.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, socks=False):
        super().__init__(('127.0.0.1', 0), SocksHandler if socks else HttpHandler)
        self.records = []
        self.thread = threading.Thread(target=self.serve_forever, daemon=True)
        self.thread.start()

    def close(self):
        self.shutdown(); self.server_close(); self.thread.join()


class HttpHandler(socketserver.BaseRequestHandler):
    def handle(self):
        with contextlib.suppress(OSError, EOFError, ValueError):
            header = b''
            while b'\r\n\r\n' not in header:
                header += read_exact(self.request, 1)
                if len(header) > 32768:
                    return
            lines = header.decode('iso-8859-1').split('\r\n')
            method, target, version = lines[0].split(' ')
            auth = next((line.split(':',1)[1].strip() for line in lines if line.lower().startswith('proxy-authorization:')), '')
            expected = 'Basic ' + base64.b64encode(USER+b':'+PASSWORD).decode()
            if auth != expected:
                self.request.sendall(b'HTTP/1.1 407 Proxy Authentication Required\r\nProxy-Authenticate: Basic realm="audit"\r\nContent-Length: 0\r\n\r\n')
                return
            if method == 'CONNECT':
                host, port = target.rsplit(':', 1)
                remote = socket.create_connection((host, int(port)), timeout=15)
                self.request.sendall(b'HTTP/1.1 200 Connection established\r\n\r\n')
            else:
                parts = urlsplit(target)
                host, port = parts.hostname, parts.port or 80
                remote = socket.create_connection((host, port), timeout=15)
                lines[0] = f'{method} {parts.path or "/"}{"?"+parts.query if parts.query else ""} {version}'
                lines = [line for line in lines if not line.lower().startswith(('proxy-authorization:', 'proxy-connection:'))]
                remote.sendall('\r\n'.join(lines).encode('iso-8859-1'))
            self.server.records.append({'host': host, 'port': int(port), 'username_ok': True, 'password_ok': True})
            relay(self.request, remote)


class SocksHandler(socketserver.BaseRequestHandler):
    def handle(self):
        with contextlib.suppress(OSError, EOFError, ValueError):
            version, count = read_exact(self.request, 2)
            methods = read_exact(self.request, count)
            if version != 5 or 2 not in methods:
                self.request.sendall(b'\x05\xff'); return
            self.request.sendall(b'\x05\x02')
            version, length = read_exact(self.request, 2)
            user = read_exact(self.request, length)
            password = read_exact(self.request, read_exact(self.request, 1)[0])
            valid = user == USER and password == PASSWORD
            self.request.sendall(b'\x01\x00' if valid else b'\x01\x01')
            if not valid:
                return
            version, command, _, kind = read_exact(self.request, 4)
            if command != 1:
                return
            if kind == 1:
                host = socket.inet_ntoa(read_exact(self.request, 4))
            elif kind == 3:
                host = read_exact(self.request, read_exact(self.request,1)[0]).decode()
            elif kind == 4:
                host = socket.inet_ntop(socket.AF_INET6, read_exact(self.request,16))
            else:
                return
            port = struct.unpack('!H', read_exact(self.request,2))[0]
            remote = socket.create_connection((host,port), timeout=15)
            self.request.sendall(b'\x05\x00\x00\x01\x7f\x00\x00\x01\x00\x00')
            self.server.records.append({'host':host,'port':port,'username_ok':True,'password_ok':True,'address_type':kind})
            relay(self.request,remote)


class MediaServer(http.server.ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, media, require_cookie=False, slow=False):
        super().__init__(('127.0.0.1',0),MediaHandler)
        self.media, self.require_cookie, self.slow = media, require_cookie, slow
        self.requests_seen = []
        self.thread=threading.Thread(target=self.serve_forever,daemon=True);self.thread.start()

    def close(self):
        self.shutdown();self.server_close();self.thread.join()


class MediaHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self,*args):
        pass

    def do_GET(self):
        valid=self.headers.get('Cookie') == 'audit_session=controlled-test'
        self.server.requests_seen.append({'cookie_ok':valid,'ua_ok':self.headers.get('User-Agent')=='B01-test-agent'})
        if self.server.require_cookie and not valid:
            self.send_error(403);return
        if self.path.startswith('/fail'):
            self.send_error(500);return
        import time
        content=self.server.media.read_bytes()
        start=0
        if self.headers.get('Range'):
            start=int(self.headers['Range'].split('=')[1].split('-')[0])
        self.send_response(206 if start else 200)
        self.send_header('Content-Type','video/mp4')
        self.send_header('Content-Length',len(content)-start)
        self.send_header('Accept-Ranges','bytes')
        if start:self.send_header('Content-Range',f'bytes {start}-{len(content)-1}/{len(content)}')
        self.end_headers()
        with contextlib.suppress(OSError):
            for i in range(start,len(content),65536):
                self.wfile.write(content[i:i+65536]);self.wfile.flush()
                if self.server.slow:time.sleep(.05)
