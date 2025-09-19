"""
Train classifier for scam detection
"""
import os
import json
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    DataCollatorWithPadding
)
from datasets import Dataset
import torch
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScamClassifierTrainer:
    """Trainer for scam detection classifier"""
    
    def __init__(self, model_name: str = "xlm-roberta-base"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.training_args = None
        
    def load_data(self, data_path: str) -> Tuple[List[str], List[int]]:
        """Load training data"""
        logger.info(f"Loading data from {data_path}")
        
        # Load sample data (in production, load from actual dataset)
        texts = []
        labels = []
        
        # Sample scam texts
        scam_texts = [
            "Send ₹1000 to UPI abc@upi to claim your lottery prize of ₹50,000! Limited time offer.",
            "Urgent: Your account will be closed. Send money immediately to avoid penalty.",
            "Congratulations! You won ₹1,00,000. Click here to claim your prize now!",
            "Act now! Limited time offer. Send ₹500 to get ₹50,000 instantly.",
            "Your bank account is suspended. Send verification fee to restore access.",
            "तत्काल ₹1000 UPI abc@upi पर भेजें और ₹50,000 का लॉटरी पुरस्कार जीतें!",
            "अवसर खोना मत! सीमित समय का प्रस्ताव। अभी पैसे भेजें।",
            "₹1000 ஐ UPI abc@upi க்கு உடனடியாக அனுப்பி ₹50,000 லாட்டரி பரிசை வெல்லுங்கள்!",
            "ತಕ್ಷಣ ₹1000 ಅನ್ನು UPI abc@upi ಗೆ ಕಳುಹಿಸಿ ₹50,000 ಲಾಟರಿ ಬಹುಮಾನವನ್ನು ಗೆಲ್ಲಿ!"
        ]
        
        # Sample legitimate texts
        legitimate_texts = [
            "The Earth is round and orbits around the Sun.",
            "Water boils at 100 degrees Celsius at sea level.",
            "COVID-19 vaccines are safe and effective.",
            "Regular exercise is important for good health.",
            "The capital of India is New Delhi.",
            "पृथ्वी गोल है और सूर्य के चारों ओर घूमती है।",
            "जल समुद्र तल पर 100 डिग्री सेल्सियस पर उबलता है।",
            "பூமி உருண்டையானது மற்றும் சூரியனைச் சுற்றி வருகிறது.",
            "ಭೂಮಿ ಗೋಳಾಕಾರದಲ್ಲಿದೆ ಮತ್ತು ಸೂರ್ಯನ ಸುತ್ತ ಸುತ್ತುತ್ತದೆ."
        ]
        
        # Combine and label data
        texts.extend(scam_texts)
        labels.extend([1] * len(scam_texts))  # 1 for scam
        
        texts.extend(legitimate_texts)
        labels.extend([0] * len(legitimate_texts))  # 0 for legitimate
        
        logger.info(f"Loaded {len(texts)} samples")
        return texts, labels
    
    def prepare_dataset(self, texts: List[str], labels: List[int]) -> Dataset:
        """Prepare dataset for training"""
        logger.info("Preparing dataset...")
        
        # Tokenize texts
        tokenized = self.tokenizer(
            texts,
            truncation=True,
            padding=True,
            max_length=512,
            return_tensors="pt"
        )
        
        # Create dataset
        dataset = Dataset.from_dict({
            "input_ids": tokenized["input_ids"],
            "attention_mask": tokenized["attention_mask"],
            "labels": labels
        })
        
        return dataset
    
    def compute_metrics(self, eval_pred):
        """Compute evaluation metrics"""
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        
        # Calculate accuracy
        accuracy = (predictions == labels).astype(np.float32).mean().item()
        
        return {"accuracy": accuracy}
    
    def train(self, data_path: str, output_dir: str = "models/classifier"):
        """Train the classifier"""
        logger.info("Starting training...")
        
        # Load data
        texts, labels = self.load_data(data_path)
        
        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name,
            num_labels=2,
            problem_type="single_label_classification"
        )
        
        # Prepare dataset
        dataset = self.prepare_dataset(texts, labels)
        
        # Split dataset
        train_dataset, eval_dataset = train_test_split(
            dataset, 
            test_size=0.2, 
            random_state=42
        )
        
        # Training arguments
        self.training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=3,
            per_device_train_batch_size=8,
            per_device_eval_batch_size=8,
            warmup_steps=100,
            weight_decay=0.01,
            logging_dir=f"{output_dir}/logs",
            logging_steps=10,
            evaluation_strategy="steps",
            eval_steps=50,
            save_strategy="steps",
            save_steps=100,
            load_best_model_at_end=True,
            metric_for_best_model="accuracy",
            greater_is_better=True,
        )
        
        # Data collator
        data_collator = DataCollatorWithPadding(tokenizer=self.tokenizer)
        
        # Create trainer
        trainer = Trainer(
            model=self.model,
            args=self.training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            tokenizer=self.tokenizer,
            data_collator=data_collator,
            compute_metrics=self.compute_metrics,
        )
        
        # Train model
        logger.info("Training model...")
        trainer.train()
        
        # Save model
        logger.info(f"Saving model to {output_dir}")
        trainer.save_model()
        self.tokenizer.save_pretrained(output_dir)
        
        # Evaluate model
        logger.info("Evaluating model...")
        eval_results = trainer.evaluate()
        logger.info(f"Evaluation results: {eval_results}")
        
        # Save model metadata
        metadata = {
            "model_name": self.model_name,
            "num_labels": 2,
            "labels": ["legitimate", "scam"],
            "languages": ["en", "hi", "ta", "kn"],
            "thresholds": {
                "en": 0.92,
                "hi": 0.90,
                "ta": 0.90,
                "kn": 0.90
            },
            "evaluation_results": eval_results,
            "training_samples": len(texts)
        }
        
        with open(f"{output_dir}/model_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
        
        logger.info("Training completed successfully!")
        return eval_results

def main():
    """Main training function"""
    trainer = ScamClassifierTrainer()
    
    # Create output directory
    os.makedirs("models/classifier", exist_ok=True)
    
    # Train model
    results = trainer.train("data/demo/sample_claims.json", "models/classifier")
    
    print("🎉 Training completed!")
    print(f"📊 Final accuracy: {results['eval_accuracy']:.4f}")

if __name__ == "__main__":
    main()
