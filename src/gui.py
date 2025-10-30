"""
Interface graphique principale de MineSpyder
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
from typing import List, Dict, Optional
from PIL import Image, ImageTk
import base64
import io

from .scanner import MinecraftScanner, MinecraftServer
from .config import Config

class ServerListFrame(ttk.Frame):
    """Frame contenant la liste des serveurs"""
    
    def __init__(self, parent, scanner: MinecraftScanner):
        super().__init__(parent)
        self.scanner = scanner
        self.servers = []
        self.filtered_servers = []
        self.current_filter = ""
        self.current_country_filter = ""
        
        self.setup_ui()
        
        # Callbacks du scanner
        self.scanner.add_callback('server_found', self.on_server_found)
    
    def setup_ui(self):
        """Configure l'interface de la liste de serveurs"""
        # Frame pour les filtres
        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill='x', padx=5, pady=5)
        
        # Filtre par texte
        ttk.Label(filter_frame, text="Filtrer:").pack(side='left')
        self.filter_var = tk.StringVar()
        self.filter_var.trace('w', self.on_filter_change)
        filter_entry = ttk.Entry(filter_frame, textvariable=self.filter_var, width=30)
        filter_entry.pack(side='left', padx=(5, 10))
        
        # Filtre par pays
        ttk.Label(filter_frame, text="Pays:").pack(side='left')
        self.country_var = tk.StringVar()
        self.country_combo = ttk.Combobox(filter_frame, textvariable=self.country_var, width=15, state='readonly')
        self.country_combo.pack(side='left', padx=(5, 10))
        self.country_combo.bind('<<ComboboxSelected>>', self.on_country_filter_change)
        
        # Boutons d'action
        ttk.Button(filter_frame, text="Rafraîchir", command=self.refresh_servers).pack(side='right', padx=5)
        ttk.Button(filter_frame, text="Effacer", command=self.clear_servers).pack(side='right')
        
        # Treeview pour la liste des serveurs
        columns = ('ip', 'name', 'players', 'ping', 'version', 'location')
        self.tree = ttk.Treeview(self, columns=columns, show='tree headings', height=20)
        
        # Configuration des colonnes
        self.tree.heading('#0', text='Icône')
        self.tree.heading('ip', text='IP:Port')
        self.tree.heading('name', text='Nom du serveur')
        self.tree.heading('players', text='Joueurs')
        self.tree.heading('ping', text='Ping')
        self.tree.heading('version', text='Version')
        self.tree.heading('location', text='Localisation')
        
        # Largeur des colonnes
        self.tree.column('#0', width=50, minwidth=50)
        self.tree.column('ip', width=120, minwidth=100)
        self.tree.column('name', width=200, minwidth=150)
        self.tree.column('players', width=80, minwidth=60)
        self.tree.column('ping', width=60, minwidth=50)
        self.tree.column('version', width=100, minwidth=80)
        self.tree.column('location', width=150, minwidth=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack du treeview et scrollbars
        self.tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Bind du double-clic
        self.tree.bind('<Double-1>', self.on_server_double_click)
        
        # Menu contextuel
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Copier IP", command=self.copy_ip)
        self.context_menu.add_command(label="Connexion Minecraft", command=self.connect_minecraft)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Détails du serveur", command=self.show_server_details)
        
        self.tree.bind('<Button-3>', self.show_context_menu)  # Clic droit sur macOS
        self.tree.bind('<Button-2>', self.show_context_menu)  # Clic droit sur Linux/Windows
    
    def on_server_found(self, server: MinecraftServer):
        """Appelé quand un nouveau serveur est trouvé"""
        self.servers.append(server)
        self.update_country_filter()
        self.apply_filters()
    
    def on_filter_change(self, *args):
        """Appelé quand le filtre texte change"""
        self.current_filter = self.filter_var.get().lower()
        self.apply_filters()
    
    def on_country_filter_change(self, event=None):
        """Appelé quand le filtre pays change"""
        self.current_country_filter = self.country_var.get()
        self.apply_filters()
    
    def apply_filters(self):
        """Applique les filtres et met à jour l'affichage"""
        self.filtered_servers = []
        
        for server in self.servers:
            # Filtre par texte
            if self.current_filter:
                searchable_text = f"{server.ip} {server.name} {server.description} {server.version}".lower()
                if self.current_filter not in searchable_text:
                    continue
            
            # Filtre par pays
            if self.current_country_filter and self.current_country_filter != "Tous":
                if server.location['country'] != self.current_country_filter:
                    continue
            
            self.filtered_servers.append(server)
        
        self.update_tree()
    
    def update_tree(self):
        """Met à jour l'affichage du treeview"""
        # Effacer les éléments existants
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Ajouter les serveurs filtrés
        for server in self.filtered_servers:
            # Préparer les données d'affichage
            ip_text = f"{server.ip}:{server.port}"
            name_text = server.name or server.description or "Serveur sans nom"
            players_text = f"{server.players_online}/{server.players_max}"
            ping_text = f"{server.ping}ms"
            version_text = server.version
            location_text = f"{server.location['city']}, {server.location['country']}"
            
            # Couleur basée sur le ping
            tag = ""
            if server.ping < 50:
                tag = "low_ping"
            elif server.ping < 150:
                tag = "medium_ping"
            else:
                tag = "high_ping"
            
            # Ajouter l'élément
            item = self.tree.insert('', 'end', 
                                  values=(ip_text, name_text, players_text, ping_text, version_text, location_text),
                                  tags=(tag,))
            
            # Ajouter l'icône si disponible
            if server.favicon:
                try:
                    icon = self.decode_favicon(server.favicon)
                    if icon:
                        self.tree.set(item, '#0', '🖼️')
                except:
                    pass
        
        # Configuration des tags de couleur
        self.tree.tag_configure("low_ping", foreground="green")
        self.tree.tag_configure("medium_ping", foreground="orange")
        self.tree.tag_configure("high_ping", foreground="red")
    
    def update_country_filter(self):
        """Met à jour la liste des pays dans le filtre"""
        countries = set()
        for server in self.servers:
            if server.location['country'] != 'Unknown':
                countries.add(server.location['country'])
        
        countries_list = ["Tous"] + sorted(list(countries))
        self.country_combo['values'] = countries_list
        
        if not self.country_var.get():
            self.country_var.set("Tous")
    
    def decode_favicon(self, favicon_data: str) -> Optional[ImageTk.PhotoImage]:
        """Décode et redimensionne un favicon de serveur"""
        try:
            # Le favicon est en base64, préfixé par "data:image/png;base64,"
            if favicon_data.startswith('data:image/png;base64,'):
                base64_data = favicon_data[22:]  # Enlever le préfixe
            else:
                base64_data = favicon_data
            
            # Décoder le base64
            image_data = base64.b64decode(base64_data)
            
            # Créer l'image PIL
            image = Image.open(io.BytesIO(image_data))
            
            # Redimensionner à 16x16
            image = image.resize((16, 16), Image.Resampling.LANCZOS)
            
            # Convertir pour Tkinter
            return ImageTk.PhotoImage(image)
            
        except Exception as e:
            return None
    
    def refresh_servers(self):
        """Rafraîchit les informations des serveurs"""
        # Ici on pourrait re-ping les serveurs pour mettre à jour leurs infos
        self.apply_filters()
    
    def clear_servers(self):
        """Efface tous les serveurs de la liste"""
        self.servers.clear()
        self.filtered_servers.clear()
        self.scanner.clear_servers()
        self.update_tree()
        self.update_country_filter()
    
    def on_server_double_click(self, event):
        """Gestionnaire de double-clic sur un serveur"""
        self.show_server_details()
    
    def show_context_menu(self, event):
        """Affiche le menu contextuel"""
        # Sélectionner l'élément sous la souris
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def copy_ip(self):
        """Copie l'IP du serveur sélectionné"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            ip_text = self.tree.item(item)['values'][0]  # Premier élément = IP:Port
            self.clipboard_clear()
            self.clipboard_append(ip_text)
            messagebox.showinfo("Copié", f"IP copiée: {ip_text}")
    
    def connect_minecraft(self):
        """Ouvre Minecraft avec l'IP du serveur (si possible)"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            ip_text = self.tree.item(item)['values'][0]
            messagebox.showinfo("Connexion Minecraft", 
                              f"Copiez cette IP dans Minecraft:\n{ip_text}\n\n"
                              f"1. Ouvrez Minecraft\n"
                              f"2. Allez dans 'Multijoueur'\n"
                              f"3. Cliquez 'Ajouter un serveur'\n"
                              f"4. Collez l'IP: {ip_text}")
    
    def show_server_details(self):
        """Affiche les détails complets du serveur sélectionné"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            ip_text = self.tree.item(item)['values'][0]
            
            # Trouver le serveur correspondant
            server = None
            for s in self.filtered_servers:
                if f"{s.ip}:{s.port}" == ip_text:
                    server = s
                    break
            
            if server:
                ServerDetailsWindow(self, server)

class ScanControlFrame(ttk.Frame):
    """Frame de contrôle du scan"""
    
    def __init__(self, parent, scanner: MinecraftScanner, config: Config):
        super().__init__(parent)
        self.scanner = scanner
        self.config = config
        
        self.setup_ui()
        
        # Callbacks du scanner
        self.scanner.add_callback('progress_update', self.on_progress_update)
        self.scanner.add_callback('scan_started', self.on_scan_started)
        self.scanner.add_callback('scan_complete', self.on_scan_complete)
    
    def setup_ui(self):
        """Configure l'interface de contrôle du scan"""
        # Frame principal
        main_frame = ttk.LabelFrame(self, text="Contrôle du scan", padding="10")
        main_frame.pack(fill='x', padx=5, pady=5)
        
        # Frame de configuration
        config_frame = ttk.Frame(main_frame)
        config_frame.pack(fill='x', pady=(0, 10))
        
        # Sélection du pays/région
        ttk.Label(config_frame, text="Région à scanner:").grid(row=0, column=0, sticky='w')
        self.region_var = tk.StringVar()
        self.region_combo = ttk.Combobox(config_frame, textvariable=self.region_var, width=20, state='readonly')
        
        # Charger les pays depuis la config
        countries = list(self.config.get_countries().keys())
        self.region_combo['values'] = ["Plage personnalisée"] + countries
        self.region_combo.grid(row=0, column=1, padx=5, sticky='ew')
        self.region_combo.set("France")
        
        # Plage IP personnalisée
        ttk.Label(config_frame, text="IP personnalisée:").grid(row=1, column=0, sticky='w')
        self.custom_ip_var = tk.StringVar(value="192.168.1.0/24")
        custom_ip_entry = ttk.Entry(config_frame, textvariable=self.custom_ip_var, width=25)
        custom_ip_entry.grid(row=1, column=1, padx=5, sticky='ew')
        
        # Paramètres de scan
        params_frame = ttk.Frame(config_frame)
        params_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=10)
        
        ttk.Label(params_frame, text="Threads:").grid(row=0, column=0)
        self.threads_var = tk.StringVar(value=str(self.config.get_max_threads()))
        threads_spin = ttk.Spinbox(params_frame, from_=10, to=500, textvariable=self.threads_var, width=10)
        threads_spin.grid(row=0, column=1, padx=5)
        
        ttk.Label(params_frame, text="Timeout:").grid(row=0, column=2, padx=(20, 0))
        self.timeout_var = tk.StringVar(value=str(self.config.get_scan_timeout()))
        timeout_spin = ttk.Spinbox(params_frame, from_=1, to=10, textvariable=self.timeout_var, width=10)
        timeout_spin.grid(row=0, column=3, padx=5)
        
        # Boutons de contrôle
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')
        
        self.start_button = ttk.Button(button_frame, text="🔍 Démarrer le scan", command=self.start_scan)
        self.start_button.pack(side='left', padx=(0, 5))
        
        self.stop_button = ttk.Button(button_frame, text="⏹️ Arrêter", command=self.stop_scan, state='disabled')
        self.stop_button.pack(side='left', padx=5)
        
        # Boutons de sauvegarde
        ttk.Button(button_frame, text="💾 Sauvegarder", command=self.save_results).pack(side='right', padx=5)
        ttk.Button(button_frame, text="📂 Charger", command=self.load_results).pack(side='right')
        
        # Barre de progression
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill='x', pady=(10, 0))
        
        self.progress_bar = ttk.Progressbar(progress_frame, maximum=100)
        self.progress_bar.pack(fill='x', pady=(0, 5))
        
        self.status_label = ttk.Label(progress_frame, text="Prêt à scanner")
        self.status_label.pack()
        
        # Configuration de la grille
        config_frame.columnconfigure(1, weight=1)
    
    def start_scan(self):
        """Démarre le scan"""
        try:
            # Vérifier les paramètres
            max_threads = int(self.threads_var.get())
            timeout = int(self.timeout_var.get())
            
            # Déterminer les plages IP à scanner
            region = self.region_var.get()
            
            if region == "Plage personnalisée":
                ip_ranges = [self.custom_ip_var.get()]
            else:
                ip_ranges = self.config.get_country_ranges(region)
                if not ip_ranges:
                    messagebox.showerror("Erreur", f"Aucune plage IP configurée pour {region}")
                    return
            
            # Obtenir les ports à scanner
            ports = self.config.get_scan_ports()
            
            # Lancer le scan dans un thread séparé
            scan_thread = threading.Thread(
                target=self.run_scan,
                args=(ip_ranges, ports, max_threads, timeout),
                daemon=True
            )
            scan_thread.start()
            
        except ValueError:
            messagebox.showerror("Erreur", "Valeurs de paramètres invalides")
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du démarrage du scan: {e}")
    
    def run_scan(self, ip_ranges: List[str], ports: List[int], max_threads: int, timeout: int):
        """Lance le scan (à exécuter dans un thread)"""
        try:
            self.scanner.scan_multiple_ranges(ip_ranges, ports, max_threads, timeout)
        except Exception as e:
            print(f"Erreur durant le scan: {e}")
    
    def stop_scan(self):
        """Arrête le scan en cours"""
        self.scanner.stop_scan()
    
    def on_scan_started(self):
        """Appelé quand le scan démarre"""
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.progress_bar['value'] = 0
        self.status_label.config(text="Scan en cours...")
    
    def on_progress_update(self, progress: float, scanned: int, total: int, found: int):
        """Appelé lors de la mise à jour du progrès"""
        self.progress_bar['value'] = progress
        self.status_label.config(text=f"Scan: {scanned}/{total} IPs - {found} serveurs trouvés")
    
    def on_scan_complete(self, total_found: int):
        """Appelé quand le scan est terminé"""
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress_bar['value'] = 100
        self.status_label.config(text=f"Scan terminé - {total_found} serveurs trouvés")
    
    def save_results(self):
        """Sauvegarde les résultats du scan"""
        if not self.scanner.servers:
            messagebox.showwarning("Attention", "Aucun serveur à sauvegarder")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Sauvegarder les serveurs",
            defaultextension=".json",
            filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")]
        )
        
        if filename:
            self.scanner.save_servers(filename)
            messagebox.showinfo("Succès", f"Serveurs sauvegardés dans {filename}")
    
    def load_results(self):
        """Charge des résultats sauvegardés"""
        filename = filedialog.askopenfilename(
            title="Charger des serveurs",
            filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")]
        )
        
        if filename:
            self.scanner.load_servers(filename)
            messagebox.showinfo("Succès", f"Serveurs chargés depuis {filename}")

class ServerDetailsWindow:
    """Fenêtre de détails d'un serveur"""
    
    def __init__(self, parent, server: MinecraftServer):
        self.server = server
        self.window = tk.Toplevel(parent)
        self.window.title(f"Détails - {server.ip}:{server.port}")
        self.window.geometry("500x600")
        self.window.resizable(True, True)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configure l'interface de détails"""
        # Frame principal avec scrollbar
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Informations générales
        general_frame = ttk.LabelFrame(main_frame, text="Informations générales", padding="10")
        general_frame.pack(fill='x', pady=(0, 10))
        
        info_items = [
            ("IP:", f"{self.server.ip}:{self.server.port}"),
            ("Nom:", self.server.name or "Non défini"),
            ("Description:", self.server.description or "Non définie"),
            ("Version:", self.server.version or "Inconnue"),
            ("Protocole:", str(self.server.protocol)),
            ("Ping:", f"{self.server.ping}ms"),
            ("Whitelist:", "Oui" if self.server.whitelist else "Non"),
            ("Dernière vérification:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.server.last_seen)))
        ]
        
        for i, (label, value) in enumerate(info_items):
            ttk.Label(general_frame, text=label, font=('TkDefaultFont', 9, 'bold')).grid(row=i, column=0, sticky='nw', padx=(0, 10))
            ttk.Label(general_frame, text=value, wraplength=300).grid(row=i, column=1, sticky='nw')
        
        # Informations sur les joueurs
        players_frame = ttk.LabelFrame(main_frame, text="Joueurs", padding="10")
        players_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(players_frame, text=f"Connectés: {self.server.players_online}/{self.server.players_max}", 
                 font=('TkDefaultFont', 10, 'bold')).pack(anchor='w')
        
        if self.server.players_list:
            ttk.Label(players_frame, text="Joueurs en ligne:", font=('TkDefaultFont', 9, 'bold')).pack(anchor='w', pady=(10, 5))
            
            # Liste des joueurs dans un frame avec scrollbar
            players_list_frame = ttk.Frame(players_frame)
            players_list_frame.pack(fill='both', expand=True)
            
            players_text = tk.Text(players_list_frame, height=6, wrap='word')
            players_scrollbar = ttk.Scrollbar(players_list_frame, orient='vertical', command=players_text.yview)
            players_text.configure(yscrollcommand=players_scrollbar.set)
            
            players_text.pack(side='left', fill='both', expand=True)
            players_scrollbar.pack(side='right', fill='y')
            
            players_text.insert('1.0', '\n'.join(self.server.players_list))
            players_text.config(state='disabled')
        
        # Localisation
        location_frame = ttk.LabelFrame(main_frame, text="Localisation", padding="10")
        location_frame.pack(fill='x', pady=(0, 10))
        
        location_items = [
            ("Pays:", self.server.location.get('country', 'Inconnu')),
            ("Ville:", self.server.location.get('city', 'Inconnue')),
            ("Latitude:", str(self.server.location.get('lat', 0))),
            ("Longitude:", str(self.server.location.get('lon', 0)))
        ]
        
        for i, (label, value) in enumerate(location_items):
            ttk.Label(location_frame, text=label, font=('TkDefaultFont', 9, 'bold')).grid(row=i, column=0, sticky='w', padx=(0, 10))
            ttk.Label(location_frame, text=value).grid(row=i, column=1, sticky='w')
        
        # Favicon (si disponible)
        if self.server.favicon:
            favicon_frame = ttk.LabelFrame(main_frame, text="Icône du serveur", padding="10")
            favicon_frame.pack(fill='x', pady=(0, 10))
            
            try:
                # Décoder le favicon
                if self.server.favicon.startswith('data:image/png;base64,'):
                    base64_data = self.server.favicon[22:]
                else:
                    base64_data = self.server.favicon
                
                image_data = base64.b64decode(base64_data)
                image = Image.open(io.BytesIO(image_data))
                
                # Agrandir l'image pour l'affichage
                image = image.resize((64, 64), Image.Resampling.NEAREST)
                photo = ImageTk.PhotoImage(image)
                
                icon_label = ttk.Label(favicon_frame, image=photo)
                icon_label.image = photo  # Garder une référence
                icon_label.pack()
                
            except Exception as e:
                ttk.Label(favicon_frame, text="Erreur lors du chargement de l'icône").pack()
        
        # Boutons d'action
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Button(button_frame, text="Copier IP", command=self.copy_ip).pack(side='left', padx=(0, 5))
        ttk.Button(button_frame, text="Fermer", command=self.window.destroy).pack(side='right')
    
    def copy_ip(self):
        """Copie l'IP du serveur dans le presse-papiers"""
        ip_text = f"{self.server.ip}:{self.server.port}"
        self.window.clipboard_clear()
        self.window.clipboard_append(ip_text)
        messagebox.showinfo("Copié", f"IP copiée: {ip_text}")

class MineSpyderGUI:
    """Interface graphique principale de MineSpyder"""
    
    def __init__(self, root: tk.Tk, scanner: MinecraftScanner, config: Config):
        self.root = root
        self.scanner = scanner
        self.config = config
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configure l'interface principale"""
        # Configuration du style
        style = ttk.Style()
        
        # Menu principal
        self.create_menu()
        
        # Frame principal
        main_paned = ttk.PanedWindow(self.root, orient='vertical')
        main_paned.pack(fill='both', expand=True)
        
        # Frame de contrôle du scan (en haut)
        self.scan_control = ScanControlFrame(main_paned, self.scanner, self.config)
        main_paned.add(self.scan_control, weight=0)
        
        # Frame de la liste des serveurs (en bas)
        self.server_list = ServerListFrame(main_paned, self.scanner)
        main_paned.add(self.server_list, weight=1)
        
        # Barre de statut
        self.status_bar = ttk.Label(self.root, text="MineSpyder prêt - Aucun scan en cours", 
                                   relief='sunken', anchor='w')
        self.status_bar.pack(side='bottom', fill='x')
    
    def create_menu(self):
        """Crée le menu principal"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Nouveau scan", command=self.new_scan)
        file_menu.add_separator()
        file_menu.add_command(label="Sauvegarder les résultats...", command=self.save_results)
        file_menu.add_command(label="Charger des résultats...", command=self.load_results)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.root.quit)
        
        # Menu Edition
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edition", menu=edit_menu)
        edit_menu.add_command(label="Effacer la liste", command=self.clear_list)
        edit_menu.add_command(label="Actualiser", command=self.refresh_list)
        
        # Menu Outils
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Outils", menu=tools_menu)
        tools_menu.add_command(label="Configuration...", command=self.show_config)
        tools_menu.add_command(label="Statistiques", command=self.show_stats)
        
        # Menu Aide
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="À propos", command=self.show_about)
    
    def new_scan(self):
        """Démarre un nouveau scan"""
        self.server_list.clear_servers()
    
    def save_results(self):
        """Sauvegarde les résultats"""
        self.scan_control.save_results()
    
    def load_results(self):
        """Charge des résultats"""
        self.scan_control.load_results()
    
    def clear_list(self):
        """Efface la liste des serveurs"""
        self.server_list.clear_servers()
    
    def refresh_list(self):
        """Actualise la liste"""
        self.server_list.refresh_servers()
    
    def show_config(self):
        """Affiche la fenêtre de configuration"""
        messagebox.showinfo("Configuration", "Fenêtre de configuration à implémenter")
    
    def show_stats(self):
        """Affiche les statistiques"""
        total_servers = len(self.scanner.servers)
        if total_servers == 0:
            messagebox.showinfo("Statistiques", "Aucun serveur scanné")
            return
        
        # Calculer des statistiques
        countries = {}
        versions = {}
        total_players = 0
        
        for server in self.scanner.servers:
            # Compter par pays
            country = server.location.get('country', 'Inconnu')
            countries[country] = countries.get(country, 0) + 1
            
            # Compter par version
            version = server.version or 'Inconnue'
            versions[version] = versions.get(version, 0) + 1
            
            # Compter les joueurs
            total_players += server.players_online
        
        # Créer le message de statistiques
        stats_msg = f"Total de serveurs: {total_servers}\n"
        stats_msg += f"Total de joueurs: {total_players}\n\n"
        
        stats_msg += "Top 5 pays:\n"
        for country, count in sorted(countries.items(), key=lambda x: x[1], reverse=True)[:5]:
            stats_msg += f"  {country}: {count}\n"
        
        stats_msg += "\nTop 5 versions:\n"
        for version, count in sorted(versions.items(), key=lambda x: x[1], reverse=True)[:5]:
            stats_msg += f"  {version}: {count}\n"
        
        messagebox.showinfo("Statistiques", stats_msg)
    
    def show_about(self):
        """Affiche la fenêtre À propos"""
        about_text = """MineSpyder v1.0
        
Scanner de serveurs Minecraft

Développé pour découvrir des serveurs Minecraft
publics dans le monde entier.

Fonctionnalités:
• Scan par pays ou plage IP personnalisée
• Filtrage intelligent (pas de whitelist)
• Interface graphique intuitive
• Sauvegarde/chargement des résultats
• Informations détaillées sur les serveurs

⚠️ Utilisation responsable recommandée"""

        messagebox.showinfo("À propos de MineSpyder", about_text)
