"""
Data preparation for classifier training
"""
import os
import json
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
import logging
from pathlib import Path
import re
import unicodedata

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataPreparator:
    """Prepare training data for classifier"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path("models/data")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Language mappings
        self.language_map = {
            "en": "english",
            "hi": "hindi", 
            "ta": "tamil",
            "kn": "kannada"
        }
        
        # Scam keywords by language
        self.scam_keywords = {
            "en": [
                "lottery", "prize", "winner", "congratulations", "urgent",
                "limited time", "act now", "click here", "free money",
                "guaranteed", "no risk", "instant", "immediate", "exclusive",
                "secret", "hidden", "special offer", "once in a lifetime"
            ],
            "hi": [
                "लॉटरी", "पुरस्कार", "विजेता", "बधाई", "तत्काल",
                "सीमित समय", "अभी कार्य करें", "यहाँ क्लिक करें", "मुफ्त पैसा",
                "गारंटी", "कोई जोखिम नहीं", "तुरंत", "तत्काल", "विशेष",
                "गुप्त", "छुपा", "विशेष प्रस्ताव", "जीवन में एक बार"
            ],
            "ta": [
                "லாட்டரி", "பரிசு", "வெற்றியாளர்", "வாழ்த்துக்கள்", "அவசரம்",
                "வரம்புக்குட்பட்ட நேரம்", "இப்போது செயல்படுங்கள்", "இங்கே கிளிக் செய்யுங்கள்", "இலவச பணம்",
                "உத்தரவாதம்", "ஆபத்து இல்லை", "உடனடி", "உடனடி", "விசேஷ",
                "ரகசியம்", "மறைக்கப்பட்ட", "விசேஷ சலுகை", "வாழ்க்கையில் ஒரு முறை"
            ],
            "kn": [
                "ಲಾಟರಿ", "ಬಹುಮಾನ", "ವಿಜೇತ", "ಅಭಿನಂದನೆಗಳು", "ತುರ್ತು",
                "ಸೀಮಿತ ಸಮಯ", "ಈಗ ಕಾರ್ಯನಿರ್ವಹಿಸಿ", "ಇಲ್ಲಿ ಕ್ಲಿಕ್ ಮಾಡಿ", "ಉಚಿತ ಹಣ",
                "ಭರವಸೆ", "ಅಪಾಯವಿಲ್ಲ", "ತಕ್ಷಣ", "ತಕ್ಷಣ", "ವಿಶೇಷ",
                "ರಹಸ್ಯ", "ಗುಪ್ತ", "ವಿಶೇಷ ಪ್ರಸ್ತಾಪ", "ಜೀವನದಲ್ಲಿ ಒಮ್ಮೆ"
            ]
        }
    
    def load_sample_claims(self) -> List[Dict[str, Any]]:
        """Load sample claims from demo data"""
        claims_file = self.data_dir / "demo" / "sample_claims.json"
        
        if not claims_file.exists():
            logger.warning(f"Sample claims file not found: {claims_file}")
            return []
        
        with open(claims_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        claims = []
        for lang_claims in data.values():
            claims.extend(lang_claims)
        
        logger.info(f"Loaded {len(claims)} sample claims")
        return claims
    
    def create_synthetic_data(self, base_claims: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create synthetic training data by augmenting base claims"""
        synthetic_data = []
        
        for claim in base_claims:
            # Original claim
            synthetic_data.append(claim)
            
            # Create variations
            variations = self._create_variations(claim)
            synthetic_data.extend(variations)
        
        logger.info(f"Created {len(synthetic_data)} synthetic claims from {len(base_claims)} base claims")
        return synthetic_data
    
    def _create_variations(self, claim: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create variations of a claim"""
        variations = []
        
        # Add urgency variations
        urgency_phrases = {
            "en": ["URGENT!", "LIMITED TIME!", "ACT NOW!", "DON'T MISS OUT!"],
            "hi": ["तत्काल!", "सीमित समय!", "अभी कार्य करें!", "चूकें नहीं!"],
            "ta": ["அவசரம்!", "வரம்புக்குட்பட்ட நேரம்!", "இப்போது செயல்படுங்கள்!", "தவறவிடாதீர்கள்!"],
            "kn": ["ತುರ್ತು!", "ಸೀಮಿತ ಸಮಯ!", "ಈಗ ಕಾರ್ಯನಿರ್ವಹಿಸಿ!", "ತಪ್ಪಿಸಿಕೊಳ್ಳಬೇಡಿ!"]
        }
        
        lang = claim.get("language", "en")
        if lang in urgency_phrases:
            for phrase in urgency_phrases[lang]:
                variation = claim.copy()
                variation["claim_text"] = f"{phrase} {claim['claim_text']}"
                variation["id"] = f"{claim['id']}_urgent_{len(variations)}"
                variations.append(variation)
        
        # Add payment method variations
        payment_methods = {
            "en": ["UPI", "Paytm", "PhonePe", "Google Pay", "Bank Transfer"],
            "hi": ["UPI", "Paytm", "PhonePe", "Google Pay", "बैंक ट्रांसफर"],
            "ta": ["UPI", "Paytm", "PhonePe", "Google Pay", "வங்கி பரிமாற்றம்"],
            "kn": ["UPI", "Paytm", "PhonePe", "Google Pay", "ಬ್ಯಾಂಕ್ ಟ್ರಾನ್ಸ್ಫರ್"]
        }
        
        if lang in payment_methods:
            for method in payment_methods[lang]:
                variation = claim.copy()
                variation["claim_text"] = claim["claim_text"].replace("UPI", method)
                variation["id"] = f"{claim['id']}_payment_{len(variations)}"
                variations.append(variation)
        
        # Add amount variations
        amounts = ["₹100", "₹500", "₹1000", "₹5000", "₹10000"]
        for amount in amounts:
            variation = claim.copy()
            variation["claim_text"] = re.sub(r'₹\d+', amount, claim["claim_text"])
            variation["id"] = f"{claim['id']}_amount_{len(variations)}"
            variations.append(variation)
        
        return variations
    
    def normalize_text(self, text: str, language: str = "en") -> str:
        """Normalize text for training"""
        # Basic cleaning
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)  # Remove extra whitespace
        
        # Language-specific normalization
        if language in ["hi", "ta", "kn"]:
            # Unicode normalization for Indic languages
            text = unicodedata.normalize('NFC', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\-]', '', text)
        
        return text
    
    def extract_features(self, claim: Dict[str, Any]) -> Dict[str, Any]:
        """Extract features from claim for training"""
        text = claim["claim_text"]
        language = claim.get("language", "en")
        
        features = {
            "text": self.normalize_text(text, language),
            "language": language,
            "length": len(text),
            "word_count": len(text.split()),
            "has_urgency": self._has_urgency_keywords(text, language),
            "has_payment": self._has_payment_keywords(text, language),
            "has_amount": bool(re.search(r'₹\d+', text)),
            "has_phone": bool(re.search(r'\d{10}', text)),
            "has_email": bool(re.search(r'@', text)),
            "has_url": bool(re.search(r'http', text)),
            "exclamation_count": text.count('!'),
            "caps_ratio": sum(1 for c in text if c.isupper()) / len(text) if text else 0,
            "scam_keyword_count": self._count_scam_keywords(text, language)
        }
        
        return features
    
    def _has_urgency_keywords(self, text: str, language: str) -> bool:
        """Check if text contains urgency keywords"""
        urgency_keywords = {
            "en": ["urgent", "immediate", "now", "quick", "fast", "hurry"],
            "hi": ["तत्काल", "तुरंत", "अभी", "जल्दी", "तेज", "हड़बड़ी"],
            "ta": ["அவசரம்", "உடனடி", "இப்போது", "விரைவு", "வேகம்", "அவசர"],
            "kn": ["ತುರ್ತು", "ತಕ್ಷಣ", "ಈಗ", "ವೇಗ", "ವೇಗವಾಗಿ", "ಅವಸರ"]
        }
        
        if language not in urgency_keywords:
            return False
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in urgency_keywords[language])
    
    def _has_payment_keywords(self, text: str, language: str) -> bool:
        """Check if text contains payment keywords"""
        payment_keywords = {
            "en": ["upi", "paytm", "phonepe", "google pay", "transfer", "send money"],
            "hi": ["upi", "paytm", "phonepe", "google pay", "ट्रांसफर", "पैसा भेजें"],
            "ta": ["upi", "paytm", "phonepe", "google pay", "பரிமாற்றம்", "பணம் அனுப்ப"],
            "kn": ["upi", "paytm", "phonepe", "google pay", "ವರ್ಗಾವಣೆ", "ಹಣ ಕಳುಹಿಸಿ"]
        }
        
        if language not in payment_keywords:
            return False
        
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in payment_keywords[language])
    
    def _count_scam_keywords(self, text: str, language: str) -> int:
        """Count scam keywords in text"""
        if language not in self.scam_keywords:
            return 0
        
        text_lower = text.lower()
        count = 0
        for keyword in self.scam_keywords[language]:
            count += text_lower.count(keyword.lower())
        
        return count
    
    def prepare_training_data(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Prepare training and validation data"""
        logger.info("Preparing training data...")
        
        # Load sample claims
        base_claims = self.load_sample_claims()
        
        # Create synthetic data
        all_claims = self.create_synthetic_data(base_claims)
        
        # Extract features
        training_data = []
        for claim in all_claims:
            features = self.extract_features(claim)
            features["label"] = claim.get("category", "unknown")
            features["original_id"] = claim.get("id", "")
            training_data.append(features)
        
        # Split into train and validation
        np.random.seed(42)
        np.random.shuffle(training_data)
        
        split_idx = int(0.8 * len(training_data))
        train_data = training_data[:split_idx]
        val_data = training_data[split_idx:]
        
        logger.info(f"Training data: {len(train_data)} samples")
        logger.info(f"Validation data: {len(val_data)} samples")
        
        return train_data, val_data
    
    def save_training_data(self, train_data: List[Dict[str, Any]], val_data: List[Dict[str, Any]]):
        """Save training data to files"""
        # Save as JSON
        train_file = self.output_dir / "train_data.json"
        val_file = self.output_dir / "val_data.json"
        
        with open(train_file, 'w', encoding='utf-8') as f:
            json.dump(train_data, f, indent=2, ensure_ascii=False)
        
        with open(val_file, 'w', encoding='utf-8') as f:
            json.dump(val_data, f, indent=2, ensure_ascii=False)
        
        # Save as CSV for easy inspection
        train_df = pd.DataFrame(train_data)
        val_df = pd.DataFrame(val_data)
        
        train_csv = self.output_dir / "train_data.csv"
        val_csv = self.output_dir / "val_data.csv"
        
        train_df.to_csv(train_csv, index=False)
        val_df.to_csv(val_csv, index=False)
        
        logger.info(f"Saved training data to {train_file} and {train_csv}")
        logger.info(f"Saved validation data to {val_file} and {val_csv}")
        
        # Print data statistics
        self._print_data_statistics(train_data, val_data)
    
    def _print_data_statistics(self, train_data: List[Dict[str, Any]], val_data: List[Dict[str, Any]]):
        """Print data statistics"""
        logger.info("Data Statistics:")
        
        # Label distribution
        train_labels = [item["label"] for item in train_data]
        val_labels = [item["label"] for item in val_data]
        
        from collections import Counter
        train_label_counts = Counter(train_labels)
        val_label_counts = Counter(val_labels)
        
        logger.info("Training set label distribution:")
        for label, count in train_label_counts.items():
            logger.info(f"  {label}: {count} ({count/len(train_data)*100:.1f}%)")
        
        logger.info("Validation set label distribution:")
        for label, count in val_label_counts.items():
            logger.info(f"  {label}: {count} ({count/len(val_data)*100:.1f}%)")
        
        # Language distribution
        train_langs = [item["language"] for item in train_data]
        val_langs = [item["language"] for item in val_data]
        
        train_lang_counts = Counter(train_langs)
        val_lang_counts = Counter(val_langs)
        
        logger.info("Training set language distribution:")
        for lang, count in train_lang_counts.items():
            logger.info(f"  {lang}: {count} ({count/len(train_data)*100:.1f}%)")
        
        logger.info("Validation set language distribution:")
        for lang, count in val_lang_counts.items():
            logger.info(f"  {lang}: {count} ({count/len(val_data)*100:.1f}%)")

def main():
    """Main function"""
    preparator = DataPreparator()
    
    # Prepare training data
    train_data, val_data = preparator.prepare_training_data()
    
    # Save training data
    preparator.save_training_data(train_data, val_data)
    
    logger.info("Data preparation completed!")

if __name__ == "__main__":
    main()
