import socket
import threading
import random
import time
from flask import Flask, render_template_string, redirect
from dataclasses import dataclass
from typing import List, Dict
import logging
import concurrent.futures
import signal
import sys

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s')

@dataclass
class Player:
    name: str
    connection: socket.socket
    ip: str
    assigned_port: int = None
    team: int = None
    position: int = None

@dataclass
class Team:
    players: List[Player]
    submissions: List[tuple] = None
    team_port: int = None
    start_time: float = None

    def __post_init__(self):
        self.submissions = []

class GameServer:
    def __init__(self):
        self.players = []
        self.teams: Dict[int, Team] = {}
        self.game_started = False
        self.used_ports = set()
        self.server_ip = socket.gethostbyname(socket.gethostname())
        
    def get_random_port(self):
        while True:
            port = random.randint(2000, 65000)
            if port not in self.used_ports:
                self.used_ports.add(port)
                return port

    def handle_client(self, client_socket, address):
        client_socket.send(b"Enter first name: ")
        first_name = client_socket.recv(1024).decode().strip()
        # client_socket.send(b"Enter last name: ")
        # last_name = client_socket.recv(1024).decode().strip()
        last_name = " "
        
        player = Player(f"{first_name} {last_name}", client_socket, address[0])
        self.players.append(player)
        logging.info(f"Added player: {player.name}")

    def start_game(self):
        logging.info("Starting game")
        random.shuffle(self.players)
        now = time.time()
        
        num_teams = len(self.players) // 3
        for team_num in range(num_teams):
            team_players = self.players[team_num * 3:(team_num + 1) * 3]
            team = Team(team_players)
            team.team_port = self.get_random_port()
            team.start_time = now
            self.teams[team_num] = team
            
            for pos, player in enumerate(team_players):
                player.team = team_num
                player.position = pos
                player.assigned_port = self.get_random_port()
                
            for pos, player in enumerate(team_players):
                if pos == len(team_players) - 1:
                    # Last player connects back to game server
                    msg = f"Listen on port {player.assigned_port}\nConnect to game server at {self.server_ip}:{team.team_port}\n"
                else:
                    # Connect to next player
                    next_player = team_players[pos + 1]
                    msg = f"Listen on port {player.assigned_port}\nConnect to next player at {next_player.ip}:{next_player.assigned_port}\n"
                
                logging.debug(f"Sending to {player.name}: {msg.strip()}")
                player.connection.send(msg.encode())
        
        self.game_started = True
        threading.Thread(target=self.game_loop).start()

    def game_loop(self):
        while self.game_started:
            def send_to_team(team):
                first_player = team.players[0]
                while True:
                    time.sleep(1)
                    try:
                        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        client.connect((first_player.ip, first_player.assigned_port))
                        client.send(b"abracadabra\n")
                        client.close()
                        logging.debug(f"Sent word to {first_player.name} on port {first_player.assigned_port}")
                    except:
                        logging.debug(f"Error when sending word to {first_player.name} on port {first_player.assigned_port}")

            def recv_from_team(team):
                try:
                    team_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    team_socket.bind(('0.0.0.0', team.team_port))
                    team_socket.listen(1)
                    # team_socket.settimeout(10)
                    
                    while True:
                        try:
                            client, _ = team_socket.accept()
                            response = client.recv(1024).decode().strip()
                            elapsed = time.time() - team.start_time
                            team.submissions.append((response, elapsed, time.time()))
                            client.close()
                        except socket.timeout:
                            team.submissions.append(("timeout", time.time() - team.start_time, time.time()))
                except:
                    logging.debug(f"Error when trying to receive word from {team.team_port}")


            executor = concurrent.futures.ThreadPoolExecutor(len(self.teams.values()) * 2 + 5)
            self.futures = [executor.submit(send_to_team, item) for item in self.teams.values()]
            self.futures += [executor.submit(recv_from_team, item) for item in self.teams.values()]

            concurrent.futures.wait(self.futures)
            
            # time.sleep(5)
    


app = Flask(__name__)
game_server = GameServer()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Word Game Status</title>
    <meta http-equiv="refresh" content="5">
</head>
<body>
    <h1>Word Game Status</h1>
    {% if not game_server.game_started %}
        <h2>Waiting Players</h2>
        <ul>
        {% for player in game_server.players %}
            <li>{{ player.name }}</li>
        {% endfor %}
        </ul>
        <form method="POST" action="/start">
            <input type="submit" value="Start Game">
        </form>
    {% else %}
        <h2>Teams</h2>
        {% for team_num, team in game_server.teams.items() %}
            <h3>Team {{ team_num + 1 }}</h3>
            <ul>
            {% for player in team.players %}
                <li>{{ player.name }} (Port: {{ player.assigned_port }})</li>
            {% endfor %}
            <li>Team Server Port: {{ team.team_port }}</li>
            </ul>
            <h4>Submissions:</h4>
            <ul>
            {% for response, elapsed, timestamp in team.submissions %}
                <li>{{ response }} ({{ "%.2f"|format(elapsed) }}s from game start)</li>
            {% endfor %}
            </ul>
        {% endfor %}
    {% endif %}
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, game_server=game_server)

@app.route('/start', methods=['POST'])
def start_game():
    if not game_server.game_started:
        game_server.start_game()
    return redirect("/")

def start_socket_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 1111))
    server.listen()
    logging.info("Socket server started on port 1111")
    
    while True:
        client, address = server.accept()
        threading.Thread(target=game_server.handle_client, args=(client, address)).start()

if __name__ == '__main__':
    def handle_sigterm(*args):
        print("Received SIGTERM, shutting down...", flush=True)
        sys.exit(0)
    signal.signal(signal.SIGTERM, handle_sigterm)

    threading.Thread(target=start_socket_server, daemon=True).start()
    app.run(port=8080)