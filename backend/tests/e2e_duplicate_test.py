from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_duplicate_guess():
    # First guess
    response1 = client.post("/guess?guess=Paper&persona=serious")
    assert response1.status_code == 200
    user_id = response1.cookies.get("user_id")
    assert user_id is not None

    # Second duplicate guess
    response2 = client.post(f"/guess?guess=Paper&persona=serious", cookies={"user_id": user_id})
    assert response2.status_code == 200 # Changed from 400 to 200
    assert "GAME OVER!" in response2.json()["message"] # Changed assertion

    #check that the score is reset to zero
    response3 = client.get(f"/history", cookies={"user_id": user_id})
    assert response3.status_code == 200
    assert len(response3.json()["history"]) == 1
