#!/usr/bin/env python3
"""
Script d'installation et de configuration de MineSpyder
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Vérifie la version de Python"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 ou plus récent est requis")
        print(f"Version actuelle: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} détecté")
    return True

def install_requirements():
    """Installe les dépendances"""
    print("📦 Installation des dépendances...")
    
    requirements = [
        "requests>=2.31.0",
        "Pillow>=10.0.0",
        "psutil>=5.9.0"  # Pour les informations système
    ]
    
    for requirement in requirements:
        try:
            print(f"  Installing {requirement}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", requirement])
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur lors de l'installation de {requirement}: {e}")
            return False
    
    print("✅ Toutes les dépendances ont été installées")
    return True

def check_system_compatibility():
    """Vérifie la compatibilité du système"""
    system = platform.system()
    print(f"🖥️  Système détecté: {system}")
    
    if system in ['Windows', 'Darwin', 'Linux']:
        print("✅ Système compatible")
        return True
    else:
        print("⚠️  Système non testé, mais devrait fonctionner")
        return True

def create_directories():
    """Crée les répertoires nécessaires"""
    print("📁 Création des répertoires...")
    
    directories = ['data', 'assets', 'logs']
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  ✅ {directory}/")
    
    return True

def test_installation():
    """Test rapide de l'installation"""
    print("🧪 Test de l'installation...")
    
    try:
        # Test d'import des modules principaux
        import socket
        import threading
        import tkinter as tk
        from PIL import Image
        import requests
        
        print("✅ Tous les modules sont importables")
        
        # Test de création d'une fenêtre Tkinter
        root = tk.Tk()
        root.withdraw()  # Cacher la fenêtre
        root.destroy()
        print("✅ Tkinter fonctionne correctement")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def main():
    """Fonction principale d'installation"""
    print("🕷️  Installation de MineSpyder")
    print("=" * 40)
    
    steps = [
        ("Vérification de Python", check_python_version),
        ("Vérification du système", check_system_compatibility),
        ("Installation des dépendances", install_requirements),
        ("Création des répertoires", create_directories),
        ("Test de l'installation", test_installation)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if not step_func():
            print(f"❌ Échec: {step_name}")
            return False
    
    print("\n" + "=" * 40)
    print("🎉 Installation terminée avec succès!")
    print("\nPour lancer MineSpyder:")
    print("  python main.py")
    print("\nPour plus d'informations, consultez le README.md")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Installation interrompue par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        sys.exit(1)
