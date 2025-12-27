
import pickle
import os

MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'time_series_models'))
model_filename = "Cabai_Rawit_Hijau.pkl"
model_path = os.path.join(MODEL_DIR, model_filename)

if os.path.exists(model_path):
    with open(model_path, 'rb') as f:
        loaded_object = pickle.load(f)
    print(f"Model object for {model_filename}:")
    print(loaded_object)
else:
    print(f"Model file not found: {model_path}")