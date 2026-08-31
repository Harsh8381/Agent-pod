master_insights_list = [
    "None",
    "Diabetes (Type 2)",
    "Hypertension",
    "Hyperlipidemia",
    "Asthma",
    "Osteoarthritis",
    "Obesity",
    "Smoking History",
    "Alcohol Use",
    "Anxiety",
    "Depression",
    "Fever",
    "Chronic Cough",
    "Fatigue",
    "Headache",
    "Chest Pain",
    "Nausea",
    "Color Blindness"
]


def get_detected_insights(transcript_text):

    transcript_lower = transcript_text.lower()

    detected = set()

    keyword_map = {
        "diabetes": "Diabetes (Type 2)",
        "hypertension": "Hypertension",
        "high bp": "Hypertension",
        "cholesterol": "Hyperlipidemia",
        "asthma": "Asthma",
        "arthritis": "Osteoarthritis",
        "obesity": "Obesity",
        "smok": "Smoking History",
        "alcohol": "Alcohol Use",
        "anxiety": "Anxiety",
        "depression": "Depression",
        "fever": "Fever",
        "cough": "Chronic Cough",
        "fatigue": "Fatigue",
        "headache": "Headache",
        "chest pain": "Chest Pain",
        "nausea": "Nausea",
        "color blind": "Color Blindness"
    }

    for keyword, condition in keyword_map.items():

        if keyword in transcript_lower:
            detected.add(condition)

    return list(detected)