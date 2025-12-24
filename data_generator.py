import pymongo
import random
from datetime import datetime, timedelta
import pandas as pd
import certifi  

MONGO_URI = "mongodb+srv://yangqikai04:DBProject@database.rpt54sl.mongodb.net/"

print("Connecting to database...")

try:
    client = pymongo.MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    client.admin.command('ping')
    print("Successful connection.")
except Exception as e:
    print(f"Connection failed: {e}")
    exit()

db = client["eda_project"]

try:
    db.DimCustomer.delete_many({})
    db.FactClaimChronic.delete_many({})
    db.ClinicalNote.delete_many({})
    print("Old data cleaned.")
except Exception as e:
    print(f"Error when cleaning: {e}")

high_risk_notes = [
    "Patient diagnosed with type 2 diabetes, blood sugar uncontrolled. HbA1c at 8.5%.",
    "Severe hypertension detected. Patient complains of chest pain and shortness of breath.",
    "History of chronic heart failure. Edema present in lower extremities.",
    "Patient suffering from chronic kidney disease stage 3. Dialysis considered.",
    "Recurrent asthma attacks requiring hospitalization. Inhaler usage increased.",
    "Hyperlipidemia and high cholesterol levels observed. Statins prescribed.",
    "Patient reports severe joint pain, diagnosed with rheumatoid arthritis.",
    "Coronary artery disease confirmed via angiogram. Stent placement recommended.",
]

low_risk_notes = [
    "Patient came in for annual physical. No significant findings. Vitals stable.",
    "Routine checkup. Blood pressure and vitals are within normal range.",
    "Patient complains of mild seasonal allergies. Prescribed antihistamines.",
    "Minor ankle sprain from playing soccer. Rest and ice recommended.",
    "Skin rash on arm, likely contact dermatitis. Prescribed topical ointment.",
    "Flu shot administered. Patient is in good general health.",
    "Dental checkup required. No systemic health issues reported.",
    "Vision test performed. Prescription updated. Otherwise healthy.",
]

customers = []
claims = []
notes = []

print("Start generating data.")

for i in range(1, 501):
    customer_id = i
    
    is_chronic = random.random() < 0.3
    
    if is_chronic:
        age = random.randint(45, 85)
        note_text = random.choice(high_risk_notes)
        gender = random.randint(0, 1)
        claim_count = random.randint(2, 6)
        living_std = random.randint(1, 6)
    else:
        age = random.randint(20, 50)
        note_text = random.choice(low_risk_notes)
        gender = random.randint(0, 1)
        claim_count = 0 if random.random() < 0.7 else 1
        living_std = random.randint(5, 10)

    dob = datetime.now() - timedelta(days=age*365)
    age_band = f"{((age // 10) * 10)}-{((age // 10) * 10) + 9}"

    customer = {
        "CustomerID": customer_id,
        "CustomerNumber": f"CUST-{customer_id:05d}",
        "FullName": f"Customer_{customer_id}",
        "DateOfBirth": dob,
        "Age": age,
        "AgeBand": age_band,
        "Gender": gender,
        "Country": "USA",
        "Region": random.choice(["North", "South", "East", "West"]),
        "City": "New York",
        "PostalCode": f"100{random.randint(10, 99)}",
        "LivingStandardIndex": living_std,
        "CreatedTimestamp": datetime.now(),
        "UpdatedTimestamp": datetime.now()
    }
    customers.append(customer)
    
    note = {
        "NoteID": i,
        "ClaimID": i * 100 + 1,
        "CustomerID": customer_id,
        "NoteSource": random.choice(["Physician", "Nurse", "Adjuster"]),
        "NoteText": note_text,
        "CreatedTimestamp": datetime.now()
    }
    notes.append(note)

    if claim_count > 0:
        for j in range(claim_count):
            this_claim_id = i * 100 + (j + 1)
            claim_date = datetime.now() - timedelta(days=random.randint(1, 730))
            
            claim = {
                "ClaimID": this_claim_id,
                "ClaimNumber": f"CLM-{this_claim_id}",
                "PolicyID": random.randint(10000, 99999),
                "CustomerID": customer_id,
                "ProductID": random.randint(1, 50),
                "ClaimDate": claim_date,
                "ClaimStatus": random.choice(["Paid", "Pending", "Closed"]),
                "DiseaseType": "Chronic" if is_chronic else "Acute",
                "IsChronicFlag": "Y" if is_chronic else "N",
                "ReadmissionFlag": "Y" if (is_chronic and random.random() < 0.2) else "N",
                "PaidAmount": round(random.uniform(500, 10000), 2),
                "DeniedAmount": 0.0,
                "ReservedAmount": 0.0,
                "ServiceProviderID": random.randint(1, 100),
                "RiskScore": None,
                "CreatedTimestamp": datetime.now(),
                "UpdatedTimestamp": datetime.now()
            }
            claims.append(claim)

if customers:
    db.DimCustomer.insert_many(customers)
if notes:
    db.ClinicalNote.insert_many(notes)
if claims:
    db.FactClaimChronic.insert_many(claims)

print(f"Finish:")
print(f"- DimCustomer: {len(customers)}")
print(f"- ClinicalNote: {len(notes)}")
print(f"- FactClaimChronic: {len(claims)}")