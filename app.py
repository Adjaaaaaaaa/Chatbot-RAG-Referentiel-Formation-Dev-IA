import os
import gradio as gr
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# Charger les variables d'environnement
load_dotenv()

# Variables globales
GLOBAL_QA_CHAIN = None
CURRENT_PROVIDER = "Aucun"

def get_llm_and_embeddings():
    """Tente de charger Gemini, sinon bascule sur Ollama de façon transparente."""
    api_key = os.getenv("GOOGLE_API_KEY")
    
    # 1. Tentative avec Gemini
    if api_key:
        try:
            print("Tentative de connexion à Gemini...")
            llm = ChatGoogleGenerativeAI(
                model=os.getenv("GEMINI_MODEL", "gemini-2.5-pro"), 
                temperature=0.1
            )

            embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")
            vector_store_path = "vector_store/faiss_index_gemini"
            return llm, embeddings, vector_store_path, "Gemini Pro"
        except Exception as e:
            print(f"Échec de l'initialisation Gemini ({e}). Bascule sur Ollama...")

    # 2. Fallback sur Ollama
    print("Initialisation de la solution de secours : Ollama...")
    llm = ChatOllama(
        model="phi3",
        temperature=0.1
    )
    embeddings = OllamaEmbeddings(
        model="nomic-embed-text"
    )
    vector_store_path = "vector_store/faiss_index_ollama"
    return llm, embeddings, vector_store_path, "Ollama (Local)"

def load_retrieval_qa_chain():
    """Charge le Vector Store, initialise le LLM et le retriever."""
    global CURRENT_PROVIDER
    llm, embeddings, vector_store_path, CURRENT_PROVIDER = get_llm_and_embeddings()

    # Vérifier si le Vector Store correspondant existe
    if not os.path.exists(vector_store_path):
        raise FileNotFoundError(
            f"Le Vector Store pour {CURRENT_PROVIDER} n'a pas été trouvé à l'emplacement : {vector_store_path}. "
            "Veuillez exécuter le script 'ingest.py' pour le créer."
        )

    # Charger le Vector Store
    vector_store = FAISS.load_local(vector_store_path, embeddings, allow_dangerous_deserialization=True)

    # Configurer le retriever
    retriever = vector_store.as_retriever(
        search_type="similarity", 
        search_kwargs={'k': 5}
    )

    # Construire le prompt système
    prompt_template = """
    Tu es un assistant expert chargé d'analyser la couverture des compétences du référentiel RNCP "Développeur IA" de Simplon.
    Utilise UNIQUEMENT les extraits du référentiel fournis ci-dessous pour répondre à la question. Ne te base pas sur tes connaissances générales.

    Contexte (extraits du référentiel) :
    {context}

    Question de l'utilisateur (description du projet) :
    {question}

    Ta mission est de fournir une réponse structurée en trois parties :
    1.  **Compétences RNCP couvertes** : Liste chaque compétence couverte (ex: C1, C5...). Pour chaque compétence, justifie ta réponse en citant un passage pertinent des extraits fournis.
    2.  **Compétences potentiellement manquantes** : Liste les compétences qui ne semblent pas être couvertes par la description du projet et qui sont importantes pour le bloc de compétences concerné.
    3.  **Justification** : Explique brièvement pourquoi certaines compétences sont considérées comme manquantes.

    Format de la réponse attendue (utilise Markdown) :
    ### ✅ Compétences Couvertes
    - **C[Numéro] - [Titre de la compétence]** : Justification basée sur l'extrait "...".
    
    ### ❌ Compétences Manquantes ou à Préciser
    - **C[Numéro] - [Titre de la compétence]** : Il manque des informations sur [aspect manquant] pour valider cette compétence.
    
    Réponse :
    """
    
    QA_CHAIN_PROMPT = PromptTemplate.from_template(prompt_template)

    # Créer la chaîne RetrievalQA
    qa_chain = RetrievalQA.from_chain_type(
        llm,
        retriever=retriever,
        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
        return_source_documents=True
    )
    return qa_chain

def analyze_project(project_description):
    """Fonction appelée par l'interface Gradio."""
    global GLOBAL_QA_CHAIN
    
    try:
        if GLOBAL_QA_CHAIN is None:
            GLOBAL_QA_CHAIN = load_retrieval_qa_chain()
            
        result = GLOBAL_QA_CHAIN.invoke({"query": project_description})
        
        # Affichage du modèle utilisé pour prouver que le fallback fonctionne
        final_response = f"*(Analyse générée via **{CURRENT_PROVIDER}**)*\n\n" + result['result']
        
        # Affichage des sources consultées
        if 'source_documents' in result and result['source_documents']:
            final_response += "\n\n---\n### 📚 Sources consultées (Extraits du référentiel)\n"
            for i, doc in enumerate(result['source_documents']):
                content = doc.page_content.replace('\n', ' ')
                final_response += f"- **Extrait {i+1}** : *{content}*\n"
                
        return final_response
        
    except Exception as e:
        return f"### Une erreur est survenue\n\n```text\n{str(e)}\n```\n\n*Assurez-vous que la base vectorielle est générée (`python ingest.py`).*"

# Interface Gradio
iface = gr.Interface(
    fn=analyze_project,
    inputs=gr.Textbox(lines=10, label="Décrivez votre projet ici", placeholder="Ex: J'ai développé une API REST avec FastAPI, conteneurisée avec Docker et déployée via un pipeline CI/CD sur GitHub Actions..."),
    outputs=gr.Markdown(label="Analyse de couverture des compétences RNCP"),
    title="🤖 Assistant d'analyse de compétences RNCP Dev IA",
    description="Cet outil analyse la description de votre projet pour identifier les compétences du référentiel RNCP couvertes. L'architecture RAG bascule automatiquement sur un modèle local si l'API Cloud est inaccessible.",
    allow_flagging="never"
)

if __name__ == "__main__":
   iface.launch(server_name="0.0.0.0", server_port=7860)