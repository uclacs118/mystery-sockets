import socket
import threading
import http.server
import socketserver
import json
from collections import defaultdict
import time
import traceback

connection_data = defaultdict(dict)
connection_lock = threading.Lock()


def get_local_ip():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        # Doesn't have to connect to a valid server
        s.connect(("1.1.1.1", 80))
        local_ip = s.getsockname()[0]
    return local_ip

LOCAL_IP = get_local_ip()



def handle_tcp_client(client_socket, client_address):
    with connection_lock:
        connection_data[client_address] = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'open',
            'data': ["Name:", "Major:"]
        }
    
    try:
        client_socket.send(b"Welcome to the ice breaker server! Note that everything you enter here will appear on the screen in the front, so don't put anything you don't want publicly listed. What is your name? ")
        name = client_socket.recv(1024).decode().strip()
        connection_data[client_address]['data'][0] = (f'Name: {name}')
        connection_data[client_address]['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        client_socket.send(b"What is your year and major? ")
        major = client_socket.recv(1024).decode().strip()
        connection_data[client_address]['data'][1] = (f'Major: {major}')
        connection_data[client_address]['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        client_socket.send(b"Nice! Now, open port 2222. I'll be trying to connect to your port 2222 repeatedly to send some important information.\n")
        connection_data[client_address]['status'] = 'outgoing_connection'
        client_socket.close()
        
        while True:
            try:
                follow_up = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                follow_up.connect((client_address[0], 2222))
                large_text = "This is a large block of text " * 100
                follow_up.send(large_text.encode())
                connection_data[client_address]['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
                connection_data[client_address]['status'] = 'completed'
                follow_up.close()
                break
            except ConnectionRefusedError:
                time.sleep(1)
                continue
            except TimeoutError:
                time.sleep(1)
                continue
            except ConnectionResetError:
                time.sleep(1)
                continue
            except BrokenPipeError:
                time.sleep(1)
                continue
            
    except Exception as e:
        print(f"Error handling client {client_address}: {e}")
        print(traceback.format_exc())
        connection_data[client_address]['status'] = 'closed'
    # finally:
    #     with connection_lock:
    #         connection_data[client_address]['status'] = 'closed'

class HTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            with connection_lock:
                data_list = [
                    {
                        'ip': f"{addr[0]}:{addr[1]}", 
                        'timestamp': info['timestamp'],
                        'status': info['status'],
                        'data': info['data']
                    }
                    for addr, info in sorted(
                        connection_data.items(),
                        key=lambda x: x[1]['timestamp'],
                        reverse=True
                    )
                ]
            self.wfile.write(json.dumps(data_list).encode())
            return

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = """

        """.replace("{{LOCAL_IP}}", LOCAL_IP)

        with open("index.html", "rb") as f:
            self.wfile.write(f.read().replace(b"{{LOCAL_IP}}", str(LOCAL_IP).encode()))

        # self.wfile.write(html.encode())

def start_tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 1111))
    server.listen(1000)
    
    while True:
        client_sock, address = server.accept()
        client_thread = threading.Thread(target=handle_tcp_client, 
                                      args=(client_sock, address))
        client_thread.start()

def main():
    tcp_thread = threading.Thread(target=start_tcp_server)
    tcp_thread.daemon = True
    tcp_thread.start()
    
    http_server = socketserver.TCPServer(('0.0.0.0', 8080), HTTPRequestHandler, False)
    http_server.allow_reuse_address = True
    http_server.server_bind()
    http_server.server_activate()
    print("Servers started. HTTP server on port 8080, TCP server on port 1111")
    http_server.serve_forever()

if __name__ == '__main__':
    main()