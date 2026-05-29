# Assistant RAG - Analyse de Compétences RNCP (Dev IA)

Ce projet est une application d'Intelligence Artificielle basée sur une architecture **RAG (Retrieval-Augmented Generation)**. Son objectif est d'analyser la description d'un projet technique et d'identifier les compétences couvertes issues du référentiel RNCP "Développeur en Intelligence Artificielle".

## Fonctionnalités clés

* **Architecture Hybride (Cloud / Local) :** L'application interroge en priorité l'API Cloud ultra-rapide de Google (Gemini). En cas de panne de l'API ou de dépassement des quotas, le système bascule automatiquement (*fallback*) sur une IA locale via Ollama.
* **Vector Store Local :** Utilisation de FAISS pour stocker les embeddings du référentiel PDF, garantissant une recherche sémantique rapide et sans dépendance externe pour le stockage.
* **Interface Utilisateur Intuitive :** Développée avec Gradio pour une interaction fluide et conversationnelle.
* **Déploiement Conteneurisé :** Environnement 100% reproductible grâce à Docker, avec des versions de dépendances strictement figées (*Version Pinning*).

## Technologies Utilisées

* **Langage :** Python 3.10
* **Framework IA :** LangChain (v0.2.x)
* **LLMs :** Google Gemini (Cloud) / Phi3 ou Llama3 via Ollama (Local)
* **Embeddings :** Google Generative AI / Nomic-embed-text (Local)
* **Base Vectorielle :** FAISS
* **Interface Web :** Gradio (v4.44.1)
* **Déploiement :** Docker

---

##  Prérequis

Avant de lancer le projet, assurez-vous de disposer des éléments suivants :
1. **Python 3.10+** (pour l'exécution locale) ou **Docker** (pour l'exécution conteneurisée).
2. Une clé API Google AI Studio valide.
3. [Ollama](https://ollama.com/) installé sur votre machine (nécessaire uniquement pour tester le mode de secours local).

**Configuration d'Ollama (Si utilisation du fallback local) :**
```bash
ollama pull phi3
ollama pull nomic-embed-text
Installation & Configuration
Cloner le dépôt :

Bash
git clone https://github.com/Adjaaaaaaaa/Chatbot-RAG-Referentiel-Formation-Dev-IA.git
cd Chatbot-RAG-Referentiel-Formation-Dev-IA
Configurer les variables d'environnement :
Créez un fichier .env à la racine du projet et ajoutez-y votre clé API Google :

Extrait de code
GOOGLE_API_KEY=votre_cle_api_ici
GEMINI_MODEL=gemini-2.5-flash
OLLAMA_MODEL=phi3
Utilisation en mode Local (Développement)
Créer un environnement virtuel et installer les dépendances :

Bash
python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate
pip install -r requirements.txt
Ingérer les documents (Création de la base vectorielle) :
Cette étape lit le PDF du référentiel et crée les index FAISS. À exécuter une seule fois au début.

Bash
python ingest.py
Lancer l'application :

Bash
python app.py
L'interface sera accessible sur http://127.0.0.1:7860.

Déploiement avec Docker
L'application est configurée pour fonctionner dans un conteneur isolé, évitant tout conflit de dépendances.

Construire l'image Docker :

Bash
docker build -t chatbot-rncp .
Lancer le conteneur :

Bash
docker run -p 7860:7860 --env-file .env chatbot-rncp
Accéder à l'application :
Ouvrez votre navigateur web et rendez-vous sur : http://localhost:7860

Structure du Projet
Plaintext
📦 Chatbot-RAG-Referentiel-Formation-Dev-IA
 ┣ 📂 vector_store/      # Bases de données vectorielles FAISS générées
 ┣ 📜 app.py             # Script principal (Interface Gradio & Logique RAG)
 ┣ 📜 ingest.py          # Script d'ingestion et de découpage du PDF
 ┣ 📜 requirements.txt   # Dépendances Python (Versions épinglées)
 ┣ 📜 Dockerfile         # Configuration de l'image Docker
 ┣ 📜 .dockerignore      # Fichiers exclus du conteneur
 ┣ 📜 .env               # Variables d'environnement (API keys)
 ┗ 📜 README.md          # Documentation du projet


