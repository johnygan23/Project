import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

class AmbiguityDetector:
    def __init__(self, model_path):
        print(f"📥 Loading Detection Model from: {model_path}...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
            self.model.to(self.device)
            print("✅ Detection Model Loaded Successfully.")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise e

    def predict(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=128).to(self.device)
        
        with torch.no_grad():
            logits = self.model(**inputs).logits
            probabilities = torch.softmax(logits, dim=1)
            prediction = torch.argmax(probabilities, dim=1).item()
            score = probabilities[0][prediction].item()
            
        # Mapping: 0 = Clean, 1 = Ambiguous (Check your specific training mapping)
        label = "Ambiguous" if prediction == 1 else "Clear"
        return label, score