# 💳  Chipp.ai for Python

⚡ Building the pay-per-generation monetization platform for AI applications ⚡

[![PyPI version](https://badge.fury.io/py/chippai.svg)](https://pypi.org/project/chippai/) ![Downloads](https://pepy.tech/badge/chippai) [![Documentation Status](https://readthedocs.org/projects/ansicolortags/badge/?version=latest)](http://docs.chipp.ai) [![](https://dcbadge.vercel.app/api/server/8VCay4XTTh?compact=true&style=flat)](https://discord.gg/8VCay4XTTh) [![Twitter](https://img.shields.io/twitter/url/https/twitter.com/chippdotai.svg?style=social&label=Follow%20%40Chippdotai)](https://twitter.com/chippdotai) 

Be sure to sign up for an account and complete Stripe onboarding at https://app.chipp.ai

# Installation

`pip install chippai`

# Dependencies

This package requires requests for making API calls. However, it will be automatically installed when you install the chippai package using pip.

# Usage

```python
from chippai import Chipp

chipp = Chipp(api_key="your-api-key-from-Chipp-dashboard")

# userId needs to come from your database or auth session
user = chipp.get_user(user_id="a-unique-identifier-for-user")

# If the user is None, the user does not exist in the Chipp system and needs to be created
if user is None:
    user = chipp.create_user(user_id="a-unique-identifier-for-user")

# Get the number of credits remaining for this user
num_chipps = user.get_credits()

# Deduct credits from this user
user.deduct_credits(1)

# Generate a payment URL where this user can choose their preferred packages of credits and buy more.
# Pass in a redirect URL to bring your user back to your app after the user payment succeeds
url = user.get_packages_url(return_to_url="https://your-app.com/wherever-user-was")
```

# Further Documentation
For a more detailed guide and advanced usage patterns, refer to the [official documentation](http://docs.chipp.ai).

