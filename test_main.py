from fastapi.testclient import TestClient
from main import app
import os

client = TestClient(app)

def test_analyze_contract_txt():
    # Create a dummy text file for testing
    with open("dummy.txt", "w") as f:
        f.write("This is a test contract.")

    with open("dummy.txt", "rb") as f:
        response = client.post("/analyze_contract/", files={"file": ("dummy.txt", f, "text/plain")})
    
    assert response.status_code == 200
    assert "analysis" in response.json()
    
    os.remove("dummy.txt")
