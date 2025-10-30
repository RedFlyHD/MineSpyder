#!/bin/bash
# Script de lancement MineSpyder pour macOS/Linux

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🕷️  Lancement de MineSpyder..."

# Se déplacer dans le répertoire du script
cd "$(dirname "$0")"

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 n'est pas installé${NC}"
    echo "Veuillez installer Python 3.7 ou plus récent"
    exit 1
fi

# Vérifier la version de Python
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo -e "${GREEN}✅ Python $python_version détecté${NC}"

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Création de l'environnement virtuel...${NC}"
    python3 -m venv venv
fi

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate

# Vérifier si les dépendances sont installées
echo "📦 Vérification des dépendances..."

if ! python -c "import requests, PIL" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Installation des dépendances requise${NC}"
    echo "Installation automatique..."
    pip install requests Pillow
fi

# Lancer l'application
echo -e "${GREEN}🚀 Lancement de MineSpyder...${NC}"
python main_simple.py

echo -e "${GREEN}👋 MineSpyder fermé${NC}"
