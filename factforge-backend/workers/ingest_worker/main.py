"""
Ingest Worker - Classifies items and manages vector indexing
"""
import os
import json
import time
import pika
import psycopg2
from psycopg2.extras import RealDictCursor
import requests
from sentence_transformers import SentenceTransformer
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType
import logging
from typing import Dict, Any, List
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IngestWorker:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/factforge")
        self.rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
        self.milvus_host = os.getenv("MILVUS_HOST", "localhost")
        self.milvus_port = os.getenv("MILVUS_PORT", "19530")
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        
        # Initialize embedding model
        self.embedding_model = None
        self.load_embedding_model()
        
        # Initialize Milvus
        self.milvus_collection = None
        self.init_milvus()
        
        # Classification thresholds by language
        self.thresholds = {
            'hi': 0.90,
            'ta': 0.90,
            'kn': 0.90,
            'en': 0.92
        }

    def load_embedding_model(self):
        """Load sentence transformer model"""
        try:
            model_name = os.getenv("EMBEDDING_MODEL", "paraphrase-multilingual-mpnet-base-v2")
            self.embedding_model = SentenceTransformer(model_name)
            logger.info(f"Embedding model loaded: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")

    def init_milvus(self):
        """Initialize Milvus collection"""
        try:
            connections.connect(
                host=self.milvus_host,
                port=self.milvus_port
            )
            
            # Define collection schema
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="doc_id", dtype=DataType.VARCHAR, max_length=100),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=384),
                FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=10000),
                FieldSchema(name="language", dtype=DataType.VARCHAR, max_length=10),
                FieldSchema(name="label", dtype=DataType.VARCHAR, max_length=50),
                FieldSchema(name="score", dtype=DataType.FLOAT),
                FieldSchema(name="url", dtype=DataType.VARCHAR, max_length=500)
            ]
            
            schema = CollectionSchema(fields, "FactForge vector collection")
            
            # Create or get collection
            collection_name = "factforge_vectors"
            if connections.has_collection(collection_name):
                self.milvus_collection = Collection(collection_name)
            else:
                self.milvus_collection = Collection(collection_name, schema)
                # Create index
                index_params = {
                    "metric_type": "L2",
                    "index_type": "IVF_FLAT",
                    "params": {"nlist": 1024}
                }
                self.milvus_collection.create_index("embedding", index_params)
            
            logger.info("Milvus collection initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Milvus: {e}")

    def classify_text(self, text: str, language: str) -> float:
        """Classify text as scam or not using LLM"""
        try:
            prompt = f"""Classify the following text as scam (1.0) or not scam (0.0). 
            Respond with only a number between 0.0 and 1.0.

            Text: {text}
            Language: {language}

            Consider these factors:
            - Urgency and pressure tactics
            - Promises of easy money or prizes
            - Requests for personal information or payment
            - Suspicious URLs or contact methods
            - Grammatical errors or unprofessional language

            Score:"""

            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "llama3.2:3b",
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "top_p": 0.9
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "0.5").strip()
                
                # Extract number from response
                try:
                    score = float(response_text.split()[0])
                    return max(0.0, min(1.0, score))  # Clamp to [0, 1]
                except (ValueError, IndexError):
                    return 0.5  # Default neutral score
            else:
                logger.error(f"LLM classification failed: {response.status_code}")
                return 0.5
                
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return 0.5

    def generate_embedding(self, text: str, language: str) -> List[float]:
        """Generate embedding for text"""
        try:
            if self.embedding_model:
                embedding = self.embedding_model.encode(text)
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

    def store_vector(self, doc_id: str, text: str, language: str, label: str, score: float, url: str) -> int:
        """Store vector in Milvus and return vector ID"""
        try:
            if not self.milvus_collection:
                logger.error("Milvus collection not initialized")
                return None
            
            # Generate embedding
            embedding = self.generate_embedding(text, language)
            
            # Prepare data
            data = [{
                "doc_id": doc_id,
                "embedding": embedding,
                "text": text[:10000],  # Truncate if too long
                "language": language,
                "label": label,
                "score": score,
                "url": url[:500]  # Truncate if too long
            }]
            
            # Insert into Milvus
            result = self.milvus_collection.insert(data)
            self.milvus_collection.flush()
            
            # Get the generated ID
            vector_id = result.primary_keys[0]
            
            # Store mapping in database
            self.store_vector_mapping(doc_id, vector_id, embedding)
            
            logger.info(f"Stored vector for doc {doc_id} with ID {vector_id}")
            return vector_id
            
        except Exception as e:
            logger.error(f"Vector storage failed: {e}")
            return None

    def store_vector_mapping(self, doc_id: str, vector_id: int, embedding: List[float]):
        """Store vector mapping in database"""
        try:
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor()
            
            query = """
            INSERT INTO vectors (doc_id, embedding_id, milvus_id, metadata)
            VALUES (%s, %s, %s, %s)
            """
            
            cur.execute(query, (
                doc_id,
                f"emb_{doc_id}",
                str(vector_id),
                json.dumps({"embedding_dim": len(embedding)})
            ))
            
            conn.commit()
            cur.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Vector mapping storage failed: {e}")

    def add_to_review_queue(self, doc_id: str, score: float, language: str):
        """Add item to review queue"""
        try:
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor()
            
            query = """
            INSERT INTO review_queue (doc_id, status, priority, note)
            VALUES (%s, 'pending', %s, %s)
            """
            
            priority = 5 if score > 0.8 else 3
            note = f"Auto-queued: score={score:.3f}, lang={language}"
            
            cur.execute(query, (doc_id, priority, note))
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info(f"Added to review queue: {doc_id}")
            
        except Exception as e:
            logger.error(f"Review queue addition failed: {e}")

    def process_ingest_item(self, message: Dict[str, Any]) -> bool:
        """Process a single ingest item"""
        try:
            url = message['url']
            language = message['language']
            heuristic_score = message['heuristic_score']
            
            logger.info(f"Processing ingest item: {url}")
            
            # Get item from database
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            query = """
            SELECT id, clean_text, heuristic_score, domain
            FROM crawled_items 
            WHERE url = %s
            ORDER BY created_at DESC
            LIMIT 1
            """
            
            cur.execute(query, (url,))
            item = cur.fetchone()
            
            if not item:
                logger.error(f"Item not found in database: {url}")
                return False
            
            doc_id = str(item['id'])
            text = item['clean_text']
            
            # Classify text
            classifier_score = self.classify_text(text, language)
            
            # Determine label based on scores
            threshold = self.thresholds.get(language, 0.9)
            
            if classifier_score >= threshold:
                label = "scam"
                # Store vector for scam items
                vector_id = self.store_vector(doc_id, text, language, label, classifier_score, url)
                
                # Update database
                update_query = """
                UPDATE crawled_items 
                SET label = %s, classifier_score = %s
                WHERE id = %s
                """
                cur.execute(update_query, (label, classifier_score, doc_id))
                
            elif classifier_score >= 0.6:
                label = "pending"
                # Add to review queue
                self.add_to_review_queue(doc_id, classifier_score, language)
                
                # Update database
                update_query = """
                UPDATE crawled_items 
                SET label = %s, classifier_score = %s
                WHERE id = %s
                """
                cur.execute(update_query, (label, classifier_score, doc_id))
                
            else:
                label = "benign"
                # Update database
                update_query = """
                UPDATE crawled_items 
                SET label = %s, classifier_score = %s
                WHERE id = %s
                """
                cur.execute(update_query, (label, classifier_score, doc_id))
            
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info(f"Successfully processed: {url} -> {label} (score: {classifier_score:.3f})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process ingest item {url}: {e}")
            return False

    def start_consuming(self):
        """Start consuming messages from RabbitMQ"""
        try:
            connection = pika.BlockingConnection(pika.URLParameters(self.rabbitmq_url))
            channel = connection.channel()
            
            # Declare queue
            channel.queue_declare(queue='ingest.queue', durable=True)
            
            def callback(ch, method, properties, body):
                try:
                    message = json.loads(body)
                    success = self.process_ingest_item(message)
                    
                    if success:
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                    else:
                        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                        
                except Exception as e:
                    logger.error(f"Message processing failed: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
            # Set up consumer
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue='ingest.queue', on_message_callback=callback)
            
            logger.info("Ingest worker started, waiting for messages...")
            channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("Stopping ingest worker...")
            channel.stop_consuming()
            connection.close()
        except Exception as e:
            logger.error(f"Consumer error: {e}")

if __name__ == "__main__":
    worker = IngestWorker()
    worker.start_consuming()
