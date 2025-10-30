#!/usr/bin/env python3
"""
Test rapide de MineSpyder - Vérification du système
"""

import sys
import os
import importlib.util

def check_python_version():
    """Vérifie la version de Python"""
    print("🐍 Vérification de Python...")
    if sys.version_info >= (3, 7):
        print(f"   ✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        return True
    else:
        print(f"   ❌ Python {sys.version_info.major}.{sys.version_info.minor} (minimum requis: 3.7)")
        return False

def check_modules():
    """Vérifie la disponibilité des modules"""
    print("\n📦 Vérification des modules...")
    
    required_modules = [
        ('tkinter', 'Interface graphique'),
        ('requests', 'Requêtes HTTP'),
        ('PIL', 'Traitement d\'images'),
        ('threading', 'Multi-threading'),
        ('socket', 'Connexions réseau'),
        ('json', 'Gestion JSON'),
        ('ipaddress', 'Gestion des adresses IP')
    ]
    
    all_good = True
    
    for module_name, description in required_modules:
        try:
            if module_name == 'PIL':
                importlib.import_module('PIL.Image')
            else:
                importlib.import_module(module_name)
            print(f"   ✅ {module_name} - {description}")
        except ImportError:
            print(f"   ❌ {module_name} - {description} (MANQUANT)")
            all_good = False
    
    return all_good

def check_minespyder_modules():
    """Vérifie les modules MineSpyder"""
    print("\n🕷️ Vérification des modules MineSpyder...")
    
    minespyder_modules = [
        ('src.scanner', 'Scanner de serveurs'),
        ('src.config', 'Configuration'),
        ('src.gui', 'Interface graphique'),
        ('src.utils', 'Utilitaires')
    ]
    
    all_good = True
    
    for module_name, description in minespyder_modules:
        try:
            importlib.import_module(module_name)
            print(f"   ✅ {module_name} - {description}")
        except ImportError as e:
            print(f"   ❌ {module_name} - {description} (ERREUR: {e})")
            all_good = False
    
    return all_good

def check_files():
    """Vérifie la présence des fichiers requis"""
    print("\n📁 Vérification des fichiers...")
    
    required_files = [
        'config.json',
        'main.py',
        'main_simple.py',
        'src/__init__.py',
        'src/scanner.py',
        'src/config.py',
        'src/gui.py',
        'src/utils.py'
    ]
    
    all_good = True
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} (MANQUANT)")
            all_good = False
    
    return all_good

def main():
    """Fonction principale de vérification"""
    print("🔍 MineSpyder - Vérification du système")
    print("=" * 50)
    
    checks = [
        ("Version Python", check_python_version),
        ("Modules Python", check_modules), 
        ("Modules MineSpyder", check_minespyder_modules),
        ("Fichiers requis", check_files)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        passed = check_func()
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 TOUS LES TESTS PASSÉS !")
        print("\n🚀 Vous pouvez maintenant lancer MineSpyder:")
        print("   python main_simple.py  # Interface graphique")
        print("   python demo.py         # Démonstration")
        print("   python test_scanner.py # Test du scanner")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("\n🛠️ Actions recommandées:")
        print("   1. Assurez-vous d'être dans l'environnement virtuel:")
        print("      source venv/bin/activate")
        print("   2. Installez les dépendances manquantes:")
        print("      pip install requests Pillow")
        print("   3. Relancez cette vérification:")
        print("      python check_system.py")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
