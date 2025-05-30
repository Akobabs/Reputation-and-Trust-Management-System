import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder

class BiasDetector:
    def __init__(self):
        self.model = RandomForestClassifier(random_state=42)
        self.label_encoders = {'seller_gender': LabelEncoder(), 'seller_nationality': LabelEncoder()}
        self.is_trained = False
        self.feature_order = ['Average Rating', 'seller_gender', 'seller_nationality']

    def train(self, data_path):
        try:
            df = pd.read_csv(data_path)
            # Verify required columns
            if not all(col in df.columns for col in self.feature_order + ['bias_flag']):
                missing = [col for col in self.feature_order + ['bias_flag'] if col not in df.columns]
                raise ValueError(f"Missing columns: {missing}")
            X = df[self.feature_order]
            y = df['bias_flag']
            # Encode categorical features
            X.loc[:, 'seller_gender'] = self.label_encoders['seller_gender'].fit_transform(X['seller_gender'])
            X.loc[:, 'seller_nationality'] = self.label_encoders['seller_nationality'].fit_transform(X['seller_nationality'])
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            self.model.fit(X_train, y_train)
            self.is_trained = True
            y_pred = self.model.predict(X_test)
            print("Accuracy:", accuracy_score(y_test, y_pred))
            print("Classification Report:\n", classification_report(y_test, y_pred))
            return self.model
        except Exception as e:
            print(f"Training error: {str(e)}")
            raise

    def predict(self, review_data):
        if not self.is_trained:
            raise ValueError("Model not trained")
        # Validate input
        if not all(key in review_data for key in self.feature_order):
            raise ValueError(f"Missing required keys: {self.feature_order}")
        if not isinstance(review_data['Average Rating'], (int, float)) or review_data['Average Rating'] < 1 or review_data['Average Rating'] > 5:
            raise ValueError("Average Rating must be a number between 1 and 5")
        # Encode categorical features
        try:
            review_data = review_data.copy()  # Avoid modifying input
            review_data['seller_gender'] = self.label_encoders['seller_gender'].transform([review_data['seller_gender']])[0]
            review_data['seller_nationality'] = self.label_encoders['seller_nationality'].transform([review_data['seller_nationality']])[0]
        except ValueError as e:
            raise ValueError(f"Invalid categorical value: {str(e)}")
        # Create DataFrame with correct feature order
        X = pd.DataFrame([review_data], columns=self.feature_order)
        return self.model.predict(X)[0]

if __name__ == "__main__":
    detector = BiasDetector()
    detector.train('data/processed_fiverr_data.csv')