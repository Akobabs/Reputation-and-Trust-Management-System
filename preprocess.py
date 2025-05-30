import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

def preprocess_fiverr_data(input_path, output_path):
    # Load dataset
    df = pd.read_csv(input_path)
    
    # Clean 'Number of Reviewers'
    def clean_reviewers(value):
        if isinstance(value, str) and 'k+' in value.lower():
            return int(float(value.lower().replace('k+', '')) * 1000)
        return int(value)
    df['Number of Reviewers'] = df['Number of Reviewers'].apply(clean_reviewers)
    
    # Handle missing values
    df['Average Rating'] = df['Average Rating'].fillna(df['Average Rating'].mean())
    
    # Remove duplicates based on 'Title' (as no 'gig_id' or 'seller_id')
    df.drop_duplicates(subset=['Title'], inplace=True)
    
    # Normalize ratings
    df['Average Rating'] = df['Average Rating'].clip(1, 5)
    
    # Simulate demographic data
    df['seller_gender'] = np.random.choice(['male', 'female', 'unknown'], size=len(df), p=[0.45, 0.45, 0.1])
    df['seller_nationality'] = np.random.choice(['USA', 'India', 'Pakistan', 'Nigeria', 'UK'], size=len(df), p=[0.4, 0.2, 0.2, 0.1, 0.1])
    
    # Simulate bias_flag (low ratings for specific nationalities)
    df['bias_flag'] = 0
    bias_condition = (df['Average Rating'] < 3) & (df['seller_nationality'].isin(['India', 'Pakistan', 'Nigeria']))
    df.loc[bias_condition, 'bias_flag'] = 1
    
    # Encode categorical variables
    le_gender = LabelEncoder()
    le_nationality = LabelEncoder()
    df['seller_gender'] = le_gender.fit_transform(df['seller_gender'])
    df['seller_nationality'] = le_nationality.fit_transform(df['seller_nationality'])
    
    # Save processed dataset
    df.to_csv(output_path, index=False)
    return df

if __name__ == "__main__":
    preprocess_fiverr_data('data/fiverr-data-gigs-cleaned.csv', 'data/processed_fiverr_data.csv')