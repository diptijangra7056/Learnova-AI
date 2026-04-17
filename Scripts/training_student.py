import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
import joblib
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import os
# Encode string labels into integers
le = LabelEncoder()

df = pd.read_csv("DATA/data_student.csv") 

x = df[['english_marks', 'maths_marks', 'science_marks', 'computer_marks']]
y = df["course"]              
y = le.fit_transform(df["course"])

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

# Train models
rf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
rf.fit(x_train, y_train)
y_pred = rf.predict(x_test)
y_pred_labels = le.inverse_transform(y_pred)
y_test_labels = le.inverse_transform(y_test)
print("Sample Predictions:")
for true, pred in zip(y_test_labels[:10], y_pred_labels[:10]):
    print(f"True: {true}  Predicted: {pred}")

#accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"\nRandom Forest Accuracy: {accuracy:.4f}")
print(classification_report(y_test, y_pred))

#boosting algorithm
gb = GradientBoostingClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=3,
    min_samples_split=2,
    min_samples_leaf=1,
    subsample=1.0,
    random_state=42    
)
gb.fit(x_train, y_train)
y_pred_gb = gb.predict(x_test)
gb_accuracy = accuracy_score(y_test, y_pred_gb)
print(f"Gradient Boosting Accuracy: {gb_accuracy:.4f}")

os.makedirs("../MODELS", exist_ok=True)

joblib.dump(rf,"MODELS/recommendation_model.pkl")
joblib.dump(le, "MODELS/label_encoder.pkl")
print("✅ Recommendation model trained and saved!")
