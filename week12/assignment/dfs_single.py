import time
import requests
from virusApi import *
from cse251functions import *

TOP_API_URL = 'http://127.0.0.1:8129'
NUMBER_GENERATIONS = 6
NUMBER_THREADS = 0  # Single-threaded for now

# COMMENT every line you write yourself

def dfs(start_id, generations):
    """Performs an iterative depth-first search to fetch and process virus data."""
    global NUMBER_THREADS

    pandemic = Pandemic(start_id)

    # Start the pandemic simulation
    requests.get(f'{TOP_API_URL}/start/{generations}')

    stack = []  # DFS stack
    stack.append(start_id)

    while stack:
        family_id = stack.pop()

        # Request family data
        family_response = requests.get(f'{TOP_API_URL}/family/{family_id}')
        if not family_response.ok:
            continue

        family = Family.fromResponse(family_response.json())

        if not pandemic.does_family_exist(family.id):
            pandemic.add_family(family)

        # Request and add viruses
        virus_data = []

        for vid in [family.virus1, family.virus2] + family.offspring:
            if vid:
                response = requests.get(f'{TOP_API_URL}/virus/{vid}')
                if response.ok:
                    virus_data.append(response.json())

        for vdata in virus_data:
            virus = Virus.createVirus(vdata)

            if not pandemic.does_virus_exist(virus.id):
                pandemic.add_virus(virus)

                # Add parents' family id to stack for DFS
                if virus.parents:
                    stack.append(virus.parents)

    # End the simulation
    requests.get(f'{TOP_API_URL}/end')

    # Print stats
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

    virus_count = dfs(start_id, NUMBER_GENERATIONS)

    total_time = time.perf_counter() - begin_time

    print(f'\nTotal time = {total_time:.2f} sec')
    print(f'Number of threads: {NUMBER_THREADS}')  # Will be 0 or 1 for now
    print(f'Performance: {round(virus_count / total_time, 2)} viruses/sec')


if __name__ == '__main__':
    main()
    create_signature_file("CSE251W25")