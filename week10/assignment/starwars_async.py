import json
import threading
import time
from datetime import datetime, timedelta

import requests

# Const Values
TOP_API_URL = 'http://127.0.0.1:8790'

def main():
    
    t = requests.get(TOP_API_URL)
    response = t.json()
    film_url = response['films']
    t = requests.get(f'{film_url}6')
    response = t.json()
    print(response['characters'])
    
    # TODO - create a process pool
    #      - call apply_async to call a function that passes the url as argument
    #      - the function makes a request to the web server using the url
    #      - use a callback function to get the return result and print out the name



if __name__ == "__main__":
    main()