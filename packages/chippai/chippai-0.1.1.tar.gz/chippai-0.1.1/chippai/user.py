import requests

BASE_URL = "https://app.chipp.ai/api/public"

class User:
    def __init__(self, user_id, api_key):
        self.user_id = user_id
        self.api_key = api_key
        self.token_balance = self.get_credits()

    def get_credits(self):
        response = requests.get(f"{BASE_URL}/user/{self.user_id}", headers={
            "Authorization": f"Bearer {self.api_key}"
        })
        response.raise_for_status()  # Will raise an error if not a 2xx response
        return response.json()['tokenBalance']

    def deduct_credits(self, quantity):
        response = requests.post(
            f"{BASE_URL}/transactions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "tokenQty": quantity,
                "consumerIdentifier": self.user_id
            }
        )
        response.raise_for_status()
        self.token_balance -= quantity

    def get_packages_url(self, return_to_url=None):
        url = f"{BASE_URL}/purchase-page/packages-url/?consumerIdentifier={self.user_id}"
        if return_to_url:
            url += f"&returnToUrl={return_to_url}"
        response = requests.get(url, headers={
            "Authorization": f"Bearer {self.api_key}"
        })
        response.raise_for_status()
        return response.json()['url']
