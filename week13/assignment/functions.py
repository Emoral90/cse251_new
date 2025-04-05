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
import requests
import queue
from collections import deque

# -----------------------------------------------------------------------------
def depth_fs_pedigree(family_id, tree):
    # TODO - implement Depth first retrieval

    visited_families = set()
    stack = [family_id]

    while stack:
        current_family_id = stack.pop()

        if current_family_id in visited_families:
            continue
        visited_families.add(current_family_id)

        # Request the family
        family_thread = Request_thread(f'{TOP_API_URL}/family/{current_family_id}')
        family_thread.start()
        family_thread.join()

        if not family_thread.response:
            print(f'[ERROR] No data received for family {current_family_id}')
            continue

        family_data = family_thread.response
        family = Family(current_family_id, family_data)
        tree.add_family(family)

        # Fetch husband and wife
        person_threads = []
        for person_id in [family.husband, family.wife]:
            thread = Request_thread(f'{TOP_API_URL}/person/{person_id}')
            thread.start()
            person_threads.append((person_id, thread))

        # Fetch children
        for child_id in family.children:
            thread = Request_thread(f'{TOP_API_URL}/person/{child_id}')
            thread.start()
            person_threads.append((child_id, thread))

        # Join all person threads and add to tree
        for person_id, thread in person_threads:
            thread.join()
            if thread.response:
                person = Person(thread.response)
                tree.add_person(person)

        # Add parents of husband and wife to stack (for DFS)
        for person_id in [family.husband, family.wife]:
            person = tree.get_person(person_id)
            if person:
                parent_family_id = person.parents
                if parent_family_id and parent_family_id not in visited_families:
                    stack.append(parent_family_id)

# -----------------------------------------------------------------------------
def breadth_fs_pedigree(start_id, tree):
    # TODO - implement breadth first retrieval

    visited_families = set()
    queue = deque([start_id])

    while queue:
        current_family_id = queue.popleft()

        if current_family_id in visited_families:
            continue
        visited_families.add(current_family_id)

        # Request the family
        family_thread = Request_thread(f'{TOP_API_URL}/family/{current_family_id}')
        family_thread.start()
        family_thread.join()

        if not family_thread.response:
            print(f'[ERROR] No data received for family {current_family_id}')
            continue

        family_data = family_thread.response
        family = Family(current_family_id, family_data)
        tree.add_family(family)

        # Fetch husband and wife
        person_threads = []
        for person_id in [family.husband, family.wife]:
            thread = Request_thread(f'{TOP_API_URL}/person/{person_id}')
            thread.start()
            person_threads.append((person_id, thread))

        # Fetch children
        for child_id in family.children:
            thread = Request_thread(f'{TOP_API_URL}/person/{child_id}')
            thread.start()
            person_threads.append((child_id, thread))

        # Join and store people
        for person_id, thread in person_threads:
            thread.join()
            if thread.response:
                person = Person(thread.response)
                tree.add_person(person)

        # Enqueue parents of husband and wife
        for person_id in [family.husband, family.wife]:
            person = tree.get_person(person_id)
            if person:
                parent_family_id = person.parents
                if parent_family_id and parent_family_id not in visited_families:
                    queue.append(parent_family_id)


# -----------------------------------------------------------------------------
def breadth_fs_pedigree_limit5(start_id, tree):
    # TODO - implement breadth first retrieval
    #      - Limit number of concurrent connections to the FS server to 5

    max_threads = 5
    semaphore = threading.Semaphore(max_threads)
    visited_families = set()
    queue = deque([start_id])
    lock = threading.Lock()

    def fetch_family_and_people(family_id):
        nonlocal tree, visited_families, queue

        # Acquire semaphore slot
        with semaphore:
            # Get family info
            family_thread = Request_thread(f'{TOP_API_URL}/family/{family_id}')
            family_thread.start()
            family_thread.join()

            if not family_thread.response:
                print(f'[ERROR] No family data for {family_id}')
                return

            family_data = family_thread.response
            family = Family(family_id, family_data)

            with lock:
                if family_id not in visited_families:
                    tree.add_family(family)
                    visited_families.add(family_id)

            # Fetch husband, wife, and children
            person_threads = []
            for person_id in [family.husband, family.wife] + family.children:
                person_thread = Request_thread(f'{TOP_API_URL}/person/{person_id}')
                person_thread.start()
                person_threads.append((person_id, person_thread))

            # Join threads and add people to tree
            for person_id, thread in person_threads:
                thread.join()
                if thread.response:
                    person = Person(thread.response)
                    with lock:
                        tree.add_person(person)

            # Enqueue parents (only once per family)
            for person_id in [family.husband, family.wife]:
                person = tree.get_person(person_id)
                if person and person.parents not in visited_families and person.parents is not None:
                    with lock:
                        queue.append(person.parents)

    # Start thread-processing loop
    threads = []

    while queue:
        family_id = queue.popleft()

        # Skip if already processed
        if family_id in visited_families:
            continue

        # Start a thread that uses semaphore
        t = threading.Thread(target=fetch_family_and_people, args=(family_id,))
        t.start()
        threads.append(t)

    # Wait for all threads to complete
    for t in threads:
        t.join()
