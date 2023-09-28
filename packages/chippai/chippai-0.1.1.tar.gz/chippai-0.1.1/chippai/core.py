import requests
from .user import User

BASE_URL = "https://app.chipp.ai/api/public"

class Chipp:
    def __init__(self, api_key):
        self.api_key = api_key

    def create_user(self, user_id):
        response = requests.post(
            f"{BASE_URL}/user",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"consumerIdentifier": user_id}
        )
        if response.status_code == 409:
            raise Exception("User already exists")
        response.raise_for_status()
        return User(user_id, self.api_key)

    def get_user(self, user_id):
        response = requests.get(f"{BASE_URL}/user/{user_id}", headers={
            "Authorization": f"Bearer {self.api_key}"
        })
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return User(user_id, self.api_key)
