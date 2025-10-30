"""
Fonctions utilitaires pour MineSpyder
"""

import ipaddress
import socket
import re
from typing import List, Tuple, Optional

def validate_ip_address(ip: str) -> bool:
    """Valide si une chaîne est une adresse IP valide"""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def validate_ip_range(ip_range: str) -> bool:
    """Valide si une chaîne est une plage IP valide (CIDR)"""
    try:
        ipaddress.ip_network(ip_range, strict=False)
        return True
    except ValueError:
        return False

def expand_ip_range(ip_range: str, max_ips: int = 1000) -> List[str]:
    """Expand une plage IP en liste d'adresses individuelles"""
    try:
        network = ipaddress.ip_network(ip_range, strict=False)
        ips = []
        count = 0
        
        for ip in network.hosts():
            if count >= max_ips:
                break
            ips.append(str(ip))
            count += 1
        
        return ips
    except ValueError:
        return []

def is_port_open(ip: str, port: int, timeout: float = 3.0) -> bool:
    """Vérifie si un port est ouvert sur une IP donnée"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def parse_minecraft_motd(motd_text: str) -> str:
    """Parse et nettoie un MOTD Minecraft (supprime les codes de couleur)"""
    if not motd_text:
        return ""
    
    # Supprimer les codes de couleur Minecraft (§ suivi d'un caractère)
    clean_text = re.sub(r'§.', '', motd_text)
    
    # Supprimer les codes de couleur JSON
    clean_text = re.sub(r'"color":\s*"[^"]*"', '', clean_text)
    clean_text = re.sub(r'"bold":\s*(?:true|false)', '', clean_text)
    clean_text = re.sub(r'"italic":\s*(?:true|false)', '', clean_text)
    clean_text = re.sub(r'"underlined":\s*(?:true|false)', '', clean_text)
    clean_text = re.sub(r'"strikethrough":\s*(?:true|false)', '', clean_text)
    clean_text = re.sub(r'"obfuscated":\s*(?:true|false)', '', clean_text)
    
    # Nettoyer les espaces multiples
    clean_text = re.sub(r'\s+', ' ', clean_text)
    
    return clean_text.strip()

def format_player_count(online: int, max_players: int) -> str:
    """Formate le nombre de joueurs de manière lisible"""
    if max_players == 0:
        return f"{online}"
    
    percentage = (online / max_players) * 100 if max_players > 0 else 0
    
    if percentage == 0:
        status = "Vide"
    elif percentage < 25:
        status = "Peu peuplé"
    elif percentage < 75:
        status = "Modérément peuplé"
    elif percentage < 100:
        status = "Bien peuplé"
    else:
        status = "Complet"
    
    return f"{online}/{max_players} ({status})"

def ping_to_quality(ping: int) -> Tuple[str, str]:
    """Convertit un ping en qualité et couleur"""
    if ping < 50:
        return "Excellent", "green"
    elif ping < 100:
        return "Bon", "orange"
    elif ping < 200:
        return "Moyen", "yellow"
    elif ping < 300:
        return "Mauvais", "red"
    else:
        return "Très mauvais", "darkred"

def get_minecraft_version_info(protocol: int) -> Optional[str]:
    """Retourne des informations sur la version Minecraft basées sur le protocole"""
    protocol_versions = {
        4: "1.7.2-1.7.5",
        5: "1.7.6-1.7.10",
        47: "1.8-1.8.9",
        107: "1.9",
        108: "1.9.1",
        109: "1.9.2",
        110: "1.9.4",
        210: "1.10-1.10.2",
        315: "1.11",
        316: "1.11.2",
        335: "1.12",
        338: "1.12.1",
        340: "1.12.2",
        393: "1.13",
        401: "1.13.1",
        404: "1.13.2",
        477: "1.14",
        480: "1.14.1",
        485: "1.14.2",
        490: "1.14.3",
        498: "1.14.4",
        573: "1.15",
        575: "1.15.1",
        578: "1.15.2",
        735: "1.16",
        736: "1.16.1",
        751: "1.16.2",
        753: "1.16.3",
        754: "1.16.4-1.16.5",
        755: "1.17",
        756: "1.17.1",
        757: "1.18-1.18.1",
        758: "1.18.2",
        759: "1.19",
        760: "1.19.2",
        761: "1.19.3",
        762: "1.19.4",
        763: "1.20-1.20.1"
    }
    
    return protocol_versions.get(protocol, f"Protocole {protocol}")

def sanitize_filename(filename: str) -> str:
    """Nettoie un nom de fichier pour qu'il soit valide sur tous les OS"""
    # Caractères interdits sur Windows
    invalid_chars = '<>:"/\\|?*'
    
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Supprimer les espaces en début/fin
    filename = filename.strip()
    
    # Supprimer les points en fin (problème Windows)
    filename = filename.rstrip('.')
    
    # Limiter la longueur
    if len(filename) > 100:
        filename = filename[:100]
    
    return filename or "unnamed"

def format_bytes(bytes_count: int) -> str:
    """Formate un nombre d'octets de manière lisible"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_count < 1024.0:
            return f"{bytes_count:.1f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.1f} TB"

def estimate_scan_time(ip_count: int, thread_count: int, timeout: float) -> float:
    """Estime le temps de scan en secondes"""
    # Estimation basée sur l'expérience : 
    # - La plupart des IPs ne répondent pas (timeout rapide)
    # - Quelques IPs répondent (temps de connexion normal)
    
    avg_time_per_ip = timeout * 0.3  # 30% du timeout en moyenne
    estimated_seconds = (ip_count * avg_time_per_ip) / thread_count
    
    return max(estimated_seconds, 1.0)  # Au moins 1 seconde

def format_duration(seconds: float) -> str:
    """Formate une durée en secondes de manière lisible"""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes:.0f}m {remaining_seconds:.0f}s"
    else:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        return f"{hours:.0f}h {remaining_minutes:.0f}m"

def is_private_ip(ip: str) -> bool:
    """Vérifie si une IP est privée (RFC 1918)"""
    try:
        ip_obj = ipaddress.ip_address(ip)
        return ip_obj.is_private
    except ValueError:
        return False

def is_local_ip(ip: str) -> bool:
    """Vérifie si une IP est locale (loopback, link-local, etc.)"""
    try:
        ip_obj = ipaddress.ip_address(ip)
        return ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_multicast
    except ValueError:
        return False

def get_public_ip_ranges() -> List[str]:
    """Retourne une liste de plages IP publiques communes pour le scan"""
    return [
        "8.8.8.0/24",       # Google DNS
        "1.1.1.0/24",       # Cloudflare DNS
        "208.67.222.0/24",  # OpenDNS
        "74.125.0.0/16",    # Google
        "31.13.0.0/16",     # Facebook
        "157.240.0.0/16",   # Facebook/Instagram
        "104.16.0.0/12",    # Cloudflare
        "13.107.0.0/16",    # Microsoft
        "40.96.0.0/12",     # Microsoft Azure
        "52.96.0.0/12",     # Microsoft Azure
    ]

class IPRangeValidator:
    """Validateur de plages IP avec vérifications de sécurité"""
    
    @staticmethod
    def is_safe_to_scan(ip_range: str) -> Tuple[bool, str]:
        """Vérifie si une plage IP est sûre à scanner"""
        try:
            network = ipaddress.ip_network(ip_range, strict=False)
            
            # Vérifier si c'est une plage privée
            if network.is_private:
                return False, "Plage IP privée - scan local seulement"
            
            # Vérifier la taille de la plage
            if network.num_addresses > 65536:  # Plus de 64k adresses
                return False, "Plage IP trop large (max 65536 adresses)"
            
            # Vérifier les plages sensibles
            sensitive_ranges = [
                "127.0.0.0/8",      # Loopback
                "169.254.0.0/16",   # Link-local
                "224.0.0.0/4",      # Multicast
                "240.0.0.0/4",      # Reserved
            ]
            
            for sensitive in sensitive_ranges:
                sensitive_net = ipaddress.ip_network(sensitive)
                if network.overlaps(sensitive_net):
                    return False, f"Plage sensible détectée: {sensitive}"
            
            return True, "Plage IP valide"
            
        except ValueError as e:
            return False, f"Format de plage invalide: {e}"

def get_country_ip_ranges() -> dict:
    """Retourne un dictionnaire des plages IP par pays (approximatif)"""
    return {
        "France": [
            "81.2.69.0/24",
            "82.225.0.0/16", 
            "90.0.0.0/9",
            "193.252.0.0/16"
        ],
        "United States": [
            "8.8.8.0/24",
            "74.125.0.0/16",
            "173.194.0.0/16",
            "208.65.152.0/22"
        ],
        "Germany": [
            "85.214.0.0/16",
            "87.106.0.0/16",
            "194.25.0.0/16"
        ],
        "United Kingdom": [
            "81.2.69.0/24",
            "82.132.0.0/16",
            "194.109.0.0/16"
        ],
        "Canada": [
            "99.224.0.0/16",
            "142.4.0.0/16",
            "206.191.0.0/16"
        ],
        "Australia": [
            "1.128.0.0/11",
            "27.32.0.0/11",
            "101.160.0.0/11"
        ]
    }
