import requests
def get_test(URL, Token):
    

    headers = {
        'accept': 'application/json',
        'Authorisation': 'Bearer '+Token,
    }

    response = requests.get(URL, headers=headers)

    return response.text