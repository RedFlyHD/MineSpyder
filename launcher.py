#!/usr/bin/env python3
"""
Lanceur principal de MineSpyder avec menu de sélection
"""

import sys
import os
import subprocess

def print_banner():
    """Affiche la bannière MineSpyder"""
    banner = """
🕷️  ███╗   ███╗██╗███╗   ██╗███████╗███████╗██████╗ ██╗   ██╗██████╗ ███████╗██████╗ 
    ████╗ ████║██║████╗  ██║██╔════╝██╔════╝██╔══██╗╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗
    ██╔████╔██║██║██╔██╗ ██║█████╗  ███████╗██████╔╝ ╚████╔╝ ██║  ██║█████╗  ██████╔╝
    ██║╚██╔╝██║██║██║╚██╗██║██╔══╝  ╚════██║██╔═══╝   ╚██╔╝  ██║  ██║██╔══╝  ██╔══██╗
    ██║ ╚═╝ ██║██║██║ ╚████║███████╗███████║██║        ██║   ██████╔╝███████╗██║  ██║
    ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝╚═╝        ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝
    
    🌐 Scanner de serveurs Minecraft - Version 1.0
    🔍 Découvrez des serveurs Minecraft dans le monde entier
    """
    print(banner)

def show_menu():
    """Affiche le menu principal"""
    print("\n" + "="*60)
    print("📋 QUE VOULEZ-VOUS FAIRE ?")
    print("="*60)
    print()
    print("1. 🖥️  Lancer l'interface graphique complète")
    print("2. 🎮 Lancer l'interface graphique simplifiée")
    print("3. 🎯 Voir la démonstration avec serveurs d'exemple")
    print("4. 🧪 Tester le scanner en ligne de commande")
    print("5. 🔧 Vérifier l'installation du système")
    print("6. 📚 Afficher l'aide et les informations")
    print("7. 🚪 Quitter")
    print()
    print("="*60)

def run_with_venv(script_name):
    """Lance un script avec l'environnement virtuel"""
    if os.path.exists("venv"):
        if sys.platform.startswith('win'):
            python_path = os.path.join("venv", "Scripts", "python.exe")
        else:
            python_path = os.path.join("venv", "bin", "python")
        
        if os.path.exists(python_path):
            subprocess.run([python_path, script_name])
        else:
            print("❌ Environnement virtuel non configuré correctement")
            print("💡 Exécutez: python -m venv venv && source venv/bin/activate && pip install requests Pillow")
    else:
        print("❌ Environnement virtuel non trouvé")
        print("💡 Exécutez: python -m venv venv && source venv/bin/activate && pip install requests Pillow")

def show_help():
    """Affiche l'aide"""
    help_text = """
📚 AIDE MINESPYDER

🔧 INSTALLATION:
   1. Assurez-vous d'avoir Python 3.7+ installé
   2. Lancez: python launcher.py
   3. L'installation se fera automatiquement

🎮 UTILISATION:
   • Interface graphique: Plus intuitive, recommandée pour débutants
   • Ligne de commande: Plus rapide, pour utilisateurs avancés
   • Démonstration: Montre des serveurs d'exemple sans scan réel

⚙️ CONFIGURATION:
   • Fichier config.json: Paramètres de scan et plages IP par pays
   • Timeout: Durée d'attente par serveur (1-10 secondes)
   • Threads: Nombre de connexions simultanées (10-500)

🌍 PLAGES IP:
   • Par pays: Utilise des plages IP prédéfinies
   • Personnalisée: Format CIDR (ex: 192.168.1.0/24)
   • Publiques: Évitez les plages privées (192.168.x.x, 10.x.x.x)

⚠️ IMPORTANT:
   • Utilisez l'outil de manière responsable
   • Respectez les conditions d'utilisation des serveurs
   • Certains réseaux peuvent bloquer les scans

🆘 DÉPANNAGE:
   • "Module non trouvé": Vérifiez l'environnement virtuel
   • "Permission denied": chmod +x sur les scripts .sh
   • "Connexion échouée": Vérifiez votre connexion internet

📧 SUPPORT:
   • GitHub Issues: Signaler des bugs
   • README.md: Documentation complète
   • check_system.py: Diagnostic automatique
    """
    print(help_text)

def main():
    """Fonction principale du lanceur"""
    print_banner()
    
    while True:
        show_menu()
        
        try:
            choice = input("👉 Votre choix (1-7): ").strip()
            
            if choice == "1":
                print("\n🚀 Lancement de l'interface graphique complète...")
                run_with_venv("main.py")
                
            elif choice == "2":
                print("\n🚀 Lancement de l'interface graphique simplifiée...")
                run_with_venv("main_simple.py")
                
            elif choice == "3":
                print("\n🎯 Lancement de la démonstration...")
                run_with_venv("demo.py")
                
            elif choice == "4":
                print("\n🧪 Lancement du test scanner...")
                run_with_venv("test_scanner.py")
                
            elif choice == "5":
                print("\n🔧 Vérification du système...")
                run_with_venv("check_system.py")
                
            elif choice == "6":
                show_help()
                input("\n📚 Appuyez sur Entrée pour continuer...")
                
            elif choice == "7":
                print("\n👋 Au revoir ! Merci d'avoir utilisé MineSpyder!")
                break
                
            else:
                print("\n❌ Choix invalide. Veuillez entrer un nombre entre 1 et 7.")
                input("📝 Appuyez sur Entrée pour continuer...")
        
        except KeyboardInterrupt:
            print("\n\n👋 Au revoir !")
            break
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
            input("📝 Appuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Application fermée par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        sys.exit(1)
