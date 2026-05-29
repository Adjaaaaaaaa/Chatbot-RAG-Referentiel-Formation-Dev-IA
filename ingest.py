import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Charger les variables d'environnement du fichier .env
load_dotenv()

DATA_PATH = "data/referentiel_rncp_dev_ia.pdf"

# Déterminer la cible en fonction de la présence de la clé API
USE_GEMINI = bool(os.getenv("GOOGLE_API_KEY"))
VECTOR_STORE_PATH = "vector_store/faiss_index_gemini" if USE_GEMINI else "vector_store/faiss_index_ollama"

def create_vector_store():
    """
    Charge le document PDF, le découpe en chunks, crée les embeddings
    et les stocke dans un Vector Store FAISS.
    """
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(
            f"Le fichier PDF n'a pas été trouvé à l'emplacement : {DATA_PATH}. "
            "Veuillez vous assurer que le fichier 'referentiel_rncp_dev_ia.pdf' est bien dans le dossier 'data' à la racine du projet."
        )

    print("Chargement du document...")
    loader = PyPDFLoader(DATA_PATH)
    documents = loader.load()

    print("Découpage du document en chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    docs = text_splitter.split_documents(documents)

    print(f"Nombre de chunks créés : {len(docs)}")

    # Choix conditionnel des Embeddings
    if USE_GEMINI:
        print(" Utilisation de GEMINI pour les embeddings...")
       
        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")
    else:
        print(" Utilisation d'OLLAMA pour les embeddings...")
        embeddings = OllamaEmbeddings(
           model="nomic-embed-text"
        )
    
    print(f"Création et sauvegarde du Vector Store dans {VECTOR_STORE_PATH}...")
    vector_store = FAISS.from_documents(docs, embeddings)
    vector_store.save_local(VECTOR_STORE_PATH)
    print("Le Vector Store a été créé et sauvegardé avec succès.")


if __name__ == "__main__":
    create_vector_store()