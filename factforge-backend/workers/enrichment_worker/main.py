"""
Enrichment Worker - Processes crawled items with OCR, LID, and transliteration
"""
import os
import json
import time
import hashlib
import pika
import psycopg2
from psycopg2.extras import RealDictCursor
from bs4 import BeautifulSoup
import requests
from PIL import Image
import pytesseract
import fasttext
import indic_transliteration
from indic_transliteration import sanscript
import imagehash
import whois
import re
from typing import Dict, Any, List, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnrichmentWorker:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/factforge")
        self.rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
        self.tessdata_prefix = os.getenv("TESSDATA_PREFIX", "/usr/share/tessdata")
        
        # Initialize language detection model
        self.lid_model = None
        self.load_lid_model()
        
        # Language mappings
        self.language_mappings = {
            'hi': 'hin',
            'ta': 'tam', 
            'kn': 'kan',
            'en': 'eng'
        }
        
        # Scam keywords by language
        self.scam_keywords = {
            'en': ['urgent', 'limited time', 'act now', 'guaranteed', 'free money', 'lottery', 'winner'],
            'hi': ['तत्काल', 'सीमित समय', 'अभी करें', 'गारंटी', 'मुफ्त पैसा', 'लॉटरी', 'विजेता'],
            'ta': ['அவசரம்', 'வரம்புக்குட்பட்ட நேரம்', 'இப்போது செய்யுங்கள்', 'உத்தரவாதம்', 'இலவச பணம்', 'லாட்டரி', 'வெற்றியாளர்'],
            'kn': ['ತುರ್ತು', 'ಸೀಮಿತ ಸಮಯ', 'ಈಗ ಮಾಡಿ', 'ಖಾತರಿ', 'ಉಚಿತ ಹಣ', 'ಲಾಟರಿ', 'ವಿಜೇತ']
        }
        
        # UPI and phone patterns
        self.upi_pattern = r'\b\w+@\w+\b'
        self.phone_pattern = r'(\+91|91)?[6-9]\d{9}'
        self.rupee_pattern = r'[₹₹]\s*\d+'

    def load_lid_model(self):
        """Load fastText language detection model"""
        try:
            model_path = os.getenv("LID_MODEL_PATH", "/app/models/lid.176.ftz")
            if os.path.exists(model_path):
                self.lid_model = fasttext.load_model(model_path)
                logger.info("Language detection model loaded successfully")
            else:
                logger.warning("Language detection model not found, using heuristics")
        except Exception as e:
            logger.error(f"Failed to load language detection model: {e}")

    def detect_language(self, text: str) -> Tuple[str, float]:
        """Detect language of text"""
        if self.lid_model:
            try:
                predictions = self.lid_model.predict(text, k=1)
                lang_code = predictions[0][0].replace('__label__', '')
                confidence = float(predictions[1][0])
                
                # Map to our language codes
                lang_mapping = {
                    'hi': 'hi',
                    'ta': 'ta', 
                    'kn': 'kn',
                    'en': 'en'
                }
                
                detected_lang = lang_mapping.get(lang_code, 'en')
                return detected_lang, confidence
            except Exception as e:
                logger.error(f"Language detection failed: {e}")
        
        # Fallback to heuristic detection
        return self._heuristic_language_detection(text)

    def _heuristic_language_detection(self, text: str) -> Tuple[str, float]:
        """Heuristic language detection based on script"""
        # Check for Tamil script
        if any('\u0B80' <= char <= '\u0BFF' for char in text):
            return 'ta', 0.9
        
        # Check for Hindi/Devanagari script
        if any('\u0900' <= char <= '\u097F' for char in text):
            return 'hi', 0.9
        
        # Check for Kannada script
        if any('\u0C80' <= char <= '\u0CFF' for char in text):
            return 'kn', 0.9
        
        # Check for English
        english_words = ['the', 'and', 'is', 'in', 'to', 'of', 'a', 'that', 'it', 'with']
        text_lower = text.lower()
        english_score = sum(1 for word in english_words if word in text_lower) / len(english_words)
        
        if english_score > 0.3:
            return 'en', english_score
        
        return 'en', 0.5

    def clean_html(self, html_content: str) -> str:
        """Clean HTML content to extract text"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text and clean up
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            logger.error(f"HTML cleaning failed: {e}")
            return ""

    def extract_text_from_image(self, image_path: str, language: str) -> str:
        """Extract text from image using OCR"""
        try:
            if not os.path.exists(image_path):
                return ""
            
            # Map language to Tesseract language code
            tess_lang = self.language_mappings.get(language, 'eng')
            
            # Configure Tesseract
            config = f'--oem 3 --psm 6 -l {tess_lang}'
            
            # Extract text
            text = pytesseract.image_to_string(Image.open(image_path), config=config)
            
            return text.strip()
        except Exception as e:
            logger.error(f"OCR failed for {image_path}: {e}")
            return ""

    def detect_transliteration(self, text: str, language: str) -> bool:
        """Detect if text contains transliterated content"""
        if language == 'en':
            # Check for romanized Hindi words
            hindi_words = ['hai', 'hain', 'ka', 'ki', 'ke', 'ko', 'se', 'mein', 'par', 'aur']
            text_lower = text.lower()
            hindi_count = sum(1 for word in hindi_words if word in text_lower)
            
            if hindi_count >= 3:
                return True
        
        return False

    def transliterate_text(self, text: str, from_script: str, to_script: str) -> str:
        """Transliterate text between scripts"""
        try:
            if from_script == 'latin' and to_script == 'devanagari':
                return indic_transliteration.transliterate(text, sanscript.ITRANS, sanscript.DEVANAGARI)
            elif from_script == 'latin' and to_script == 'tamil':
                return indic_transliteration.transliterate(text, sanscript.ITRANS, sanscript.TAMIL)
            elif from_script == 'latin' and to_script == 'kannada':
                return indic_transliteration.transliterate(text, sanscript.ITRANS, sanscript.KANNADA)
            else:
                return text
        except Exception as e:
            logger.error(f"Transliteration failed: {e}")
            return text

    def extract_patterns(self, text: str) -> Dict[str, List[str]]:
        """Extract UPI, phone, and rupee patterns"""
        patterns = {
            'upi_handles': re.findall(self.upi_pattern, text),
            'phone_numbers': re.findall(self.phone_pattern, text),
            'rupee_amounts': re.findall(self.rupee_pattern, text)
        }
        return patterns

    def get_domain_info(self, domain: str) -> Dict[str, Any]:
        """Get WHOIS information for domain"""
        try:
            domain_info = whois.whois(domain)
            return {
                'creation_date': str(domain_info.creation_date) if domain_info.creation_date else None,
                'expiration_date': str(domain_info.expiration_date) if domain_info.expiration_date else None,
                'registrar': domain_info.registrar,
                'country': domain_info.country,
                'org': domain_info.org
            }
        except Exception as e:
            logger.error(f"WHOIS lookup failed for {domain}: {e}")
            return {}

    def compute_image_hashes(self, image_path: str) -> List[str]:
        """Compute image hashes for duplicate detection"""
        try:
            if not os.path.exists(image_path):
                return []
            
            image = Image.open(image_path)
            hashes = [
                str(imagehash.average_hash(image)),
                str(imagehash.phash(image)),
                str(imagehash.dhash(image)),
                str(imagehash.whash(image))
            ]
            return hashes
        except Exception as e:
            logger.error(f"Image hashing failed for {image_path}: {e}")
            return []

    def compute_heuristic_score(self, text: str, language: str, patterns: Dict[str, List[str]], 
                               domain_info: Dict[str, Any]) -> float:
        """Compute heuristic scam score"""
        score = 0.0
        
        # Check for scam keywords
        keywords = self.scam_keywords.get(language, self.scam_keywords['en'])
        text_lower = text.lower()
        
        for keyword in keywords:
            if keyword.lower() in text_lower:
                score += 2.0
        
        # Check for urgency indicators
        urgency_words = ['urgent', 'immediate', 'hurry', 'limited', 'expires']
        for word in urgency_words:
            if word in text_lower:
                score += 1.5
        
        # Check for payment patterns
        if patterns['upi_handles']:
            score += 3.0
        if patterns['phone_numbers']:
            score += 2.0
        if patterns['rupee_amounts']:
            score += 1.0
        
        # Check domain age
        if domain_info.get('creation_date'):
            try:
                from datetime import datetime
                creation_date = datetime.strptime(domain_info['creation_date'], '%Y-%m-%d %H:%M:%S')
                days_old = (datetime.now() - creation_date).days
                if days_old < 30:
                    score += 5.0
                elif days_old < 90:
                    score += 2.0
            except:
                pass
        
        # Normalize score to 0-100
        return min(score * 10, 100.0)

    def process_crawled_item(self, message: Dict[str, Any]) -> bool:
        """Process a single crawled item"""
        try:
            url = message['url']
            html_path = message.get('html_path')
            screenshot_path = message.get('screenshot_path')
            text = message.get('text', '')
            domain = message.get('domain', '')
            
            logger.info(f"Processing item: {url}")
            
            # Clean HTML if available
            if html_path and os.path.exists(html_path):
                with open(html_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                clean_text = self.clean_html(html_content)
            else:
                clean_text = text
            
            # Detect language
            language, lang_confidence = self.detect_language(clean_text)
            
            # Detect transliteration
            translit = self.detect_transliteration(clean_text, language)
            
            # OCR images if available
            ocr_text = ""
            if screenshot_path and os.path.exists(screenshot_path):
                ocr_text = self.extract_text_from_image(screenshot_path, language)
                if translit and language == 'en':
                    # Also try OCR with English for transliterated content
                    ocr_text_en = self.extract_text_from_image(screenshot_path, 'en')
                    if len(ocr_text_en) > len(ocr_text):
                        ocr_text = ocr_text_en
            
            # Combine text sources
            full_text = f"{clean_text} {ocr_text}".strip()
            
            # Extract patterns
            patterns = self.extract_patterns(full_text)
            
            # Get domain information
            domain_info = self.get_domain_info(domain)
            
            # Compute image hashes
            image_hashes = []
            if screenshot_path and os.path.exists(screenshot_path):
                image_hashes = self.compute_image_hashes(screenshot_path)
            
            # Compute heuristic score
            heuristic_score = self.compute_heuristic_score(full_text, language, patterns, domain_info)
            
            # Store in database
            self.store_processed_item(
                url=url,
                domain=domain,
                html_path=html_path,
                screenshot_path=screenshot_path,
                clean_text=full_text,
                language=language,
                lang_confidence=lang_confidence,
                translit=translit,
                heuristic_score=heuristic_score,
                patterns=patterns,
                domain_info=domain_info,
                image_hashes=image_hashes
            )
            
            # Send to ingest queue
            self.send_to_ingest_queue(url, language, heuristic_score)
            
            logger.info(f"Successfully processed: {url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process item {url}: {e}")
            return False

    def store_processed_item(self, **kwargs):
        """Store processed item in database"""
        try:
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor()
            
            query = """
            INSERT INTO crawled_items 
            (url, domain, raw_html_path, screenshot_path, clean_text, language, 
             lang_confidence, translit, heuristic_score, image_hashes, whois_data, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """
            
            cur.execute(query, (
                kwargs['url'],
                kwargs['domain'],
                kwargs['html_path'],
                kwargs['screenshot_path'],
                kwargs['clean_text'],
                kwargs['language'],
                kwargs['lang_confidence'],
                kwargs['translit'],
                kwargs['heuristic_score'],
                json.dumps(kwargs['image_hashes']),
                json.dumps(kwargs['domain_info']),
                json.dumps(kwargs['patterns'])
            ))
            
            item_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info(f"Stored item with ID: {item_id}")
            return item_id
            
        except Exception as e:
            logger.error(f"Database storage failed: {e}")
            raise

    def send_to_ingest_queue(self, url: str, language: str, heuristic_score: float):
        """Send item to ingest queue for classification"""
        try:
            connection = pika.BlockingConnection(pika.URLParameters(self.rabbitmq_url))
            channel = connection.channel()
            
            channel.queue_declare(queue='ingest.queue', durable=True)
            
            message = {
                'url': url,
                'language': language,
                'heuristic_score': heuristic_score,
                'timestamp': time.time()
            }
            
            channel.basic_publish(
                exchange='',
                routing_key='ingest.queue',
                body=json.dumps(message),
                properties=pika.BasicProperties(delivery_mode=2)
            )
            
            connection.close()
            logger.info(f"Sent to ingest queue: {url}")
            
        except Exception as e:
            logger.error(f"Failed to send to ingest queue: {e}")

    def start_consuming(self):
        """Start consuming messages from RabbitMQ"""
        try:
            connection = pika.BlockingConnection(pika.URLParameters(self.rabbitmq_url))
            channel = connection.channel()
            
            # Declare queue
            channel.queue_declare(queue='crawl.items', durable=True)
            
            def callback(ch, method, properties, body):
                try:
                    message = json.loads(body)
                    success = self.process_crawled_item(message)
                    
                    if success:
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                    else:
                        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                        
                except Exception as e:
                    logger.error(f"Message processing failed: {e}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
            # Set up consumer
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue='crawl.items', on_message_callback=callback)
            
            logger.info("Enrichment worker started, waiting for messages...")
            channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("Stopping enrichment worker...")
            channel.stop_consuming()
            connection.close()
        except Exception as e:
            logger.error(f"Consumer error: {e}")

if __name__ == "__main__":
    worker = EnrichmentWorker()
    worker.start_consuming()
