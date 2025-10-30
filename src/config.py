"""
Configuration et paramètres de l'application MineSpyder
"""

import json
import os
from typing import Dict, List, Any

class Config:
    """Classe de configuration de l'application"""
    
    def __init__(self):
        self.config_file = "config.json"
        self.default_config = {
            "scan_settings": {
                "timeout": 3,
                "max_threads": 100,
                "ports": [25565, 25566, 25567, 25568, 25569],
                "scan_ranges": [
                    "8.8.8.0/24",  # Exemple de plage
                    "1.1.1.0/24"   # Exemple de plage
                ]
            },
            "display_settings": {
                "max_servers_displayed": 1000,
                "refresh_interval": 30,
                "show_offline_servers": False
            },
            "countries": {
                "France": ["FR", "194.2.0.0/16", "193.252.0.0/16"],
                "United States": ["US", "8.8.8.0/16", "4.4.4.0/16"],
                "Germany": ["DE", "87.106.0.0/16", "85.214.0.0/16"],
                "United Kingdom": ["GB", "81.2.69.0/24", "82.132.0.0/16"],
                "Canada": ["CA", "99.224.0.0/16", "142.4.0.0/16"],
                "Australia": ["AU", "1.128.0.0/11", "27.32.0.0/11"],
                "Japan": ["JP", "133.205.0.0/16", "202.32.0.0/11"],
                "Brazil": ["BR", "189.0.0.0/8", "177.0.0.0/8"]
            },
            "geoip": {
                "database_path": "data/GeoLite2-City.mmdb",
                "auto_update": True
            }
        }
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Charge la configuration depuis le fichier"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # Fusionner avec la config par défaut pour les nouvelles clés
                return self.merge_configs(self.default_config, config)
            except Exception as e:
                print(f"⚠️  Erreur lors du chargement de la config : {e}")
                return self.default_config.copy()
        else:
            # Créer le fichier de config avec les valeurs par défaut
            self.save_config(self.default_config)
            return self.default_config.copy()
    
    def merge_configs(self, default: Dict, user: Dict) -> Dict:
        """Fusionne la configuration utilisateur avec la configuration par défaut"""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_config(self, config: Dict[str, Any] = None):
        """Sauvegarde la configuration dans le fichier"""
        if config is None:
            config = self.config
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Erreur lors de la sauvegarde de la config : {e}")
    
    def get(self, key: str, default=None):
        """Récupère une valeur de configuration"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Définit une valeur de configuration"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save_config()
    
    def get_scan_timeout(self) -> int:
        """Récupère le timeout de scan"""
        return self.get('scan_settings.timeout', 3)
    
    def get_max_threads(self) -> int:
        """Récupère le nombre maximum de threads"""
        return self.get('scan_settings.max_threads', 100)
    
    def get_scan_ports(self) -> List[int]:
        """Récupère la liste des ports à scanner"""
        return self.get('scan_settings.ports', [25565])
    
    def get_countries(self) -> Dict[str, List[str]]:
        """Récupère la liste des pays et leurs plages IP"""
        return self.get('countries', {})
    
    def get_country_ranges(self, country: str) -> List[str]:
        """Récupère les plages IP d'un pays spécifique"""
        countries = self.get_countries()
        if country in countries:
            return countries[country][1:]  # Ignore le code pays
        return []
