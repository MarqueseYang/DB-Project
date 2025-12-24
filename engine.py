import pandas as pd
import numpy as np
import joblib
import certifi 
from sentence_transformers import SentenceTransformer
from xgboost import XGBClassifier
from pymongo import MongoClient
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split 

class ChronicDiseasePredictor:
    def __init__(self, model_path='chronic_model.pkl'):
        self.model_path = model_path
        self.bert = SentenceTransformer("all-MiniLM-L6-v2")
        self.is_trained = False 

        try:
            self.clf = joblib.load(self.model_path)
            self.is_trained = True
            print(f"Success: {self.model_path}")
        except:
            print("Model not found. Retraining first.")
            self.clf = XGBClassifier(n_estimators=200, max_depth=6)

    def preprocess(self, note_text, age, gender, chronic_count):
        embedding = self.bert.encode(note_text)
        features = np.array([age, gender, chronic_count])
        final_vector = np.hstack([features, embedding])
        return final_vector.reshape(1, -1)

    def predict(self, note_text, age, gender, chronic_count):
        if not self.is_trained:
            print("Error")
            return -1 
            
        vector = self.preprocess(note_text, age, gender, chronic_count)
        prediction = self.clf.predict(vector)
        return int(prediction[0])

    def retrain(self, db_connection_string):
        print("Retraining...")
        
        client = MongoClient(db_connection_string, tlsCAFile=certifi.where())
        db = client["eda_project"]

        df_claim = pd.DataFrame(list(db.FactClaimChronic.find()))
        df_customer = pd.DataFrame(list(db.DimCustomer.find()))
        df_notes = pd.DataFrame(list(db.ClinicalNote.find()))
        
        if df_claim.empty or df_customer.empty:
            print("Skip retraining...")
            return

        df = df_customer.merge(df_notes[["CustomerID", "NoteText"]], on="CustomerID", how="left")
        df["NoteText"] = df["NoteText"].fillna("")

        chronic_claims = df_claim[df_claim["DiseaseType"] == "Chronic"]

        chronic_counts = chronic_claims.groupby("CustomerID").size().reset_index(name="ChronicCount")
        
        df = df.merge(chronic_counts, on="CustomerID", how="left")
        df["ChronicCount"] = df["ChronicCount"].fillna(0) 

        print("Generating context...")
        emb = self.bert.encode(df["NoteText"].tolist())

        X_struct = df[["Age", "Gender", "ChronicCount"]].fillna(0).to_numpy()
        X = np.hstack([X_struct, emb])

        y = df["ChronicCount"].apply(lambda x: 1 if x > 0 else 0)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        print("Training XGBoost...")
        self.clf.fit(X_train, y_train)
        self.is_trained = True 

        pred = self.clf.predict(X_test)
        print("Reporting:")
        print(classification_report(y_test, pred))
        
        joblib.dump(self.clf, self.model_path)
        print(f"Model updated at {self.model_path}")