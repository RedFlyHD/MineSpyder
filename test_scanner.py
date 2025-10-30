#!/usr/bin/env python3
"""
Version de test en ligne de commande de MineSpyder
"""

import sys
import time
from src.scanner import MinecraftScanner
from src.config import Config

def test_scanner():
    """Test basique du scanner"""
    print("🕷️  Test de MineSpyder Scanner...")
    
    # Créer le scanner
    scanner = MinecraftScanner()
    config = Config()
    
    # Callback pour afficher les serveurs trouvés
    def on_server_found(server):
        print(f"✅ Serveur trouvé: {server.ip}:{server.port}")
        print(f"   Nom: {server.name or 'Sans nom'}")
        print(f"   Joueurs: {server.players_online}/{server.players_max}")
        print(f"   Ping: {server.ping}ms")
        print(f"   Version: {server.version}")
        print(f"   Localisation: {server.location['city']}, {server.location['country']}")
        print(f"   Whitelist: {'Oui' if server.whitelist else 'Non'}")
        print("-" * 50)
    
    def on_progress(progress, scanned, total, found):
        print(f"📊 Progrès: {progress:.1f}% ({scanned}/{total}) - {found} serveurs")
    
    scanner.add_callback('server_found', on_server_found)
    scanner.add_callback('progress_update', on_progress)
    
    # Test avec une petite plage
    print("🔍 Test de scan sur une petite plage d'IP...")
    
    # Utiliser une plage plus petite pour le test
    test_ranges = ["8.8.8.0/29"]  # Seulement 8 IPs pour le test
    ports = [25565]
    
    print(f"Scan de {test_ranges} sur les ports {ports}")
    print("Appuyez sur Ctrl+C pour arrêter...")
    
    try:
        scanner.scan_multiple_ranges(test_ranges, ports, max_threads=10, timeout=2)
        
        print(f"\n🎉 Scan terminé!")
        print(f"Total de serveurs trouvés: {len(scanner.servers)}")
        
        if scanner.servers:
            print("\n📋 Résumé des serveurs:")
            for i, server in enumerate(scanner.servers, 1):
                print(f"{i}. {server.ip}:{server.port} - {server.name or 'Sans nom'}")
        else:
            print("❌ Aucun serveur Minecraft trouvé dans cette plage.")
            print("💡 Essayez d'autres plages IP ou augmentez le timeout.")
    
    except KeyboardInterrupt:
        print("\n🛑 Scan interrompu par l'utilisateur")
        scanner.stop_scan()
    except Exception as e:
        print(f"❌ Erreur: {e}")

def main():
    """Point d'entrée principal"""
    print("MineSpyder - Test Scanner v1.0")
    print("=" * 40)
    
    test_scanner()

if __name__ == "__main__":
    main()
