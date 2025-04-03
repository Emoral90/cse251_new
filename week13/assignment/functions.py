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

# Shared Data Structures
visited = set()  # Keeps track of processed person IDs
visited_lock = threading.Lock()  # Synchronization lock
stack = queue.LifoQueue()  # Thread-safe DFS stack


# -----------------------------------------------------------------------------
def depth_fs_pedigree(family_id, tree):
    # TODO - implement Depth first retrieval

    stack = [family_id]  # Stack for DFS
    visited_families = set()

    while stack:
        current_family_id = stack.pop()

        if current_family_id in visited_families:
            continue
        visited_families.add(current_family_id)

        # Request family data from the server
        family_request = Request_thread(f'{TOP_API_URL}/family/{current_family_id}')
        family_request.start()
        family_request.join()
        if not family_request.response:
            continue

        family = Family(current_family_id, family_request.response)
        tree.add_family(family)

        # Retrieve and add husband
        if family.husband:
            husband_request = Request_thread(f'{TOP_API_URL}/person/{family.husband}')
            husband_request.start()
            husband_request.join()
            if husband_request.response:
                husband = Person(husband_request.response)
                tree.add_person(husband)
                if husband.parents:  # Push husband's parent family to stack
                    stack.append(husband.parents)

        # Retrieve and add wife
        if family.wife:
            wife_request = Request_thread(f'{TOP_API_URL}/person/{family.wife}')
            wife_request.start()
            wife_request.join()
            if wife_request.response:
                wife = Person(wife_request.response)
                tree.add_person(wife)
                if wife.parents:  # Push wife's parent family to stack
                    stack.append(wife.parents)

        # Retrieve and add children
        for child_id in family.children:
            child_request = Request_thread(f'{TOP_API_URL}/person/{child_id}')
            child_request.start()
            child_request.join()
            if child_request.response:
                child = Person(child_request.response)
                tree.add_person(child)

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
