import fitz
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

# Download stopwords for NLTK
nltk.download('stopwords')
from nltk.corpus import stopwords

# Load the sentence transformer model
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Define Category Embeddings
categories = {
    'Documento Financiero': ["factura", "recibo", "balance", "presupuesto", "orden de compra"],
    'Documento Legal': ["contrato", "acuerdo", "licencia", "política de privacidad", "términos y condiciones"],
    'Documento Académico': ["tesis", "ensayo", "investigación", "análisis", "resumen"],
    'Informe de Negocios': ["propuesta", "plan", "estrategia de marketing", "informe anual"],
    'Correspondencia Formal': ["carta", "invitación", "anuncio", "boletín", "agenda de reunión"],
    'Manual o Guía': ["manual", "guía", "catálogo", "protocolo"],
}

# Create embeddings for each category by averaging the keyword embeddings
category_embeddings = {
    category: np.mean(model.encode(samples), axis=0)
    for category, samples in categories.items()
}

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def clean_text(text):
    # Remove non-alphanumeric characters
    text = re.sub(r'\W+', ' ', text)
    # Lowercase and remove stopwords
    text = text.lower()
    words = text.split()
    stop_words = set(stopwords.words('spanish'))
    cleaned_text = ' '.join([word for word in words if word not in stop_words])
    return cleaned_text

def extract_keywords(text, top_n=10):
    # Adjust max_df to 1.0 or remove min_df
    vectorizer = TfidfVectorizer(max_df=1.0, max_features=10000, min_df=1)
    tfidf_matrix = vectorizer.fit_transform([text])
    feature_array = vectorizer.get_feature_names_out()
    tfidf_sorting = tfidf_matrix.toarray().argsort(axis=1)[:, ::-1]
    top_keywords = [feature_array[idx] for idx in tfidf_sorting[0, :top_n]]
    return top_keywords

def classify_document_by_keywords(keywords):
    # Create a single embedding for the document from its keywords
    document_embedding = np.mean(model.encode(keywords), axis=0)
    
    # Compute cosine similarity between document embedding and each category embedding
    similarities = {
        category: cosine_similarity([document_embedding], [cat_emb])[0][0]
        for category, cat_emb in category_embeddings.items()
    }
    
    # Identify the category with the highest similarity score
    best_category = max(similarities, key=similarities.get)
    return best_category, similarities

# Main Function
def analyze_pdf_document(pdf_path):
    # Extract and clean text
    raw_text = extract_text_from_pdf(pdf_path)
    cleaned_text = clean_text(raw_text)
    
    # Extract keywords
    keywords = extract_keywords(cleaned_text)
    
    # Predict document type
    doc_type, scores = classify_document_by_keywords(keywords)
    return doc_type, keywords, scores