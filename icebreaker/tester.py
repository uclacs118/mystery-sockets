import socket
import time
import random
import string
import threading

# Function to generate random strings (for name)
def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters, k=length))

# Function to simulate a random major
def random_major():
    majors = ['Computer Science', 'Mathematics', 'Physics', 'Engineering', 'Biology', 'Literature', 'History']
    return random.choice(majors)


# Function to run the server on port 2222
def start_2222_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 2222))
    server_socket.listen(1)
    print("Listening on port 2222...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection received from {client_address}")
        # Handle the incoming connection from the server on port 1111
        client_socket.recv(10000)
        time.sleep(random.randint(1, 10))

# Function to simulate the client
def simulate_client():

    # Connect to localhost on port 1111
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 1111))
    
    try:
        time.sleep(random.randint(0, 10))
        # Answer for name
        client_socket.recv(1024)  # Receive the first prompt for name
        name = random_string()
        print(f"Sending name: {name}")
        client_socket.send(name.encode())
        time.sleep(random.randint(0, 10))

        # Answer for year and major
        client_socket.recv(1024)  # Receive the prompt for major
        major = random_major()
        print(f"Sending major: {major}")
        client_socket.send(major.encode())
        time.sleep(random.randint(0, 10))

        # Wait for the next message about opening port 2222
        client_socket.recv(1024)
        
        time.sleep(random.randint(0, 10))

        # Allow the server some time to establish the connection on port 2222
        time.sleep(1)
        
        # At this point, the server on port 2222 will be handling connections from the server on port 1111.
        # No further action needed as the server is already running.
        
    except Exception as e:
        print(f"Error in simulate_client: {e}")
    finally:
        client_socket.close()


if __name__ == "__main__":

    # Start the 2222 server in a separate thread
    threading.Thread(target=start_2222_server, daemon=True).start()

    # Run the simulation 20 times
    threads = []
    for _ in range(20):
        threads.append(threading.Thread(target=simulate_client, daemon=True))
        threads[-1].start()

    for thread in threads:
        thread.join()

