import requests


# response = requests.post(
#     "http://localhost:8000/advertisement",
#     json={"title": "adv_1", "description": "desc_1", "price": "356","owner": "User_1"},
# )
# response = requests.get("http://localhost:8000/advertisement/9")
# response = requests.patch(
#     "http://localhost:8000/advertisement/9",
#     json = {"title": "adv_2"}
# )

response = requests.get("http://localhost:8000/advertisement?title=adv_1")


print(response.text)
print(response.status_code)
