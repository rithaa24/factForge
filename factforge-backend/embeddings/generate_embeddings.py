"""
Generate embeddings for text data
"""
import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """Generate embeddings using sentence transformers"""
    
    def __init__(self, model_name: str = "paraphrase-multilingual-mpnet-base-v2"):
        self.model_name = model_name
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load the embedding model"""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def generate_embedding(self, text: str, language: str = "en") -> List[float]:
        """Generate embedding for a single text"""
        try:
            if self.model:
                embedding = self.model.encode(text)
                return embedding.tolist()
            else:
                # Fallback: generate dummy embedding
                import hashlib
                hash_obj = hashlib.md5(f"{text}_{language}".encode())
                hash_hex = hash_obj.hexdigest()
                
                embedding = []
                for i in range(0, len(hash_hex), 2):
                    val = int(hash_hex[i:i+2], 16) / 255.0
                    embedding.append(val)
                
                # Pad or truncate to 384 dimensions
                while len(embedding) < 384:
                    embedding.append(0.0)
                embedding = embedding[:384]
                
                return embedding
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return [0.0] * 384
    
    def generate_batch_embeddings(self, texts: List[str], languages: List[str] = None) -> List[List[float]]:
        """Generate embeddings for a batch of texts"""
        if languages is None:
            languages = ["en"] * len(texts)
        
        try:
            if self.model:
                embeddings = self.model.encode(texts)
                return embeddings.tolist()
            else:
                # Fallback: generate dummy embeddings
                embeddings = []
                for text, lang in zip(texts, languages):
                    embedding = self.generate_embedding(text, lang)
                    embeddings.append(embedding)
                return embeddings
        except Exception as e:
            logger.error(f"Batch embedding generation failed: {e}")
            return [[0.0] * 384] * len(texts)
    
    def normalize_text(self, text: str, language: str = "en") -> str:
        """Normalize text for embedding generation"""
        # Basic text normalization
        text = text.strip()
        
        # Remove extra whitespace
        text = " ".join(text.split())
        
        # Language-specific normalization
        if language in ["hi", "ta", "kn"]:
            # For Indic languages, ensure proper Unicode normalization
            import unicodedata
            text = unicodedata.normalize('NFC', text)
        
        return text
    
    def process_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process a list of documents and generate embeddings"""
        logger.info(f"Processing {len(documents)} documents")
        
        results = []
        
        for i, doc in enumerate(documents):
            try:
                text = doc.get("text", "")
                language = doc.get("language", "en")
                doc_id = doc.get("id", f"doc_{i}")
                
                # Normalize text
                normalized_text = self.normalize_text(text, language)
                
                # Generate embedding
                embedding = self.generate_embedding(normalized_text, language)
                
                # Create result
                result = {
                    "id": doc_id,
                    "text": normalized_text,
                    "language": language,
                    "embedding": embedding,
                    "embedding_dim": len(embedding),
                    "metadata": doc.get("metadata", {})
                }
                
                results.append(result)
                
                if (i + 1) % 100 == 0:
                    logger.info(f"Processed {i + 1}/{len(documents)} documents")
                    
            except Exception as e:
                logger.error(f"Failed to process document {i}: {e}")
                continue
        
        logger.info(f"Successfully processed {len(results)} documents")
        return results
    
    def save_embeddings(self, embeddings: List[Dict[str, Any]], output_file: str):
        """Save embeddings to file"""
        try:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(embeddings, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {len(embeddings)} embeddings to {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to save embeddings: {e}")
            raise

def load_sample_documents() -> List[Dict[str, Any]]:
    """Load sample documents for testing"""
    documents = [
        {
            "id": "doc_1",
            "text": "Send ₹1000 to UPI abc@upi to claim your lottery prize of ₹50,000! Limited time offer.",
            "language": "en",
            "metadata": {"category": "scam", "source": "test"}
        },
        {
            "id": "doc_2", 
            "text": "तत्काल ₹1000 UPI abc@upi पर भेजें और ₹50,000 का लॉटरी पुरस्कार जीतें!",
            "language": "hi",
            "metadata": {"category": "scam", "source": "test"}
        },
        {
            "id": "doc_3",
            "text": "The Earth is round and orbits around the Sun.",
            "language": "en",
            "metadata": {"category": "fact", "source": "test"}
        },
        {
            "id": "doc_4",
            "text": "पृथ्वी गोल है और सूर्य के चारों ओर घूमती है।",
            "language": "hi",
            "metadata": {"category": "fact", "source": "test"}
        },
        {
            "id": "doc_5",
            "text": "₹1000 ஐ UPI abc@upi க்கு உடனடியாக அனுப்பி ₹50,000 லாட்டரி பரிசை வெல்லுங்கள்!",
            "language": "ta",
            "metadata": {"category": "scam", "source": "test"}
        },
        {
            "id": "doc_6",
            "text": "பூமி உருண்டையானது மற்றும் சூரியனைச் சுற்றி வருகிறது.",
            "language": "ta",
            "metadata": {"category": "fact", "source": "test"}
        },
        {
            "id": "doc_7",
            "text": "ತಕ್ಷಣ ₹1000 ಅನ್ನು UPI abc@upi ಗೆ ಕಳುಹಿಸಿ ₹50,000 ಲಾಟರಿ ಬಹುಮಾನವನ್ನು ಗೆಲ್ಲಿ!",
            "language": "kn",
            "metadata": {"category": "scam", "source": "test"}
        },
        {
            "id": "doc_8",
            "text": "ಭೂಮಿ ಗೋಳಾಕಾರದಲ್ಲಿದೆ ಮತ್ತು ಸೂರ್ಯನ ಸುತ್ತ ಸುತ್ತುತ್ತದೆ.",
            "language": "kn",
            "metadata": {"category": "fact", "source": "test"}
        }
    ]
    
    return documents

def main():
    """Main function"""
    logger.info("Starting embedding generation...")
    
    # Initialize generator
    generator = EmbeddingGenerator()
    
    # Load sample documents
    documents = load_sample_documents()
    
    # Process documents
    embeddings = generator.process_documents(documents)
    
    # Save embeddings
    output_file = "embeddings/sample_embeddings.json"
    generator.save_embeddings(embeddings, output_file)
    
    # Print summary
    logger.info("Embedding generation completed!")
    logger.info(f"Generated {len(embeddings)} embeddings")
    logger.info(f"Embedding dimension: {len(embeddings[0]['embedding'])}")
    
    # Print language distribution
    languages = [emb["language"] for emb in embeddings]
    from collections import Counter
    lang_counts = Counter(languages)
    logger.info(f"Language distribution: {dict(lang_counts)}")

if __name__ == "__main__":
    main()
