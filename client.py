import requests

#
#
# response = requests.post(
#     "http://localhost:8000/advertisement",
#     json={"title": "adv_3", "description": "desc_1", "owner": "User_1"},
# )
# response = requests.get("http://localhost:8000/advertisement/1")
# response = requests.patch(
#     "http://localhost:8000/advertisement/2",
#     json = {"title": "adv_1"}
# )

response = requests.get("http://localhost:8000/advertisement?title=adv_2")


print(response.text)
print(response.status_code)
