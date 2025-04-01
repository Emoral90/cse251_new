import queue
import threading
import time
import requests
from concurrent.futures import ThreadPoolExecutor  # Import for thread management
from cse251functions import *
from virusApi import *

TOP_API_URL = 'http://127.0.0.1:8129'
NUMBER_GENERATIONS = 6  # set this to 2 as you are testing your code
NUMBER_THREADS = 0  # TODO use this to keep track of the number of threads you create

#COMMENT every line that you write yourself.

def create_family(family_id, q: queue.Queue, pandemic: Pandemic):
    """Fetches family and virus data from the API and processes them using threads."""

    global NUMBER_THREADS  # Use global counter for tracking threads

    # base case
    if family_id is None:
        return

    # CREATE FAMILY THREAD 
    family_response = requests.get(
        f'http://{hostName}:{serverPort}/family/{family_id}')

    if "id" not in family_response.json():
        return

    # ADD FAMILY
    family = Family.fromResponse(family_response.json())
    #print(f'###\n{family}\n###')
    pandemic.add_family(family)

    # Flag to indicate if there are no more parents to check
    any_more_parents = False
    # Add viruses and their offspring to the same list
    virus_data = []

    # Get VIRUS1
    if family.virus1:
        response = requests.get(
            f'http://{hostName}:{serverPort}/virus/{family.virus1}')
        if response.ok:
            virus_data.append(response.json())

    # Get VIRUS2
    if family.virus2:
        response = requests.get(
            f'http://{hostName}:{serverPort}/virus/{family.virus2}')
        if response.ok:
            virus_data.append(response.json())

    # Get OFFSPRING
    for id in family.offspring:
        response = requests.get(f'http://{hostName}:{serverPort}/virus/{id}')
        if response.ok:
            virus_data.append(response.json())

    # Add virus and their offspring to the Pandemic
    for v_data in virus_data:
        v = Virus.createVirus(v_data)
        if not pandemic.does_virus_exist(v.id):
            pandemic.add_virus(v)
            if v.parents:
                q.put(v.parents)
                any_more_parents = True

    # Exit the WHILE loop
    if not any_more_parents:
        q.put("DONE")


def bfs(start_id, generations):
    """Performs a breadth-first search using multithreading to fetch and process virus data."""

    global NUMBER_THREADS  # Track total thread count
    pandemic = Pandemic(start_id)

    # tell server we are starting a new generation of viruses
    requests.get(f'{TOP_API_URL}/start/{generations}')

    q = queue.Queue()
    q.put(start_id)

    # Use the slick new ThreadPoolExecutor to retreive multiple viruses as possible
    # instead of doing so sequentially
    with ThreadPoolExecutor(max_workers=50) as executor:
        while True:
            family_id = q.get()

            if family_id == "DONE":
                break

            # Increment thread count and submit family processing task
            NUMBER_THREADS += 1
            executor.submit(create_family, family_id, q, pandemic)

    requests.get(f'{TOP_API_URL}/end')

    # Print results
    print('')
    print(f'Total Viruses  : {pandemic.get_virus_count()}')
    print(f'Total Families : {pandemic.get_family_count()}')
    print(f'Generations    : {generations}')
    
    return pandemic.get_virus_count()


def main():
    global NUMBER_THREADS

    # Start a timer
    begin_time = time.perf_counter()

    print(f'Pandemic starting...')
    print('#' * 60)

    response = requests.get(f'{TOP_API_URL}')
    jsonResponse = response.json()

    print(f'First Virus Family id: {jsonResponse["start_family_id"]}')
    start_id = jsonResponse['start_family_id']

    virus_count = bfs(start_id, NUMBER_GENERATIONS)

    total_time = time.perf_counter() - begin_time
    total_time_str = "{:.2f}".format(total_time)

    print(f'\nTotal time = {total_time_str} sec')
    print(f'Number of threads: {NUMBER_THREADS}')
    print(f'Performance: {round(virus_count / total_time, 2)} viruses/sec')


if __name__ == '__main__':
    main()
    create_signature_file("CSE251W25")