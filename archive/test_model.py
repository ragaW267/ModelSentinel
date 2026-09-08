import joblib
import numpy as np

MODEL_PATH = "model/random_forest_model.pkl"

print("Loading model...")

model = joblib.load(MODEL_PATH)

print("\nModel loaded successfully!")
print("Model type:", type(model))

# Check model information
if hasattr(model, "n_features_in_"):
    print("Expected number of features:", model.n_features_in_)

if hasattr(model, "feature_names_in_"):
    print("Expected feature names:")
    print(model.feature_names_in_)

if hasattr(model, "classes_"):
    print("Classes:", model.classes_)

# Test input: 8 engine features
sample = np.array([[
    700,
    2.5,
    11.8,
    3.2,
    80,
    82,
    0.78,
    -2
]])

print("\nTesting prediction...")

prediction = model.predict(sample)

print("Prediction:", prediction)

if hasattr(model, "predict_proba"):
    probability = model.predict_proba(sample)
    print("Probability:", probability)

print("\nTEST COMPLETE")