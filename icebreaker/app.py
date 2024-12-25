import socket
import threading
import http.server
import socketserver
import json
from collections import defaultdict
import time

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
            'data': []
        }
    
    try:
        client_socket.send(b"Welcome to the ice breaker server! Note that everything you enter here will appear on the screen in the front, so don't put anything you don't want publicly listed. What is your name? ")
        name = client_socket.recv(1024).decode().strip()
        connection_data[client_address]['data'].append(f'Name: {name}')
        
        client_socket.send(b"What is your year and major? ")
        major = client_socket.recv(1024).decode().strip()
        connection_data[client_address]['data'].append(f'Major: {major}')
        
        client_socket.send(b"Nice! Now, open port 2222. I'll be trying to connect to your port 2222 repeatedly to send some important information.\n")
        connection_data[client_address]['status'] = 'outgoing_connection'
        client_socket.close()
        
        while True:
            try:
                follow_up = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                follow_up.connect((client_address[0], 2222))
                large_text = "This is a large block of text " * 100
                follow_up.send(large_text.encode())
                follow_up.close()
                break
            except ConnectionRefusedError:
                time.sleep(1)
                continue
            
    except Exception as e:
        print(f"Error handling client {client_address}: {e}")
    finally:
        with connection_lock:
            connection_data[client_address]['status'] = 'closed'

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
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }
                h2 {
                    color: #333;
                    text-align: center;
                    padding: 20px 0;
                    border-bottom: 2px solid #ddd;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    background-color: white;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.2);
                }
                th {
                    background-color: #4CAF50;
                    color: white;
                    padding: 12px;
                    text-align: left;
                }
                td {
                    padding: 12px;
                    border-bottom: 1px solid #ddd;
                }
                tr:hover {
                    background-color: #f5f5f5;
                }
                .status-open {
                    background-color: #90EE90;
                    padding: 5px 10px;
                    border-radius: 4px;
                }
                .status-closed {
                    background-color: #D3D3D3;
                    padding: 5px 10px;
                    border-radius: 4px;
                }
                .status-outgoing_connection {
                    background-color: #FFFFBF;
                    padding: 5px 10px;
                    border-radius: 4px;
                }
                .data-cell {
                    max-width: 300px;
                    overflow-wrap: break-word;
                }
            </style>
            <script>
                function updateTable() {
                    fetch('/data')
                        .then(response => response.json())
                        .then(data => {
                            const tbody = document.getElementById('connectionTable').getElementsByTagName('tbody')[0];
                            tbody.innerHTML = '';
                            
                            data.forEach(conn => {
                                const row = tbody.insertRow();
                                row.innerHTML = `
                                    <td>${conn.ip}</td>
                                    <td>${conn.timestamp}</td>
                                    <td><span class="status-${conn.status}">${conn.status}</span></td>
                                    <td class="data-cell">${conn.data.join('<br>')}</td>
                                `;
                            });
                        });
                }
                
                // Update every second
                setInterval(updateTable, 1000);
                
                // Initial update
                document.addEventListener('DOMContentLoaded', updateTable);
            </script>
        </head>
        <body>
            <h2>Connect to {{LOCAL_IP}}:1111</h2>
            <table id="connectionTable">
                <thead>
                    <tr>
                        <th>Source</th>
                        <th>Time</th>
                        <th>Status</th>
                        <th>Data</th>
                    </tr>
                </thead>
                <tbody></tbody>
            </table>
        </body>
        </html>
        """.replace("{{LOCAL_IP}}", LOCAL_IP)
        self.wfile.write(html.encode())

def start_tcp_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 1111))
    server.listen(5)
    
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