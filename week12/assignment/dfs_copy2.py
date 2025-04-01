import time
import requests
from virusApi import *
from cse251functions import *
import threading
import collections  # For deque
from concurrent.futures import ThreadPoolExecutor

TOP_API_URL = 'http://127.0.0.1:8129'
NUMBER_GENERATIONS = 6
NUMBER_THREADS = 0  # To track the number of threads used, initialized at 0
LOCK = threading.Lock()  # Lock to ensure safe deque access across threads

def create_family(family_id, q: collections.deque, pandemic: Pandemic):
    """Fetches family and virus data from the API and processes them using threads."""
    global NUMBER_THREADS  # Use global counter for tracking threads

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

            if virus.parents:
                with LOCK:  # Ensure only one thread accesses the deque at a time
                    q.append(virus.parents)  # Using deque append() for better performance

    if not q:
        with LOCK:  # Ensure the termination signal is set properly
            q.append("DONE")  # Mark the queue as done


def dfs(start_id, generations):
    """Performs a multithreaded depth-first search to fetch and process virus data."""
    global NUMBER_THREADS  # Track total thread count

    pandemic = Pandemic(start_id)

    # Start the pandemic simulation
    requests.get(f'{TOP_API_URL}/start/{generations}')

    # Initialize a thread-safe stack (deque)
    q = collections.deque([start_id])

    # Increase max_workers to a higher value (e.g., 100) for better concurrency
    with ThreadPoolExecutor(max_workers=100) as executor:  # Adjust max_workers based on load
        while True:
            with LOCK:  # Lock to ensure we safely pop from the deque
                if q:  # Ensure deque isn't empty
                    family_id = q.popleft()  # Deque pop from the left for faster processing
                else:
                    continue  # Skip iteration if deque is empty

            if family_id == "DONE":  # Termination condition when there are no more families to process
                break

            # Increment thread count and submit a new task to process the family
            NUMBER_THREADS += 1
            executor.submit(create_family, family_id, q, pandemic)

    # End the pandemic simulation
    requests.get(f'{TOP_API_URL}/end')

    # Print statistics
    print('')
    print(f'Total Viruses  : {pandemic.get_virus_count()}')
    print(f'Total Families : {pandemic.get_family_count()}')
    print(f'Generations    : {generations}')

    return pandemic.get_virus_count()


def main():
    """Main function to start simulation and measure performance."""
    global NUMBER_THREADS

    begin_time = time.perf_counter()

    print(f'Pandemic starting...')
    print('#' * 60)

    # Get start family ID
    response = requests.get(f'{TOP_API_URL}')
    jsonResponse = response.json()
    start_id = jsonResponse['start_family_id']

    print(f'First Virus Family id: {start_id}')

    # Run the DFS simulation
    virus_count = dfs(start_id, NUMBER_GENERATIONS)

    total_time = time.perf_counter() - begin_time

    # Print the results
    print(f'\nTotal time = {total_time:.2f} sec')
    print(f'Number of threads: {NUMBER_THREADS}')
    print(f'Performance: {round(virus_count / total_time, 2)} viruses/sec')


if __name__ == '__main__':
    main()
    create_signature_file("CSE251W25")