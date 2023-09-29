import requests

def main():
    url = "https://server-fuie.onrender.com/message?prompt="

    def generate(prompt):
        response = requests.get(url + prompt)
        return response.text

    while True:
        prompt = input("User: ")
        if prompt == "exit":
            break
        message = generate(prompt)
        print("Chikku: " + message)
