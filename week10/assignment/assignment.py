'''
Requirements
1. Create a multiprocessing program that reads in files with defined tasks to perform.
2. The program should use a process pool per task type and use apply_async calls with callback functions.
3. The callback functions will store the results in global lists based on the task to perform.
4. Once all 4034 tasks are done, the code should print out each list and a breakdown of 
   the number of each task performed.
5. COMMENT every line that you write yourself.
   
Questions:
1. How many processes did you specify for each pool:
   >Finding primes:                                 10
   >Finding words in a file:                        20
   >Changing text to uppercase:                     20 
   >Finding the sum of numbers:                     10
   >Web request to get names of Star Wars people:   20
   
   >How do you determine these numbers: I figured since CPU bound tasks takes up one core each, I dont want to overload all of my 20 cores with processes. And since you have to wait pretty often for IO bound tasks, I believe double the amount of processes should allow the program to concurrently run more efficiently
   
2. Specify whether each of the tasks is IO Bound or CPU Bound?
   >Finding primes:                                 CPU bound
   >Finding words in a file:                        IO bound
   >Changing text to uppercase:                     IO bound
   >Finding the sum of numbers:                     CPU bound
   >Web request to get names of Star Wars people:   IO bound
   
3. What was your overall time, with:
   >one process in each of your five pools:  208.94714426994324 seconds
   >with the number of processes you show in question one:  32.48956894874573 seconds
'''

import glob
import json
import math
import multiprocessing as mp
import os
import time
from datetime import datetime, timedelta
from cse251functions import *

import numpy as np
import requests

TYPE_PRIME = 'prime'
TYPE_WORD = 'word'
TYPE_UPPER = 'upper'
TYPE_SUM = 'sum'
TYPE_NAME = 'name'

# Global lists to collect the task results
result_primes = []
result_words = []
result_upper = []
result_sums = []
result_names = []


def is_prime(n: int):
    """Primality test using 6k+-1 optimization.
    From: https://en.wikipedia.org/wiki/Primality_test
    """
    if n <= 3:
        return n > 1
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i ** 2 <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def task_prime(value):
    """
    Use the is_prime() above
    Add the following to the global list:
        {value} is prime
            - or -
        {value} is not prime
    """
    # Use is_prime() to return either true or false
    result = f"{value} is prime" if is_prime(value) else f"{value} is not prime"
    return result


def task_word(word):
    """
    search in file 'words.txt'
    Add the following to the global list:
        {word} Found
            - or -
        {word} not found *****
    """
    # Read from file and check if words in words.txt is in the list
    with open('words.txt', 'r') as file:
        word_list = set(file.read().split())
    result = f"{word} Found" if word in word_list else f"{word} not found *****"
    return result


def task_upper(text):
    """
    Add the following to the global list:
        {text} ==>  uppercase version of {text}
    """
    # Capitalize every first letter
    return f"{text} ==> {text.upper()}"


def task_sum(start_value, end_value):
    """
    Add the following to the global list:
        sum of {start_value:,} to {end_value:,} = {total:,}
    """
    # Get to adding the 2 values
    total = sum(range(start_value, end_value + 1))
    return f"sum of {start_value:,} to {end_value:,} = {total:,}"


def task_name(url):
    """
    use requests module
    Add the following to the global list:
        {url} has name <name>
            - or -
        {url} had an error receiving the information
    """
    # Everythin inside a try and except block since it's considered good coding
    # etiquette when making requests to a server
    try:
        response = requests.get(url)
        if response.status_code == 200:
            name = response.json().get("name", "Unknown")
            return f"{url} has name {name}"
        else:
            return f"{url} had an error receiving the information"
    except requests.RequestException:
        return f"{url} had an error receiving the information"

# Thank you for putting this in here
def load_json_file(filename):
    if os.path.exists(filename):
        with open(filename) as json_file:
            data = json.load(json_file)
        return data
    else:
        return {}


def main():
    begin_time = time.time()
    
    # Load tasks
    task_files = glob.glob("tasks/*.task")
    tasks = [load_json_file(file) for file in task_files]
    count = len(tasks)

    # TODO Create process pools
    prime_pool = mp.Pool(processes=10)
    word_pool = mp.Pool(processes=20)
    upper_pool = mp.Pool(processes=20)
    sum_pool = mp.Pool(processes=10)
    name_pool = mp.Pool(processes=20)

    # prime_pool = mp.Pool(processes=1)
    # word_pool = mp.Pool(processes=1)
    # upper_pool = mp.Pool(processes=1)
    # sum_pool = mp.Pool(processes=1)
    # name_pool = mp.Pool(processes=1)
    
    # Process task pools asynchronously
    for task in tasks:
        # Check task name
        if task['task'] == TYPE_PRIME:
            prime_pool.apply_async(task_prime, (task['value'],), callback=result_primes.append) 
            # I learned that callbacks are pretty handy when it comes to not
            # blocking the main thread and automatically storing the results where you
            # tell it to
        elif task['task'] == TYPE_WORD:
            word_pool.apply_async(task_word, (task['word'],), callback=result_words.append)
        elif task['task'] == TYPE_UPPER:
            upper_pool.apply_async(task_upper, (task['text'],), callback=result_upper.append)
        elif task['task'] == TYPE_SUM:
            sum_pool.apply_async(task_sum, (task['start'], task['end']), callback=result_sums.append)
        elif task['task'] == TYPE_NAME:
            name_pool.apply_async(task_name, (task['url'],), callback=result_names.append)
    
    # TODO start pools and block until they are done before trying to print
    prime_pool.close()
    word_pool.close()
    upper_pool.close()
    sum_pool.close()
    name_pool.close()
    prime_pool.join()
    word_pool.join()
    upper_pool.join()
    sum_pool.join()
    name_pool.join()

    def print_list(lst):
        for item in lst:
            print(item)
        print(' ')

    print('-' * 80)
    print(f'Primes: {len(result_primes)}')
    print_list(result_primes)

    print('-' * 80)
    print(f'Words: {len(result_words)}')
    print_list(result_words)

    print('-' * 80)
    print(f'Uppercase: {len(result_upper)}')
    print_list(result_upper)

    print('-' * 80)
    print(f'Sums: {len(result_sums)}')
    print_list(result_sums)

    print('-' * 80)
    print(f'Names: {len(result_names)}')
    print_list(result_names)

    print(f'Number of Primes tasks: {len(result_primes)}')
    print(f'Number of Words tasks: {len(result_words)}')
    print(f'Number of Uppercase tasks: {len(result_upper)}')
    print(f'Number of Sums tasks: {len(result_sums)}')
    print(f'Number of Names tasks: {len(result_names)}')
    print(f'Finished processes {count} tasks = {time.time() - begin_time}')


if __name__ == '__main__':
    main()
    create_signature_file("CSE251W25")
