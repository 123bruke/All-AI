import re

MEDICAL_KEYWORDS = {
    "fever","pain","cough","headache","nausea","diabetes","cancer","infection",
    "rash","bleeding","injury","fracture","anxiety","depression","migraine",
    "pregnancy","pregnant","dose","medication","vaccine","allergy","surgery",
    "tumor","tumour","bp","blood pressure","heart","cardiac","stroke","asthma",
    "shortness of breath","dyspnea","chest pain","abdominal","stomach","diarrhea",
    "constipation","vomiting","MRI","x-ray","ultrasound","scan","xray"
}

RECOMMENDATION_DB = {
    "fever": {
        "rec": "Monitor temperature, stay hydrated, consider paracetamol if over 38°C. Seek care if severe.",
        "youtube": "https://www.youtube.com/watch?v=example_fever",
        "website": "https://www.who.int/news-room/fact-sheets/detail/fever"
    },
    "headache": {
        "rec": "Rest, avoid triggers, consider OTC analgesics. See doctor if severe.",
        "youtube": "https://www.youtube.com/watch?v=example_headache",
        "website": "https://www.webmd.com/migraines-headaches/default.htm"
    }
}

def appears_medical_text_simple(text):
    txt = text.lower()
    for kw in MEDICAL_KEYWORDS:
        if kw in txt:
            return True
    return False

def choose_recommendation(text):
    txt = text.lower()
    for key in RECOMMENDATION_DB:
        if key in txt:
            return RECOMMENDATION_DB[key]
    return {
        "rec": "Basic first-line measures suggested (rest, hydration). Seek local care if worsening.",
        "youtube": "https://www.youtube.com/results?search_query=first+aid",
        "website": "https://www.who.int"
    }
