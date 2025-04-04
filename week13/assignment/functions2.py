"""
Depth First Search
https://www.youtube.com/watch?v=9RHO6jU--GU

Breadth First Search
https://www.youtube.com/watch?v=86g8jAQug04

Requesting a family from the server:
family = Request_thread(f'{TOP_API_URL}/family/{id}')

Requesting an individual from the server:
person = Request_thread(f'{TOP_API_URL}/person/{id}')

10% Bonus to speed up part 3
"""
from common import *
import threading
import queue
import concurrent.futures
import threading

lock = threading.Lock()

def add_family_data_to_tree(family_data, tree):
    # Make sure to add the family and people to the tree correctly
    with lock:  # Ensure thread-safe modification of shared data
        tree.families[family_data['id']] = family_data
        # Add husband and wife to the tree
        tree.people[family_data['husband_id']] = {'id': family_data['husband_id'], 'role': 'husband'}
        tree.people[family_data['wife_id']] = {'id': family_data['wife_id'], 'role': 'wife'}
        
        # Add children to the tree
        for child_id in family_data['children']:
            tree.people[child_id] = {'id': child_id, 'role': 'child'}

def depth_fs_pedigree(family_id, tree):
    print(f"Starting Family id: {family_id}")
    print("############################################################")
    print(f"Depth First Search: 6 generations")
    print("############################################################")

    # Perform the API request to fetch the family data
    try:
        response = requests.get(f"http://localhost:8123/family/{family_id}")
        if response.status_code == 200:
            family_data = response.json()
            print(f"Successfully received family data: {family_data}")
            
            # Add the family data to the tree (update people and families)
            add_family_data_to_tree(family_data, tree)
            
        else:
            print(f"[ERROR] No data received for family {family_id}")
    
    except requests.RequestException as e:
        print(f"[ERROR] An error occurred while fetching family data: {e}")

    print(f"Tree state after family data insertion:")
    print(tree.__dict__)  # Check what is actually stored

    # Here, you can continue with the DFS traversal or any other logic you need
    print("Depth First Search Complete!")

# Example usage
tree = {
    'people': {},
    'families': {},
    'start_family_id': 5002824295,
}

depth_fs_pedigree(5002824295, tree)

# -----------------------------------------------------------------------------
def breadth_fs_pedigree(start_id, tree):
    # TODO - implement breadth first retrieval

    print('WARNING: BFS function not written')

    pass


# -----------------------------------------------------------------------------
def breadth_fs_pedigree_limit5(start_id, tree):
    # TODO - implement breadth first retrieval
    #      - Limit number of concurrent connections to the FS server to 5

    print('WARNING: BFS (Limit of 5 threads) function not written')

    pass
