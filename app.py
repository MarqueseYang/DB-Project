from flask import Flask, request, jsonify
from mongoengine import connect, Document, StringField, IntField, FloatField, DateTimeField
from engine import ChronicDiseasePredictor
import datetime
import threading
import certifi 

app = Flask(__name__)

MONGO_URI = "mongodb+srv://yangqikai04:DBProject@database.rpt54sl.mongodb.net/eda_project"
connect(host=MONGO_URI, tlsCAFile=certifi.where())

predictor = ChronicDiseasePredictor()


class FactClaimChronic(Document):
    meta = {'collection': 'FactClaimChronic'}
    ClaimID = IntField(required=True, unique=True)
    ClaimNumber = StringField() 
    CustomerID = IntField(required=True)
    PolicyID = IntField()
    ProductID = IntField()
    ClaimDate = DateTimeField(default=datetime.datetime.now)
    ClaimStatus = StringField(default="Pending")
    DiseaseType = StringField() 
    IsChronicFlag = StringField() 
    RiskScore = IntField() 
    
class ClinicalNote(Document):
    meta = {'collection': 'ClinicalNote'}
    NoteID = IntField(required=True, unique=True)
    ClaimID = IntField()
    CustomerID = IntField()
    NoteSource = StringField(default="WebSubmission") 
    NoteText = StringField()
    CreatedTimestamp = DateTimeField(default=datetime.datetime.now)


@app.route('/submit_claim', methods=['POST'])
def submit_claim():
    data = request.json
    
    note_text = data.get('note_text', '')
    age = data.get('age', 30)
    gender = data.get('gender', 0)
    history_count = data.get('history_count', 0)
    
    try:
        risk_prediction = predictor.predict(note_text, age, gender, history_count)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    import random
    new_claim_id = random.randint(100000, 999999) 
    
    ClinicalNote(
        NoteID=random.randint(100000, 999999),
        ClaimID=new_claim_id,
        CustomerID=data.get('customer_id', 999),
        NoteSource="Adjuster_Web_App",
        NoteText=note_text
    ).save()
    
    FactClaimChronic(
        ClaimID=new_claim_id,
        ClaimNumber=f"CLM-{new_claim_id}",
        CustomerID=data.get('customer_id', 999),
        PolicyID=data.get('policy_id', 8888),
        ProductID=data.get('product_id', 1),
        DiseaseType="Unknown", 
        IsChronicFlag="Y" if risk_prediction == 1 else "N", 
        RiskScore=risk_prediction 
    ).save()
    
    return jsonify({
        "status": "success",
        "claim_id": new_claim_id,
        "predicted_risk": risk_prediction,
        "message": "Claim processed and saved to Operational Data Store."
    })

@app.route('/retrain', methods=['POST'])
def trigger_retrain():
    def run_retrain():
        predictor.retrain(MONGO_URI)
    
    thread = threading.Thread(target=run_retrain)
    thread.start()
    return jsonify({'message': 'Retraining started.'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)