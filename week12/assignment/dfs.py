"""
Course: CSE 251
Lesson Week: 12
File: assignment.py
Author: Erick Morales
Purpose: Assignment 12 - Family Search
"""
import time
import requests
from virusApi import *
from cse251functions import *
import threading
import queue
from concurrent.futures import ThreadPoolExecutor

TOP_API_URL = 'http://127.0.0.1:8129'
NUMBER_GENERATIONS = 6 # set this to 2 as you are testing your code
NUMBER_THREADS = 0  # TODO use this to keep track of the number of threads you create

# COMMENT every line you write yourself

def create_family(family_id, q: queue.Queue, pandemic: Pandemic):
    """Fetches family and virus data from the API and processes them using threads."""
    global NUMBER_THREADS  # Use global counter for tracking threads

    # Exit condition if the family_id is None
    if family_id is None:
        return

    # Request family data from the server
    family_response = requests.get(f'{TOP_API_URL}/family/{family_id}')
    if not family_response.ok:
        return

    family = Family.fromResponse(family_response.json())
    if not pandemic.does_family_exist(family.id):
        pandemic.add_family(family)

    virus_data = []  # List to store virus data for the current family

    # Fetch virus information
    for vid in [family.virus1, family.virus2] + family.offspring:
        if vid:
            response = requests.get(f'{TOP_API_URL}/virus/{vid}')
            if response.ok:
                virus_data.append(response.json())

    # Add virus information to the pandemic and process further
    for vdata in virus_data:
        virus = Virus.createVirus(vdata)
        if not pandemic.does_virus_exist(virus.id):
            pandemic.add_virus(virus)

            # Add the virus' parents to the queue if available
            if virus.parents:
                q.put(virus.parents)  # Put parents in the stack for further processing

    # Signal the thread to stop if there are no more family IDs to process
    if q.empty():
        q.put("DONE")


def dfs(start_id, generations):
    """Performs a multithreaded depth-first search to fetch and process virus data."""
    global NUMBER_THREADS  # Track total thread count

    pandemic = Pandemic(start_id)

    # Start the pandemic simulation
    requests.get(f'{TOP_API_URL}/start/{generations}')

    # Initialize a thread safe queue
    q = queue.Queue()
    q.put(start_id)

    # Use ThreadPoolExecutor to manage threads and process family data concurrently
    with ThreadPoolExecutor(max_workers=50) as executor:
        while True:
            family_id = q.get()  # Pop a family ID from the queue

            if family_id == "DONE":  # Termination condition when there are no more families to process
                break

            # Increment the thread count and submit a new task to process the family
            NUMBER_THREADS += 1
            executor.submit(create_family, family_id, q, pandemic)

    # End the pandemic simulation
    requests.get(f'{TOP_API_URL}/end')

    # Print results
    print('')
    print(f'Total Viruses  : {pandemic.get_virus_count()}')
    print(f'Total Families : {pandemic.get_family_count()}')
    print(f'Generations    : {generations}')

    return pandemic.get_virus_count()


def main():
    """Main function to start simulation and measure performance."""
    global NUMBER_THREADS
    
    # Start timer
    begin_time = time.perf_counter()

    print(f'Pandemic starting...')
    print('#' * 60)

    response = requests.get(f'{TOP_API_URL}')
    jsonResponse = response.json()
    start_id = jsonResponse['start_family_id']

    print(f'First Virus Family id: {start_id}')

    virus_count = dfs(start_id, NUMBER_GENERATIONS)

    total_time = time.perf_counter() - begin_time

    print(f'\nTotal time = {total_time:.2f} sec')
    print(f'Number of threads: {NUMBER_THREADS}')  # Display the total number of threads used
    print(f'Performance: {round(virus_count / total_time, 2)} viruses/sec')


if __name__ == '__main__':
    main()
    create_signature_file("CSE251W25")