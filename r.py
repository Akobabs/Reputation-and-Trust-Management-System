import requests

for i in range(150):
    data = {
        'worker_id': 1,
        'client_id': 2,
        'rating': 4.0,
        'seller_gender': 'male',
        'seller_nationality': 'USA',
        'comment': f'Test review {i}'
    }
    response = requests.post('http://127.0.0.1:5000/submit_review', data=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")
    try:
        print(f"JSON Response: {response.json()}")
    except requests.exceptions.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")