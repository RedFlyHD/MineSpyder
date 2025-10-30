#!/usr/bin/env python3
"""
Démonstration de MineSpyder avec des serveurs connus
"""

import time
from src.scanner import MinecraftScanner, MinecraftServer

def create_demo_servers():
    """Crée quelques serveurs de démonstration"""
    demo_servers = []
    
    # Serveur exemple 1
    server1 = MinecraftServer("mc.hypixel.net", 25565)
    server1.name = "Hypixel Network"
    server1.description = "The largest Minecraft server"
    server1.version = "1.8-1.20.1"
    server1.players_online = 45000
    server1.players_max = 100000
    server1.ping = 25
    server1.whitelist = False
    server1.location = {"country": "United States", "city": "Los Angeles", "lat": 34.0522, "lon": -118.2437}
    demo_servers.append(server1)
    
    # Serveur exemple 2
    server2 = MinecraftServer("play.cubecraft.net", 25565)
    server2.name = "CubeCraft Games"
    server2.description = "Java & Bedrock Server"
    server2.version = "1.19.4"
    server2.players_online = 15000
    server2.players_max = 50000
    server2.ping = 45
    server2.whitelist = False
    server2.location = {"country": "Netherlands", "city": "Amsterdam", "lat": 52.3676, "lon": 4.9041}
    demo_servers.append(server2)
    
    # Serveur exemple 3
    server3 = MinecraftServer("mineplex.com", 25565)
    server3.name = "Mineplex"
    server3.description = "Original Minigame Server"
    server3.version = "1.18.2"
    server3.players_online = 2500
    server3.players_max = 10000
    server3.ping = 67
    server3.whitelist = False
    server3.location = {"country": "United States", "city": "Chicago", "lat": 41.8781, "lon": -87.6298}
    demo_servers.append(server3)
    
    # Serveur exemple 4 (français)
    server4 = MinecraftServer("play.funcraft.net", 25565)
    server4.name = "Funcraft"
    server4.description = "Serveur français multijeux"
    server4.version = "1.20.1"
    server4.players_online = 1200
    server4.players_max = 5000
    server4.ping = 15
    server4.whitelist = False
    server4.location = {"country": "France", "city": "Paris", "lat": 48.8566, "lon": 2.3522}
    demo_servers.append(server4)
    
    # Serveur exemple 5
    server5 = MinecraftServer("mc.manacube.net", 25565)
    server5.name = "ManaCube"
    server5.description = "Prison, Survival, Skyblock"
    server5.version = "1.19.2"
    server5.players_online = 800
    server5.players_max = 2000
    server5.ping = 89
    server5.whitelist = False
    server5.location = {"country": "Canada", "city": "Toronto", "lat": 43.6532, "lon": -79.3832}
    demo_servers.append(server5)
    
    return demo_servers

def demo_scan_simulation(scanner: MinecraftScanner):
    """Simule un scan avec progression"""
    demo_servers = create_demo_servers()
    
    print("🔍 Démarrage de la simulation de scan...")
    
    # Simuler le callback de début
    scanner._call_callbacks('scan_started')
    
    total_ips = 100
    scanner.total_ips = total_ips
    
    # Simuler la progression du scan
    for i in range(total_ips):
        scanner.scanned_ips = i + 1
        progress = (scanner.scanned_ips / total_ips) * 100
        
        # Ajouter des serveurs à des moments aléatoires
        if i in [15, 35, 58, 72, 89]:  # Positions où on "trouve" des serveurs
            server_index = len(scanner.servers)
            if server_index < len(demo_servers):
                server = demo_servers[server_index]
                scanner.servers.append(server)
                scanner.found_servers += 1
                scanner._call_callbacks('server_found', server)
                print(f"✅ Serveur trouvé: {server.name}")
        
        # Callback de progression
        scanner._call_callbacks('progress_update', progress, scanner.scanned_ips, total_ips, scanner.found_servers)
        
        # Petite pause pour l'effet visuel
        time.sleep(0.05)
    
    # Callback de fin
    scanner._call_callbacks('scan_complete', len(scanner.servers))
    print(f"🎉 Simulation terminée! {len(scanner.servers)} serveurs trouvés.")

def main():
    """Démonstration principale"""
    print("🕷️ MineSpyder - Mode Démonstration")
    print("=" * 50)
    
    scanner = MinecraftScanner()
    
    def on_server_found(server):
        print(f"📍 {server.name} ({server.ip}:{server.port})")
        print(f"   Joueurs: {server.players_online}/{server.players_max}")
        print(f"   Localisation: {server.location['city']}, {server.location['country']}")
        print(f"   Ping: {server.ping}ms")
        print()
    
    def on_progress(progress, scanned, total, found):
        bar_length = 30
        filled_length = int(bar_length * progress // 100)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)
        print(f"\r🔍 [{bar}] {progress:.1f}% ({scanned}/{total}) - {found} serveurs", end="", flush=True)
    
    scanner.add_callback('server_found', on_server_found)
    scanner.add_callback('progress_update', on_progress)
    
    # Lancer la simulation
    demo_scan_simulation(scanner)
    
    print("\n\n📋 Résumé des serveurs trouvés:")
    print("-" * 50)
    for i, server in enumerate(scanner.servers, 1):
        print(f"{i}. {server.name}")
        print(f"   IP: {server.ip}:{server.port}")
        print(f"   Joueurs: {server.players_online}/{server.players_max}")
        print(f"   Version: {server.version}")
        print(f"   Localisation: {server.location['city']}, {server.location['country']}")
        print()
    
    print("💡 Lancez 'python main_simple.py' pour l'interface graphique complète!")

if __name__ == "__main__":
    main()
