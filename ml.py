import numpy as np
import pandas as pd
import pickle
from sklearn.linear_model import LinearRegression
from pathlib import Path


def load_data():
    """Load and preprocess data from CSV file"""
    csv_path = Path("data/adresowo_wroclaw_all.csv")
    
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found at {csv_path}")
    
    # Load the CSV data
    df = pd.read_csv(csv_path)
    
    # Clean the data - remove rows with missing values in key columns
    df_clean = df.dropna(subset=['rooms', 'area_m2', 'price_total_zl'])
    
    # Convert price from string to numeric (remove spaces and convert)
    # Handle different price formats: "800 000", "800000", etc.
    df_clean['price_total_zl'] = df_clean['price_total_zl'].astype(str).str.replace(' ', '').str.replace(',', '')
    
    # Convert to numeric, handling any remaining non-numeric values
    df_clean['price_total_zl'] = pd.to_numeric(df_clean['price_total_zl'], errors='coerce')
    
    # Remove rows where price conversion failed (NaN values)
    df_clean = df_clean.dropna(subset=['price_total_zl'])

    # Filter out unrealistic values (optional data cleaning)
    df_clean = df_clean[
        (df_clean['area_m2'] > 10) &  # minimum 10 m²
        (df_clean['area_m2'] < 500) &  # maximum 500 m²
        (df_clean['price_total_zl'] > 100000) &  # minimum 100k PLN
        (df_clean['price_total_zl'] < 5000000) &  # maximum 5M PLN
        (df_clean['rooms'] > 0) &  # at least 1 room
        (df_clean['rooms'] <= 10)  # maximum 10 rooms
    ]
    
    print(f"Loaded {len(df_clean)} apartments from CSV")
    print(f"Price range: {df_clean['price_total_zl'].min():,.0f} - {df_clean['price_total_zl'].max():,.0f} PLN")
    print(f"Area range: {df_clean['area_m2'].min():.1f} - {df_clean['area_m2'].max():.1f} m²")
    print(f"Rooms range: {df_clean['rooms'].min()} - {df_clean['rooms'].max()}")
    
    return df_clean


def train_model():
    """Train the linear regression model on real data and save it to pickle file"""
    # Load real data from CSV
    df = load_data()
    
    # Prepare features (X) and target (y)
    X = df[['area_m2', 'rooms']].values  # [area, rooms]
    y = df['price_total_zl'].values
    
    # Train the model
    model = LinearRegression().fit(X, y)
    
    # Calculate and print model performance
    score = model.score(X, y)
    print(f"Model R² score: {score:.4f}")
    print(f"Model coefficients: area_m2={model.coef_[0]:.2f}, rooms={model.coef_[1]:.2f}")
    print(f"Model intercept: {model.intercept_:.2f}")
    
    # Save model to pickle file
    model_path = Path("model.pkl")
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"Model trained on {len(X)} samples and saved to {model_path}")
    return model


def load_model():
    """Load the trained model from pickle file"""
    model_path = Path("model.pkl")
    if model_path.exists():
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        return model
    else:
        print("Model file not found. Training new model...")
        return train_model()


def predict_price(area_m2: float, rooms: int):
    """Predict price using the trained model"""
    model = load_model()
    return model.predict([[area_m2, rooms]])[0]


def test_model():
    """Test the trained model with sample predictions"""
    model = load_model()
    
    # Test with some sample apartments
    test_cases = [
        (50, 2),   # 50 m², 2 rooms
        (70, 3),   # 70 m², 3 rooms  
        (30, 1),   # 30 m², 1 room
        (100, 4),  # 100 m², 4 rooms
    ]
    
    print("\n=== Model Predictions ===")
    for area, rooms in test_cases:
        predicted_price = predict_price(area, rooms)
        price_per_m2 = predicted_price / area
        print(f"Area: {area} m², Rooms: {rooms} → Price: {predicted_price:,.0f} PLN ({price_per_m2:,.0f} PLN/m²)")


# Train and save the model when this module is imported
if __name__ == "__main__":
    train_model()
    test_model()