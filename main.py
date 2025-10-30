#!/usr/bin/env python3
"""
MineSpyder - Minecraft Server Scanner
Application principale pour scanner et découvrir des serveurs Minecraft
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

# Ajouter le répertoire src au path pour les imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from scanner import MinecraftScanner
    from config import Config
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("💡 Assurez-vous d'être dans le bon répertoire et que les modules sont installés")
    sys.exit(1)

class SimpleMineSpyderApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MineSpyder - Minecraft Server Scanner")
        self.root.geometry("800x600")
        
        # Configuration
        self.config = Config()
        self.scanner = MinecraftScanner()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configure une interface utilisateur simple"""
        # Frame principal
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Titre
        title_label = tk.Label(main_frame, text="🕷️ MineSpyder", 
                              font=('Arial', 20, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Description
        desc_label = tk.Label(main_frame, 
                             text="Scanner de serveurs Minecraft\n\nPour une expérience optimale, utilisez:",
                             font=('Arial', 12))
        desc_label.pack(pady=(0, 20))
        
        # Boutons
        button_frame = tk.Frame(main_frame)
        button_frame.pack()
        
        simple_btn = tk.Button(button_frame, 
                              text="🎮 Interface Simplifiée (Recommandée)",
                              command=self.launch_simple,
                              font=('Arial', 12),
                              bg='#4CAF50',
                              fg='white',
                              padx=20,
                              pady=10)
        simple_btn.pack(pady=10)
        
        demo_btn = tk.Button(button_frame,
                            text="🎯 Voir la Démonstration", 
                            command=self.launch_demo,
                            font=('Arial', 12),
                            bg='#2196F3',
                            fg='white',
                            padx=20,
                            pady=10)
        demo_btn.pack(pady=10)
        
        test_btn = tk.Button(button_frame,
                            text="🧪 Test Scanner Terminal",
                            command=self.launch_test,
                            font=('Arial', 12),
                            bg='#FF9800',
                            fg='white', 
                            padx=20,
                            pady=10)
        test_btn.pack(pady=10)
        
        # Note
        note_label = tk.Label(main_frame,
                             text="💡 Conseil: Utilisez 'python launcher.py' pour le menu complet",
                             font=('Arial', 10),
                             fg='gray')
        note_label.pack(pady=(20, 0))
    
    def launch_simple(self):
        """Lance l'interface simplifiée"""
        self.root.destroy()
        import subprocess
        subprocess.run([sys.executable, "main_simple.py"])
    
    def launch_demo(self):
        """Lance la démonstration"""
        self.root.destroy()
        import subprocess
        subprocess.run([sys.executable, "demo.py"])
    
    def launch_test(self):
        """Lance le test terminal"""
        self.root.destroy()
        import subprocess
        subprocess.run([sys.executable, "test_scanner.py"])
    
    def run(self):
        """Lance l'application"""
        print("🕷️  Démarrage de MineSpyder...")
        self.root.mainloop()

def main():
    """Point d'entrée principal"""
    try:
        app = SimpleMineSpyderApp()
        app.run()
    except KeyboardInterrupt:
        print("\n🛑 Application interrompue par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur fatale : {e}")
        messagebox.showerror("Erreur", f"Erreur fatale : {e}")

if __name__ == "__main__":
    main()
