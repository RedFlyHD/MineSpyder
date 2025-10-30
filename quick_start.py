#!/usr/bin/env python3
"""
Lancement rapide de MineSpyder - Interface simplifiée
"""

import os
import sys

def main():
    """Lance directement l'interface simplifiée"""
    print("🕷️ Lancement rapide de MineSpyder...")
    
    # S'assurer qu'on est dans le bon répertoire
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    try:
        # Importer et lancer l'interface simplifiée
        exec(open("main_simple.py").read())
    except FileNotFoundError:
        print("❌ Fichier main_simple.py non trouvé")
        print("💡 Assurez-vous d'être dans le répertoire MineSpyder")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        print("💡 Essayez: python main_simple.py")

if __name__ == "__main__":
    main()
