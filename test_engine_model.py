import joblib
import pandas as pd

# Load model
model = joblib.load("model/random_forest_model.pkl")

# Test cases
test_cases = [

    {
        "name": "Normal Engine",
        "engine_rpm": 700,
        "lub_oil_pressure": 2.5,
        "fuel_pressure": 11.8,
        "coolant_pressure": 3.2,
        "lub_oil_temp": 80,
        "coolant_temp": 82,
        "pressure_ratio": 0.78,
        "temp_diff": -2
    },

    {
        "name": "High RPM",
        "engine_rpm": 1500,
        "lub_oil_pressure": 2.5,
        "fuel_pressure": 11.8,
        "coolant_pressure": 3.2,
        "lub_oil_temp": 80,
        "coolant_temp": 82,
        "pressure_ratio": 0.78,
        "temp_diff": -2
    },

    {
        "name": "High Temperature",
        "engine_rpm": 700,
        "lub_oil_pressure": 2.5,
        "fuel_pressure": 11.8,
        "coolant_pressure": 3.2,
        "lub_oil_temp": 120,
        "coolant_temp": 115,
        "pressure_ratio": 0.78,
        "temp_diff": 5
    },

    {
        "name": "Low Oil Pressure",
        "engine_rpm": 700,
        "lub_oil_pressure": 0.5,
        "fuel_pressure": 11.8,
        "coolant_pressure": 3.2,
        "lub_oil_temp": 80,
        "coolant_temp": 82,
        "pressure_ratio": 0.78,
        "temp_diff": -2
    }
]


for test in test_cases:

    name = test.pop("name")

    X = pd.DataFrame([test])

    prediction = model.predict(X)[0]
    probabilities = model.predict_proba(X)[0]

    print("=" * 50)
    print(name)
    print("Prediction:", prediction)
    print("Class 0 probability:", round(probabilities[0], 4))
    print("Class 1 probability:", round(probabilities[1], 4))
    print("Confidence:", round(max(probabilities), 4))