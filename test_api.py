import requests
import json

# Test configuration
BASE_URL = "http://localhost:8000"
TOKEN = "ec50966dd6ad633d5d916660e0ce299987cc4be90656b981fb49b9ffa8042e1c"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Test data
test_request = {
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
        "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
        "What is the waiting period for pre-existing diseases (PED) to be covered?",
        "Does this policy cover maternity expenses, and what are the conditions?"
    ]
}

def test_health():
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check: {response.status_code}")
    print(response.json())

def test_main_endpoint():
    response = requests.post(
        f"{BASE_URL}/api/v1/hackrx/run",
        headers=headers,
        json=test_request
    )
    print(f"Main endpoint: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(json.dumps(result, indent=2))
    else:
        print(response.text)

if __name__ == "__main__":
    test_health()
    test_main_endpoint()