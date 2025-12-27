import pickle
import os

MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'time_series_models'))
MODEL_NAME = 'Cabai_Rawit.pkl'
MODEL_PATH = os.path.join(MODEL_DIR, MODEL_NAME)

if not os.path.exists(MODEL_PATH):
    print(f"Model file not found at: {MODEL_PATH}")
else:
    try:
        with open(MODEL_PATH, 'rb') as f:
            model_obj = pickle.load(f)
        
        print(f"Successfully loaded {MODEL_NAME}")
        print("="*30)
        print("Top-level keys:", model_obj.keys())
        print("="*30)

        if model_obj.get('model_type') == 'Ensemble':
            print("Ensemble model detected.")
            for sub_model_name in ['sarima', 'holt_winters', 'prophet']:
                if sub_model_name in model_obj:
                    print(f"\n--- Sub-model: {sub_model_name} ---")
                    sub_model_info = model_obj[sub_model_name]
                    print(f"Keys: {sub_model_info.keys()}")
                    if 'history' in sub_model_info:
                        history_df = sub_model_info['history']
                        print(f"'history' key found. Is it empty? {history_df.empty}")
                        if not history_df.empty:
                            print("History DataFrame head:")
                            print(history_df.head())
                    else:
                        print("'history' key NOT found.")
    except Exception as e:
        print(f"An error occurred: {e}")