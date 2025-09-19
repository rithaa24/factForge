"""
Model evaluation and metrics calculation
"""
import os
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
import logging
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    classification_report, confusion_matrix, accuracy_score,
    precision_recall_fscore_support, roc_auc_score, roc_curve
)
from sklearn.calibration import calibration_curve
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelEvaluator:
    """Evaluate trained classifier models"""
    
    def __init__(self, model_dir: str = "models/artifacts"):
        self.model_dir = Path(model_dir)
        self.output_dir = Path("models/evaluation")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Language mappings
        self.language_map = {
            "en": "English",
            "hi": "Hindi", 
            "ta": "Tamil",
            "kn": "Kannada"
        }
    
    def load_test_data(self, test_file: str) -> Tuple[List[str], List[str], List[str]]:
        """Load test data"""
        with open(test_file, 'r', encoding='utf-8') as f:
            test_data = json.load(f)
        
        texts = [item["text"] for item in test_data]
        labels = [item["label"] for item in test_data]
        languages = [item["language"] for item in test_data]
        
        logger.info(f"Loaded {len(test_data)} test samples")
        return texts, labels, languages
    
    def evaluate_model(self, y_true: List[str], y_pred: List[str], 
                      y_prob: List[float] = None, languages: List[str] = None) -> Dict[str, Any]:
        """Evaluate model performance"""
        results = {}
        
        # Overall metrics
        results["overall"] = self._calculate_metrics(y_true, y_pred, y_prob)
        
        # Per-language metrics
        if languages:
            results["by_language"] = self._calculate_per_language_metrics(
                y_true, y_pred, y_prob, languages
            )
        
        # Per-class metrics
        results["by_class"] = self._calculate_per_class_metrics(y_true, y_pred, y_prob)
        
        return results
    
    def _calculate_metrics(self, y_true: List[str], y_pred: List[str], 
                          y_prob: List[float] = None) -> Dict[str, Any]:
        """Calculate overall metrics"""
        metrics = {}
        
        # Basic metrics
        metrics["accuracy"] = accuracy_score(y_true, y_pred)
        
        # Precision, recall, F1
        precision, recall, f1, support = precision_recall_fscore_support(
            y_true, y_pred, average='weighted'
        )
        metrics["precision"] = precision
        metrics["recall"] = recall
        metrics["f1_score"] = f1
        
        # Per-class metrics
        precision_macro, recall_macro, f1_macro, _ = precision_recall_fscore_support(
            y_true, y_pred, average='macro'
        )
        metrics["precision_macro"] = precision_macro
        metrics["recall_macro"] = recall_macro
        metrics["f1_macro"] = f1_macro
        
        # ROC AUC (if probabilities available)
        if y_prob is not None:
            try:
                # Convert to binary for ROC AUC
                y_true_binary = [1 if label == "scam" else 0 for label in y_true]
                metrics["roc_auc"] = roc_auc_score(y_true_binary, y_prob)
            except Exception as e:
                logger.warning(f"Could not calculate ROC AUC: {e}")
                metrics["roc_auc"] = None
        
        return metrics
    
    def _calculate_per_language_metrics(self, y_true: List[str], y_pred: List[str], 
                                       y_prob: List[float], languages: List[str]) -> Dict[str, Any]:
        """Calculate metrics per language"""
        lang_metrics = {}
        
        unique_languages = list(set(languages))
        
        for lang in unique_languages:
            # Filter data for this language
            lang_indices = [i for i, l in enumerate(languages) if l == lang]
            lang_y_true = [y_true[i] for i in lang_indices]
            lang_y_pred = [y_pred[i] for i in lang_indices]
            lang_y_prob = [y_prob[i] for i in lang_indices] if y_prob else None
            
            # Calculate metrics
            lang_metrics[lang] = self._calculate_metrics(lang_y_true, lang_y_pred, lang_y_prob)
            lang_metrics[lang]["sample_count"] = len(lang_indices)
        
        return lang_metrics
    
    def _calculate_per_class_metrics(self, y_true: List[str], y_pred: List[str], 
                                   y_prob: List[float]) -> Dict[str, Any]:
        """Calculate metrics per class"""
        class_metrics = {}
        
        unique_classes = list(set(y_true))
        
        for class_name in unique_classes:
            # Convert to binary for this class
            y_true_binary = [1 if label == class_name else 0 for label in y_true]
            y_pred_binary = [1 if pred == class_name else 0 for pred in y_pred]
            y_prob_binary = [prob if pred == class_name else 1-prob for pred, prob in zip(y_pred, y_prob)] if y_prob else None
            
            # Calculate metrics
            precision, recall, f1, support = precision_recall_fscore_support(
                y_true_binary, y_pred_binary, average='binary'
            )
            
            class_metrics[class_name] = {
                "precision": precision,
                "recall": recall,
                "f1_score": f1,
                "support": support
            }
            
            # ROC AUC for this class
            if y_prob_binary is not None:
                try:
                    class_metrics[class_name]["roc_auc"] = roc_auc_score(y_true_binary, y_prob_binary)
                except Exception as e:
                    logger.warning(f"Could not calculate ROC AUC for {class_name}: {e}")
                    class_metrics[class_name]["roc_auc"] = None
        
        return class_metrics
    
    def create_confusion_matrix(self, y_true: List[str], y_pred: List[str], 
                               save_path: str = None) -> np.ndarray:
        """Create and save confusion matrix"""
        cm = confusion_matrix(y_true, y_pred)
        
        if save_path:
            plt.figure(figsize=(10, 8))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
            plt.title('Confusion Matrix')
            plt.xlabel('Predicted')
            plt.ylabel('Actual')
            plt.tight_layout()
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
        
        return cm
    
    def create_roc_curve(self, y_true: List[str], y_prob: List[float], 
                        save_path: str = None) -> Dict[str, Any]:
        """Create and save ROC curve"""
        if y_prob is None:
            logger.warning("No probabilities provided for ROC curve")
            return {}
        
        # Convert to binary
        y_true_binary = [1 if label == "scam" else 0 for label in y_true]
        
        fpr, tpr, thresholds = roc_curve(y_true_binary, y_prob)
        roc_auc = roc_auc_score(y_true_binary, y_prob)
        
        if save_path:
            plt.figure(figsize=(8, 6))
            plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {roc_auc:.2f})')
            plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
            plt.xlim([0.0, 1.0])
            plt.ylim([0.0, 1.05])
            plt.xlabel('False Positive Rate')
            plt.ylabel('True Positive Rate')
            plt.title('Receiver Operating Characteristic (ROC) Curve')
            plt.legend(loc="lower right")
            plt.tight_layout()
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
        
        return {
            "fpr": fpr.tolist(),
            "tpr": tpr.tolist(),
            "thresholds": thresholds.tolist(),
            "auc": roc_auc
        }
    
    def create_calibration_curve(self, y_true: List[str], y_prob: List[float], 
                               save_path: str = None) -> Dict[str, Any]:
        """Create and save calibration curve"""
        if y_prob is None:
            logger.warning("No probabilities provided for calibration curve")
            return {}
        
        # Convert to binary
        y_true_binary = [1 if label == "scam" else 0 for label in y_true]
        
        fraction_of_positives, mean_predicted_value = calibration_curve(
            y_true_binary, y_prob, n_bins=10
        )
        
        if save_path:
            plt.figure(figsize=(8, 6))
            plt.plot(mean_predicted_value, fraction_of_positives, "s-", label="Model")
            plt.plot([0, 1], [0, 1], "k:", label="Perfectly calibrated")
            plt.xlabel('Mean Predicted Probability')
            plt.ylabel('Fraction of Positives')
            plt.title('Calibration Curve')
            plt.legend()
            plt.tight_layout()
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
        
        return {
            "fraction_of_positives": fraction_of_positives.tolist(),
            "mean_predicted_value": mean_predicted_value.tolist()
        }
    
    def create_language_comparison_plot(self, results: Dict[str, Any], 
                                      save_path: str = None) -> None:
        """Create language comparison plot"""
        if "by_language" not in results:
            logger.warning("No per-language results available")
            return
        
        lang_data = results["by_language"]
        
        # Prepare data for plotting
        languages = list(lang_data.keys())
        metrics = ["precision", "recall", "f1_score"]
        
        data = []
        for lang in languages:
            for metric in metrics:
                data.append({
                    "Language": self.language_map.get(lang, lang),
                    "Metric": metric.replace("_", " ").title(),
                    "Value": lang_data[lang][metric],
                    "Sample Count": lang_data[lang]["sample_count"]
                })
        
        df = pd.DataFrame(data)
        
        if save_path:
            fig = px.bar(df, x="Language", y="Value", color="Metric", 
                        title="Model Performance by Language",
                        barmode="group")
            fig.update_layout(height=600, width=800)
            fig.write_html(save_path)
    
    def create_class_comparison_plot(self, results: Dict[str, Any], 
                                   save_path: str = None) -> None:
        """Create class comparison plot"""
        if "by_class" not in results:
            logger.warning("No per-class results available")
            return
        
        class_data = results["by_class"]
        
        # Prepare data for plotting
        classes = list(class_data.keys())
        metrics = ["precision", "recall", "f1_score"]
        
        data = []
        for class_name in classes:
            for metric in metrics:
                data.append({
                    "Class": class_name.title(),
                    "Metric": metric.replace("_", " ").title(),
                    "Value": class_data[class_name][metric],
                    "Support": class_data[class_name]["support"]
                })
        
        df = pd.DataFrame(data)
        
        if save_path:
            fig = px.bar(df, x="Class", y="Value", color="Metric", 
                        title="Model Performance by Class",
                        barmode="group")
            fig.update_layout(height=600, width=800)
            fig.write_html(save_path)
    
    def generate_report(self, results: Dict[str, Any], save_path: str = None) -> str:
        """Generate comprehensive evaluation report"""
        report = []
        report.append("# Model Evaluation Report")
        report.append("=" * 50)
        report.append("")
        
        # Overall metrics
        if "overall" in results:
            overall = results["overall"]
            report.append("## Overall Performance")
            report.append("")
            report.append(f"- **Accuracy**: {overall['accuracy']:.4f}")
            report.append(f"- **Precision (Weighted)**: {overall['precision']:.4f}")
            report.append(f"- **Recall (Weighted)**: {overall['recall']:.4f}")
            report.append(f"- **F1-Score (Weighted)**: {overall['f1_score']:.4f}")
            report.append(f"- **Precision (Macro)**: {overall['precision_macro']:.4f}")
            report.append(f"- **Recall (Macro)**: {overall['recall_macro']:.4f}")
            report.append(f"- **F1-Score (Macro)**: {overall['f1_macro']:.4f}")
            if overall.get('roc_auc'):
                report.append(f"- **ROC AUC**: {overall['roc_auc']:.4f}")
            report.append("")
        
        # Per-language metrics
        if "by_language" in results:
            report.append("## Performance by Language")
            report.append("")
            for lang, metrics in results["by_language"].items():
                lang_name = self.language_map.get(lang, lang)
                report.append(f"### {lang_name} ({lang})")
                report.append(f"- **Samples**: {metrics['sample_count']}")
                report.append(f"- **Precision**: {metrics['precision']:.4f}")
                report.append(f"- **Recall**: {metrics['recall']:.4f}")
                report.append(f"- **F1-Score**: {metrics['f1_score']:.4f}")
                if metrics.get('roc_auc'):
                    report.append(f"- **ROC AUC**: {metrics['roc_auc']:.4f}")
                report.append("")
        
        # Per-class metrics
        if "by_class" in results:
            report.append("## Performance by Class")
            report.append("")
            for class_name, metrics in results["by_class"].items():
                report.append(f"### {class_name.title()}")
                report.append(f"- **Support**: {metrics['support']}")
                report.append(f"- **Precision**: {metrics['precision']:.4f}")
                report.append(f"- **Recall**: {metrics['recall']:.4f}")
                report.append(f"- **F1-Score**: {metrics['f1_score']:.4f}")
                if metrics.get('roc_auc'):
                    report.append(f"- **ROC AUC**: {metrics['roc_auc']:.4f}")
                report.append("")
        
        # Recommendations
        report.append("## Recommendations")
        report.append("")
        
        if "by_language" in results:
            lang_f1_scores = {lang: metrics['f1_score'] for lang, metrics in results["by_language"].items()}
            worst_lang = min(lang_f1_scores, key=lang_f1_scores.get)
            best_lang = max(lang_f1_scores, key=lang_f1_scores.get)
            
            report.append(f"- **Best performing language**: {self.language_map.get(best_lang, best_lang)} (F1: {lang_f1_scores[best_lang]:.4f})")
            report.append(f"- **Worst performing language**: {self.language_map.get(worst_lang, worst_lang)} (F1: {lang_f1_scores[worst_lang]:.4f})")
            report.append("")
        
        if "by_class" in results:
            class_f1_scores = {class_name: metrics['f1_score'] for class_name, metrics in results["by_class"].items()}
            worst_class = min(class_f1_scores, key=class_f1_scores.get)
            best_class = max(class_f1_scores, key=class_f1_scores.get)
            
            report.append(f"- **Best performing class**: {best_class.title()} (F1: {class_f1_scores[best_class]:.4f})")
            report.append(f"- **Worst performing class**: {worst_class.title()} (F1: {class_f1_scores[worst_class]:.4f})")
            report.append("")
        
        report_text = "\n".join(report)
        
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(report_text)
        
        return report_text
    
    def evaluate_model_from_files(self, test_file: str, pred_file: str, 
                                 prob_file: str = None) -> Dict[str, Any]:
        """Evaluate model from prediction files"""
        # Load test data
        texts, labels, languages = self.load_test_data(test_file)
        
        # Load predictions
        with open(pred_file, 'r', encoding='utf-8') as f:
            predictions = json.load(f)
        
        # Load probabilities (if available)
        probabilities = None
        if prob_file and os.path.exists(prob_file):
            with open(prob_file, 'r', encoding='utf-8') as f:
                probabilities = json.load(f)
        
        # Evaluate
        results = self.evaluate_model(labels, predictions, probabilities, languages)
        
        # Create visualizations
        self.create_confusion_matrix(labels, predictions, 
                                   str(self.output_dir / "confusion_matrix.png"))
        
        if probabilities:
            self.create_roc_curve(labels, probabilities, 
                                str(self.output_dir / "roc_curve.png"))
            self.create_calibration_curve(labels, probabilities, 
                                        str(self.output_dir / "calibration_curve.png"))
        
        # Create comparison plots
        self.create_language_comparison_plot(results, 
                                           str(self.output_dir / "language_comparison.html"))
        self.create_class_comparison_plot(results, 
                                        str(self.output_dir / "class_comparison.html"))
        
        # Generate report
        report = self.generate_report(results, str(self.output_dir / "evaluation_report.md"))
        
        # Save results
        with open(self.output_dir / "evaluation_results.json", 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Evaluation completed. Results saved to {self.output_dir}")
        logger.info(f"Report saved to {self.output_dir / 'evaluation_report.md'}")
        
        return results

def main():
    """Main function"""
    evaluator = ModelEvaluator()
    
    # Example usage - replace with actual file paths
    test_file = "models/data/val_data.json"
    pred_file = "models/predictions.json"
    prob_file = "models/probabilities.json"
    
    if os.path.exists(test_file):
        results = evaluator.evaluate_model_from_files(test_file, pred_file, prob_file)
        print("Evaluation completed successfully!")
    else:
        print(f"Test file not found: {test_file}")
        print("Please run data preparation first.")

if __name__ == "__main__":
    main()
