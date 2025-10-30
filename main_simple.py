#!/usr/bin/env python3
"""
MineSpyder - Version GUI simplifiée
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from src.scanner import MinecraftScanner
from src.config import Config

class SimpleMineSpyderGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MineSpyder - Minecraft Server Scanner")
        self.root.geometry("900x700")
        
        self.scanner = MinecraftScanner()
        self.config = Config()
        
        self.setup_ui()
        self.setup_callbacks()
    
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # Titre
        title_label = ttk.Label(main_frame, text="🕷️ MineSpyder - Scanner de serveurs Minecraft", 
                               font=('TkDefaultFont', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Frame de contrôle
        control_frame = ttk.LabelFrame(main_frame, text="Contrôles du scan", padding="10")
        control_frame.pack(fill='x', pady=(0, 10))
        
        # Configuration du scan
        config_frame = ttk.Frame(control_frame)
        config_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(config_frame, text="Pays/Région:").grid(row=0, column=0, sticky='w', padx=(0, 5))
        self.region_combo = ttk.Combobox(config_frame, width=20, state='readonly')
        countries = ["France", "United States", "Germany", "United Kingdom", "Canada", "Australia"]
        self.region_combo['values'] = countries + ["Plage personnalisée"]
        self.region_combo.set("France")
        self.region_combo.grid(row=0, column=1, padx=5)
        
        ttk.Label(config_frame, text="IP personnalisée:").grid(row=0, column=2, sticky='w', padx=(20, 5))
        self.custom_ip_entry = ttk.Entry(config_frame, width=20)
        self.custom_ip_entry.insert(0, "192.168.1.0/24")
        self.custom_ip_entry.grid(row=0, column=3, padx=5)
        
        # Paramètres
        params_frame = ttk.Frame(control_frame)
        params_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(params_frame, text="Threads:").grid(row=0, column=0, sticky='w')
        self.threads_spin = ttk.Spinbox(params_frame, from_=10, to=200, width=10)
        self.threads_spin.set("50")
        self.threads_spin.grid(row=0, column=1, padx=5)
        
        ttk.Label(params_frame, text="Timeout:").grid(row=0, column=2, sticky='w', padx=(20, 0))
        self.timeout_spin = ttk.Spinbox(params_frame, from_=1, to=10, width=10)
        self.timeout_spin.set("3")
        self.timeout_spin.grid(row=0, column=3, padx=5)
        
        # Boutons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill='x')
        
        self.start_button = ttk.Button(button_frame, text="🔍 Démarrer le scan", command=self.start_scan)
        self.start_button.pack(side='left', padx=(0, 5))
        
        self.stop_button = ttk.Button(button_frame, text="⏹️ Arrêter", command=self.stop_scan, state='disabled')
        self.stop_button.pack(side='left', padx=5)
        
        self.clear_button = ttk.Button(button_frame, text="🗑️ Effacer", command=self.clear_results)
        self.clear_button.pack(side='left', padx=5)
        
        # Barre de progrès
        progress_frame = ttk.Frame(control_frame)
        progress_frame.pack(fill='x', pady=(10, 0))
        
        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.pack(fill='x', pady=(0, 5))
        
        self.status_label = ttk.Label(progress_frame, text="Prêt à scanner")
        self.status_label.pack()
        
        # Liste des serveurs
        servers_frame = ttk.LabelFrame(main_frame, text="Serveurs trouvés", padding="10")
        servers_frame.pack(fill='both', expand=True)
        
        # Treeview
        columns = ('ip', 'name', 'players', 'ping', 'version', 'location')
        self.tree = ttk.Treeview(servers_frame, columns=columns, show='headings', height=15)
        
        # Configuration des colonnes
        self.tree.heading('ip', text='IP:Port')
        self.tree.heading('name', text='Nom du serveur')
        self.tree.heading('players', text='Joueurs')
        self.tree.heading('ping', text='Ping')
        self.tree.heading('version', text='Version')
        self.tree.heading('location', text='Localisation')
        
        # Largeur des colonnes
        self.tree.column('ip', width=120)
        self.tree.column('name', width=200)
        self.tree.column('players', width=80)
        self.tree.column('ping', width=60)
        self.tree.column('version', width=100)
        self.tree.column('location', width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(servers_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Bind événements
        self.tree.bind('<Double-1>', self.on_server_double_click)
    
    def setup_callbacks(self):
        """Configure les callbacks du scanner"""
        self.scanner.add_callback('server_found', self.on_server_found)
        self.scanner.add_callback('progress_update', self.on_progress_update)
        self.scanner.add_callback('scan_started', self.on_scan_started)
        self.scanner.add_callback('scan_complete', self.on_scan_complete)
    
    def start_scan(self):
        """Démarre le scan"""
        try:
            # Paramètres
            threads = int(self.threads_spin.get())
            timeout = int(self.timeout_spin.get())
            region = self.region_combo.get()
            
            # Déterminer les plages IP
            if region == "Plage personnalisée":
                ip_ranges = [self.custom_ip_entry.get()]
            else:
                ip_ranges = self.config.get_country_ranges(region)
                if not ip_ranges:
                    # Utiliser des plages par défaut si pas de config
                    default_ranges = {
                        "France": ["194.2.0.0/24", "90.0.0.0/24"],
                        "United States": ["8.8.8.0/24", "74.125.0.0/24"],
                        "Germany": ["85.214.0.0/24"],
                        "United Kingdom": ["81.2.69.0/24"],
                        "Canada": ["99.224.0.0/24"],
                        "Australia": ["1.128.0.0/24"]
                    }
                    ip_ranges = default_ranges.get(region, ["192.168.1.0/24"])
            
            ports = [25565, 25566, 25567]
            
            # Lancer le scan dans un thread
            scan_thread = threading.Thread(
                target=self.run_scan,
                args=(ip_ranges, ports, threads, timeout),
                daemon=True
            )
            scan_thread.start()
            
        except ValueError:
            messagebox.showerror("Erreur", "Paramètres invalides")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur: {e}")
    
    def run_scan(self, ip_ranges, ports, threads, timeout):
        """Lance le scan (dans un thread séparé)"""
        try:
            self.scanner.scan_multiple_ranges(ip_ranges, ports, threads, timeout)
        except Exception as e:
            print(f"Erreur de scan: {e}")
    
    def stop_scan(self):
        """Arrête le scan"""
        self.scanner.stop_scan()
    
    def clear_results(self):
        """Efface les résultats"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.scanner.clear_servers()
        self.status_label.config(text="Résultats effacés")
    
    def on_server_found(self, server):
        """Appelé quand un serveur est trouvé"""
        # Ajouter au treeview
        ip_text = f"{server.ip}:{server.port}"
        name_text = server.name or server.description or "Serveur sans nom"
        players_text = f"{server.players_online}/{server.players_max}"
        ping_text = f"{server.ping}ms"
        version_text = server.version or "Inconnue"
        location_text = f"{server.location['city']}, {server.location['country']}"
        
        self.tree.insert('', 'end', values=(ip_text, name_text, players_text, ping_text, version_text, location_text))
    
    def on_progress_update(self, progress, scanned, total, found):
        """Appelé lors de la mise à jour du progrès"""
        self.progress['value'] = progress
        self.status_label.config(text=f"Scan: {scanned}/{total} IPs - {found} serveurs trouvés")
    
    def on_scan_started(self):
        """Appelé au début du scan"""
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.progress['value'] = 0
        self.status_label.config(text="Scan en cours...")
    
    def on_scan_complete(self, total_found):
        """Appelé à la fin du scan"""
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress['value'] = 100
        self.status_label.config(text=f"Scan terminé - {total_found} serveurs trouvés")
    
    def on_server_double_click(self, event):
        """Gestionnaire de double-clic sur un serveur"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            ip_text = self.tree.item(item)['values'][0]
            messagebox.showinfo("IP du serveur", f"IP: {ip_text}\n\nCopiez cette adresse dans Minecraft pour vous connecter.")
    
    def run(self):
        """Lance l'application"""
        print("🕷️ Démarrage de MineSpyder GUI...")
        self.root.mainloop()

def main():
    """Point d'entrée principal"""
    try:
        app = SimpleMineSpyderGUI()
        app.run()
    except Exception as e:
        print(f"Erreur: {e}")
        messagebox.showerror("Erreur", f"Erreur fatale: {e}")

if __name__ == "__main__":
    main()
