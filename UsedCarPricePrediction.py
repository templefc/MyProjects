import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from flask import Flask, request, jsonify
from flask_cors import CORS

train_df = pd.read_csv('Data/train-data.csv')
train_df = train_df.dropna()

categorical_columns = ['Name', 'Location', 'Fuel_Type', 'Transmission']
label_encoders = {}
for column in categorical_columns:
    le = LabelEncoder()
    train_df[column] = le.fit_transform(train_df[column])
    label_encoders[column] = le

X_train = train_df.drop(columns=['Price'])
y_train = train_df['Price']

if hasattr(X_train, "isnull"):
    print("Missing values found:", X_train.isnull().sum().sum())
    X_train = X_train.fillna(0)  
else:
    print("Missing values found:", np.isnan(X_train).sum())
    X_train = np.nan_to_num(X_train) 

    X_train = X_train.select_dtypes(include=[np.number]) 

print(f"X_train type: {type(X_train)}")
print(f"X_train shape: {X_train.shape}")
print(X_train.head() if hasattr(X_train, "head") else X_train[:5])

scaler = StandardScaler()
try:
    X_train_scaled = scaler.fit_transform(X_train)
except Exception as e:
    print(f"Error during scaling: {e}")
X_train_scaled = scaler.fit_transform(X_train)

print("Scaled Data (first 5 rows):", X_train_scaled[:5])


model = LinearRegression()
model.fit(X_train_scaled, y_train)

joblib.dump(model, 'linear_regression_model.pkl')
joblib.dump(scaler, 'scaler.pkl')
joblib.dump(label_encoders, 'label_encoders.pkl')

test_df = pd.read_csv('Data/test-data.csv')
test_df = test_df.dropna()

for column in categorical_columns:
    le = label_encoders[column]
    test_df[column] = le.transform(test_df[column])

X_test = test_df.drop(columns=['Price'])
y_test = test_df['Price']

X_test_scaled = scaler.transform(X_test)

y_pred = model.predict(X_test_scaled)

mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f'Mean Absolute Error: {mae}')
print(f'Mean Squared Error: {mse}')
print(f'R-squared: {r2}')

app = Flask(__name__)
CORS(app)

def load_dropdown_data():
    car_data = {
        "car_models": train_df['Name'].dropna().unique().tolist(),
        "years": train_df['Year'].dropna().unique().tolist(),
        "locations": train_df['Location'].dropna().unique().tolist(),
        "fuel_types": train_df['Fuel_Type'].dropna().unique().tolist(),
        "transmissions": train_df['Transmission'].dropna().unique().tolist(),
        "mileage": train_df['Mileage'].dropna().unique().tolist(),
        "engine": train_df['Engine'].dropna().unique().tolist(),
        "power": train_df['Power'].dropna().unique().tolist(),
        "seats": train_df['Seats'].dropna().unique().tolist(),
        "new_price": train_df['New_Price'].dropna().unique().tolist(),
        "kilometers_driven": train_df['Kilometers_Driven'].dropna().unique().tolist()
    }
    return car_data

def validate_input(data):
    required_fields = ['Name', 'Year', 'Location', 'Fuel_Type', 'Transmission', 'Mileage', 
                       'Engine', 'Power', 'Seats', 'New_Price', 'Kilometers_Driven']
    
    for field in required_fields:
        if field not in data:
            return f"Missing required field: {field}"

    try:
        year = int(data['Year'])
        if year < 1900 or year > 2024:
            return "Invalid Year. Year should be between 1900 and 2024."
    except ValueError:
        return "Invalid Year format. It should be a number."
    
    try:
        mileage = int(data['Mileage'])
        if mileage < 0:
            return "Invalid Mileage. Mileage should be a positive number."
    except ValueError:
        return "Invalid Mileage format. It should be a number."

    try:
        engine = float(data['Engine'])
        if engine <= 0:
            return "Invalid Engine size. Engine size should be a positive number."
    except ValueError:
        return "Invalid Engine format. It should be a number."

    try:
        power = int(data['Power'])
        if power <= 0:
            return "Invalid Power. Power should be a positive number."
    except ValueError:
        return "Invalid Power format. It should be a number."

    try:
        seats = int(data['Seats'])
        if seats < 1 or seats > 9:
            return "Invalid Seats. Seats should be between 1 and 9."
    except ValueError:
        return "Invalid Seats format. It should be a number."
    
    try:
        new_price = float(data['New_Price'][1:].replace(',', ''))
        if new_price <= 0:
            return "Invalid New Price. New Price should be a positive number."
    except ValueError:
        return "Invalid New Price format. It should be a number."

    try:
        kilometers_driven = int(data['Kilometers_Driven'].replace(' km', '').replace(',', ''))
        if kilometers_driven < 0:
            return "Invalid Kilometers Driven. Kilometers should be a positive number."
    except ValueError:
        return "Invalid Kilometers Driven format. It should be a number."

    return None

@app.route('/')
def index():
    return "Welcome to the Used Car Price Prediction API!"

@app.route('/get_car_data', methods=['GET'])
def get_car_data():
    car_data = load_dropdown_data()
    return jsonify(car_data)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    validation_error = validate_input(data)
    if validation_error:
        return jsonify({"error": validation_error}), 400


    car_model = label_encoders['Name'].transform([data['Name']])[0]
    location = label_encoders['Location'].transform([data['Location']])[0]
    fuel_type = label_encoders['Fuel_Type'].transform([data['Fuel_Type']])[0]
    transmission = label_encoders['Transmission'].transform([data['Transmission']])[0]
    
    year = int(data['Year'])
    mileage = int(data['Mileage'])
    engine = float(data['Engine'])
    power = int(data['Power'])
    seats = int(data['Seats'])
    new_price = float(data['New_Price'][1:].replace(',', ''))
    kilometers_driven = int(data['Kilometers_Driven'].replace(' km', '').replace(',', ''))

    features = [car_model, year, location, fuel_type, transmission, mileage, engine, power, seats, new_price, kilometers_driven]
    features_df = pd.DataFrame([features], columns=['Name', 'Year', 'Location', 'Fuel_Type', 'Transmission', 'Mileage', 'Engine', 'Power', 'Seats', 'New_Price', 'Kilometers_Driven'])

    features_scaled = scaler.transform(features_df)

    prediction = model.predict(features_scaled)

    return jsonify({'predicted_price': prediction[0]})

@app.route('/evaluate', methods=['GET'])
def evaluate():
    return jsonify({
        'Mean_Absolute_Error': mae,
        'Mean_Squared_Error': mse,
        'R_squared': r2
    })

if __name__ == '__main__':
    app.run(debug=True)
