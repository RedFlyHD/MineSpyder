#!/usr/bin/env python3
"""
Script de démarrage universel pour MineSpyder
Résout automatiquement les problèmes d'environnement
"""

import sys
import os
import subprocess

def setup_environment():
    """Configure l'environnement Python"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Vérifier si l'environnement virtuel existe
    venv_path = os.path.join(script_dir, "venv")
    
    if os.path.exists(venv_path):
        # Utiliser l'environnement virtuel
        if sys.platform.startswith('win'):
            python_path = os.path.join(venv_path, "Scripts", "python.exe")
        else:
            python_path = os.path.join(venv_path, "bin", "python")
        
        if os.path.exists(python_path):
            return python_path
    
    # Fallback vers Python système
    return sys.executable

def main():
    """Lance MineSpyder avec le bon environnement"""
    print("🕷️ MineSpyder - Démarrage universel")
    print("=" * 40)
    
    # Configurer l'environnement
    python_path = setup_environment()
    
    # Menu simple
    print("\nQue voulez-vous lancer ?")
    print("1. 🎮 Interface graphique (recommandée)")
    print("2. 🎯 Démonstration")
    print("3. 🧪 Test scanner")
    print("4. 📋 Menu complet")
    
    try:
        choice = input("\nVotre choix (1-4): ").strip()
        
        scripts = {
            "1": "main_simple.py",
            "2": "demo.py", 
            "3": "test_scanner.py",
            "4": "launcher.py"
        }
        
        if choice in scripts:
            script = scripts[choice]
            print(f"\n🚀 Lancement de {script}...")
            subprocess.run([python_path, script])
        else:
            print("❌ Choix invalide")
            # Lancer l'interface par défaut
            print("🚀 Lancement de l'interface par défaut...")
            subprocess.run([python_path, "main_simple.py"])
            
    except KeyboardInterrupt:
        print("\n👋 Au revoir !")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        print("💡 Essayez de lancer manuellement avec: python main_simple.py")

if __name__ == "__main__":
    main()
