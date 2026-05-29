# Utilisation d'une image Python officielle et légère (version 3.10 pour éviter les conflits)
FROM python:3.10-slim

# Définition du répertoire de travail dans le conteneur
WORKDIR /app

# Copie uniquement le fichier requirements en premier (pour optimiser le cache Docker)
COPY requirements.txt .

# Installation des dépendances sans garder le cache pour alléger l'image finale
RUN pip install --no-cache-dir -r requirements.txt

# Copie de tout le reste du code (app.py, ingest.py, le PDF, et surtout le dossier vector_store)
COPY . .

# Variables d'environnement indispensables pour que Gradio soit accessible de l'extérieur
ENV GRADIO_SERVER_NAME="0.0.0.0"
ENV GRADIO_SERVER_PORT="7860"

# Exposition du port utilisé par Gradio
EXPOSE 7860

# Commande par défaut au démarrage du conteneur
CMD ["python", "app.py"]