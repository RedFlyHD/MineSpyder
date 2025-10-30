"""
Scanner de serveurs Minecraft
Module principal pour la découverte et l'analyse des serveurs
"""

import socket
import threading
import time
import ipaddress
import json
import base64
import struct
from typing import List, Dict, Optional, Callable, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

class MinecraftServer:
    """Classe représentant un serveur Minecraft découvert"""
    
    def __init__(self, ip: str, port: int = 25565):
        self.ip = ip
        self.port = port
        self.name = ""
        self.description = ""
        self.version = ""
        self.protocol = 0
        self.players_online = 0
        self.players_max = 0
        self.players_list = []
        self.ping = 0
        self.favicon = None
        self.whitelist = False
        self.location = {"country": "Unknown", "city": "Unknown", "lat": 0, "lon": 0}
        self.last_seen = time.time()
        self.online = True
    
    def to_dict(self) -> Dict:
        """Convertit le serveur en dictionnaire"""
        return {
            "ip": self.ip,
            "port": self.port,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "protocol": self.protocol,
            "players_online": self.players_online,
            "players_max": self.players_max,
            "players_list": self.players_list,
            "ping": self.ping,
            "favicon": self.favicon,
            "whitelist": self.whitelist,
            "location": self.location,
            "last_seen": self.last_seen,
            "online": self.online
        }
    
    def __str__(self):
        return f"{self.ip}:{self.port} - {self.name} ({self.players_online}/{self.players_max})"

class MinecraftScanner:
    """Scanner principal pour les serveurs Minecraft"""
    
    def __init__(self):
        self.servers: List[MinecraftServer] = []
        self.is_scanning = False
        self.scan_progress = 0
        self.total_ips = 0
        self.scanned_ips = 0
        self.found_servers = 0
        self.callbacks = {
            'server_found': [],
            'progress_update': [],
            'scan_complete': [],
            'scan_started': []
        }
        self.stop_flag = threading.Event()
    
    def add_callback(self, event: str, callback: Callable):
        """Ajoute un callback pour un événement"""
        if event in self.callbacks:
            self.callbacks[event].append(callback)
    
    def _call_callbacks(self, event: str, *args, **kwargs):
        """Appelle tous les callbacks d'un événement"""
        for callback in self.callbacks.get(event, []):
            try:
                callback(*args, **kwargs)
            except Exception as e:
                print(f"Erreur dans le callback {event}: {e}")
    
    def ping_server(self, ip: str, port: int = 25565, timeout: int = 3) -> Optional[MinecraftServer]:
        """Ping un serveur Minecraft spécifique"""
        try:
            start_time = time.time()
            
            # Connexion socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            
            result = sock.connect_ex((ip, port))
            if result != 0:
                sock.close()
                return None
            
            # Handshake packet
            handshake = self._create_handshake_packet(ip, port)
            sock.send(handshake)
            
            # Status request
            status_request = b'\x01\x00'
            sock.send(status_request)
            
            # Lire la réponse
            response = self._read_packet(sock)
            sock.close()
            
            if not response:
                return None
            
            # Parser la réponse JSON
            try:
                status_data = json.loads(response)
            except json.JSONDecodeError:
                return None
            
            # Calculer le ping
            ping_time = int((time.time() - start_time) * 1000)
            
            # Créer l'objet serveur
            server = MinecraftServer(ip, port)
            server.ping = ping_time
            
            # Parser les données du serveur
            if 'description' in status_data:
                desc = status_data['description']
                if isinstance(desc, dict):
                    server.description = desc.get('text', '')
                    server.name = desc.get('text', '')
                else:
                    server.description = str(desc)
                    server.name = str(desc)
            
            if 'version' in status_data:
                server.version = status_data['version'].get('name', '')
                server.protocol = status_data['version'].get('protocol', 0)
            
            if 'players' in status_data:
                players = status_data['players']
                server.players_online = players.get('online', 0)
                server.players_max = players.get('max', 0)
                
                if 'sample' in players:
                    server.players_list = [p.get('name', '') for p in players['sample']]
            
            # Favicon
            if 'favicon' in status_data:
                server.favicon = status_data['favicon']
            
            # Vérifier la whitelist (approximation basée sur le message d'erreur)
            server.whitelist = self._check_whitelist(ip, port)
            
            # Géolocalisation
            server.location = self._get_location(ip)
            
            return server
            
        except Exception as e:
            return None
    
    def _create_handshake_packet(self, ip: str, port: int) -> bytes:
        """Crée un packet de handshake Minecraft"""
        # Protocol version (nous utilisons 759 pour 1.19)
        protocol_version = 759
        
        # Construire le packet
        packet_data = b''
        
        # Packet ID (0x00 pour handshake)
        packet_data += b'\x00'
        
        # Protocol version
        packet_data += self._pack_varint(protocol_version)
        
        # Server address
        server_address = ip.encode('utf-8')
        packet_data += self._pack_varint(len(server_address))
        packet_data += server_address
        
        # Server port
        packet_data += struct.pack('>H', port)
        
        # Next state (1 pour status)
        packet_data += self._pack_varint(1)
        
        # Length + data
        length = self._pack_varint(len(packet_data))
        return length + packet_data
    
    def _pack_varint(self, value: int) -> bytes:
        """Encode un entier en VarInt"""
        result = b''
        while value >= 0x80:
            result += bytes([value & 0x7F | 0x80])
            value >>= 7
        result += bytes([value & 0x7F])
        return result
    
    def _read_varint(self, sock: socket.socket) -> int:
        """Lit un VarInt depuis un socket"""
        result = 0
        shift = 0
        while True:
            byte_data = sock.recv(1)
            if not byte_data:
                raise Exception("Connexion fermée")
            
            byte = byte_data[0]
            result |= (byte & 0x7F) << shift
            
            if not (byte & 0x80):
                break
            
            shift += 7
            if shift >= 32:
                raise Exception("VarInt trop long")
        
        return result
    
    def _read_packet(self, sock: socket.socket) -> Optional[str]:
        """Lit un packet Minecraft depuis un socket"""
        try:
            # Lire la longueur du packet
            length = self._read_varint(sock)
            
            if length <= 0 or length > 1024 * 1024:  # Limite de sécurité
                return None
            
            # Lire le packet complet
            data = b''
            while len(data) < length:
                chunk = sock.recv(length - len(data))
                if not chunk:
                    return None
                data += chunk
            
            # Le premier byte est l'ID du packet (doit être 0x00 pour status response)
            packet_id = data[0]
            if packet_id != 0:
                return None
            
            # Le reste est la longueur du JSON + le JSON
            json_length = self._read_varint_from_bytes(data[1:])
            json_start = 1 + self._varint_size(json_length)
            
            if json_start >= len(data):
                return None
            
            json_data = data[json_start:json_start + json_length]
            return json_data.decode('utf-8')
            
        except Exception:
            return None
    
    def _read_varint_from_bytes(self, data: bytes) -> int:
        """Lit un VarInt depuis des bytes"""
        result = 0
        shift = 0
        for i, byte in enumerate(data):
            result |= (byte & 0x7F) << shift
            if not (byte & 0x80):
                break
            shift += 7
            if shift >= 32:
                raise Exception("VarInt trop long")
        return result
    
    def _varint_size(self, value: int) -> int:
        """Calcule la taille d'un VarInt"""
        size = 0
        while value >= 0x80:
            size += 1
            value >>= 7
        return size + 1
    
    def _check_whitelist(self, ip: str, port: int) -> bool:
        """Vérifie approximativement si un serveur a une whitelist"""
        # Cette méthode est approximative car il n'y a pas de moyen direct
        # de vérifier la whitelist via le protocol status
        # On peut essayer de se connecter pour voir le message d'erreur
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((ip, port))
            
            # Handshake pour login
            handshake = self._create_login_handshake(ip, port)
            sock.send(handshake)
            
            # Login start avec un nom bidon
            login_start = self._create_login_start("TestUser")
            sock.send(login_start)
            
            # Lire la réponse
            try:
                response = self._read_packet(sock)
                if response and "whitelist" in response.lower():
                    sock.close()
                    return True
            except:
                pass
            
            sock.close()
            return False
            
        except:
            return False  # Assumons pas de whitelist si on ne peut pas vérifier
    
    def _create_login_handshake(self, ip: str, port: int) -> bytes:
        """Crée un handshake pour login"""
        protocol_version = 759
        packet_data = b'\x00'  # Packet ID
        packet_data += self._pack_varint(protocol_version)
        
        server_address = ip.encode('utf-8')
        packet_data += self._pack_varint(len(server_address))
        packet_data += server_address
        
        packet_data += struct.pack('>H', port)
        packet_data += self._pack_varint(2)  # Next state (2 pour login)
        
        length = self._pack_varint(len(packet_data))
        return length + packet_data
    
    def _create_login_start(self, username: str) -> bytes:
        """Crée un packet login start"""
        packet_data = b'\x00'  # Packet ID pour login start
        username_bytes = username.encode('utf-8')
        packet_data += self._pack_varint(len(username_bytes))
        packet_data += username_bytes
        
        length = self._pack_varint(len(packet_data))
        return length + packet_data
    
    def _get_location(self, ip: str) -> Dict[str, any]:
        """Obtient la géolocalisation d'une IP"""
        try:
            # Utiliser un service de géolocalisation gratuit
            response = requests.get(f"http://ip-api.com/json/{ip}", timeout=2)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    return {
                        'country': data.get('country', 'Unknown'),
                        'city': data.get('city', 'Unknown'),
                        'lat': data.get('lat', 0),
                        'lon': data.get('lon', 0)
                    }
        except:
            pass
        
        return {'country': 'Unknown', 'city': 'Unknown', 'lat': 0, 'lon': 0}
    
    def scan_ip_range(self, ip_range: str, ports: List[int] = None, max_threads: int = 100, timeout: int = 3):
        """Scanne une plage d'IP pour des serveurs Minecraft"""
        if ports is None:
            ports = [25565]
        
        self.is_scanning = True
        self.stop_flag.clear()
        self.scan_progress = 0
        self.scanned_ips = 0
        self.found_servers = 0
        
        self._call_callbacks('scan_started')
        
        try:
            # Générer toutes les IPs à scanner
            network = ipaddress.ip_network(ip_range, strict=False)
            all_ips = []
            
            for ip in network.hosts():
                if self.stop_flag.is_set():
                    break
                for port in ports:
                    all_ips.append((str(ip), port))
            
            self.total_ips = len(all_ips)
            
            # Scanner avec des threads
            with ThreadPoolExecutor(max_workers=max_threads) as executor:
                # Soumettre toutes les tâches
                future_to_ip = {
                    executor.submit(self.ping_server, ip, port, timeout): (ip, port)
                    for ip, port in all_ips
                }
                
                # Traiter les résultats au fur et à mesure
                for future in as_completed(future_to_ip):
                    if self.stop_flag.is_set():
                        break
                    
                    ip, port = future_to_ip[future]
                    self.scanned_ips += 1
                    
                    try:
                        server = future.result()
                        if server and not server.whitelist:  # Seulement les serveurs sans whitelist
                            self.servers.append(server)
                            self.found_servers += 1
                            self._call_callbacks('server_found', server)
                            print(f"✅ Serveur trouvé: {server}")
                    
                    except Exception as e:
                        pass  # Ignore les erreurs de scan individual
                    
                    # Mettre à jour le progrès
                    self.scan_progress = (self.scanned_ips / self.total_ips) * 100
                    self._call_callbacks('progress_update', self.scan_progress, self.scanned_ips, self.total_ips, self.found_servers)
        
        finally:
            self.is_scanning = False
            self._call_callbacks('scan_complete', len(self.servers))
    
    def scan_multiple_ranges(self, ip_ranges: List[str], ports: List[int] = None, max_threads: int = 100, timeout: int = 3):
        """Scanne plusieurs plages d'IP"""
        for ip_range in ip_ranges:
            if self.stop_flag.is_set():
                break
            print(f"🔍 Scanner la plage: {ip_range}")
            self.scan_ip_range(ip_range, ports, max_threads, timeout)
    
    def stop_scan(self):
        """Arrête le scan en cours"""
        self.stop_flag.set()
        self.is_scanning = False
    
    def get_servers(self) -> List[MinecraftServer]:
        """Retourne la liste des serveurs trouvés"""
        return self.servers.copy()
    
    def clear_servers(self):
        """Efface la liste des serveurs"""
        self.servers.clear()
        self.found_servers = 0
    
    def save_servers(self, filename: str):
        """Sauvegarde les serveurs dans un fichier JSON"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                servers_data = [server.to_dict() for server in self.servers]
                json.dump(servers_data, f, indent=2, ensure_ascii=False)
            print(f"💾 Serveurs sauvegardés dans {filename}")
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde: {e}")
    
    def load_servers(self, filename: str):
        """Charge les serveurs depuis un fichier JSON"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                servers_data = json.load(f)
            
            self.servers.clear()
            for data in servers_data:
                server = MinecraftServer(data['ip'], data['port'])
                server.name = data.get('name', '')
                server.description = data.get('description', '')
                server.version = data.get('version', '')
                server.protocol = data.get('protocol', 0)
                server.players_online = data.get('players_online', 0)
                server.players_max = data.get('players_max', 0)
                server.players_list = data.get('players_list', [])
                server.ping = data.get('ping', 0)
                server.favicon = data.get('favicon')
                server.whitelist = data.get('whitelist', False)
                server.location = data.get('location', {'country': 'Unknown', 'city': 'Unknown', 'lat': 0, 'lon': 0})
                server.last_seen = data.get('last_seen', time.time())
                server.online = data.get('online', True)
                
                self.servers.append(server)
            
            self.found_servers = len(self.servers)
            print(f"📂 {len(self.servers)} serveurs chargés depuis {filename}")
            
        except Exception as e:
            print(f"❌ Erreur lors du chargement: {e}")
