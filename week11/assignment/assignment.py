'''
Purpose: Dining philosophers problem

Problem statement

Five silent philosophers sit at a round table with bowls of spaghetti. Forks
are placed between each pair of adjacent philosophers.

Each philosopher must alternately think and eat. However, a philosopher can
only eat spaghetti when they have both left and right forks. Each fork can be
held by only one philosopher and so a philosopher can use the fork only if it
is not being used by another philosopher. After an individual philosopher
finishes eating, they need to put down both forks so that the forks become
available to others. A philosopher can only take the fork on their right or
the one on their left as they become available and they cannot start eating
before getting both forks.  When a philosopher is finished eating, they think 
for a little while.

Eating is not limited by the remaining amounts of spaghetti or stomach space;
an infinite supply and an infinite demand are assumed.

The problem is how to design a discipline of behavior (a concurrent algorithm)
such that no philosopher will starve

Instructions:

        ***************************************************
        ** DO NOT search for a solution on the Internet, **
        ** your goal is not to copy a solution, but to   **
        ** work out this problem.                        **
        ***************************************************

- When a philosopher wants to eat, it will ask the waiter if it can.  If the waiter 
  indicates that a philosopher can eat, the philosopher will pick up each fork and eat.  
  There must not be an issue picking up the two forks since the waiter is in control of 
  the forks. When a philosopher is finished eating, it will inform the waiter that they
  are finished.  If the waiter indicates to a philosopher that they can not eat, the 
  philosopher will wait between 1 to 3 seconds and try again.

- You have Locks and Semaphores that you can use.
- Remember that lock.acquire() has an argument called timeout. This can be useful to not
  block when trying to acquire a lock.
- Philosophers need to eat for 1 to 3 seconds when they get both forks.  
  When the number of philosophers has eaten MAX_MEALS times, stop the philosophers
  from trying to eat and any philosophers eating will put down their forks when finished.
- Philosophers need to think (digest?) for 1 to 3 seconds when they are finished eating.  
- You want as many philosophers to eat and think concurrently.
- Design your program to handle N philosophers and N forks (minimum of 5 philosophers).
- Use threads for this problem.
- Provide a way to "prove" that each philosophers will not starve. This can be counting
  how many times each philosophers eat and display a summary at the end. Or, keeping track
  how long each philosopher is eating and thinking.
- Using lists for philosophers and forks will help you in this program.
  for example: philosophers[i] needs forks[i] and forks[i+1] to eat. Hint, they are
  sitting in a circle.
'''

#COMMENT every line that you write yourself.

import time
import threading
from cse251functions import *
import random

PHILOSOPHERS = 5
MAX_MEALS = PHILOSOPHERS * 5

def main():
    # TODO - create the waiter (A class would be best here).
    # TODO - create the forks (What kind of object should a fork be?).
    # TODO - create PHILOSOPHERS philosophers.
    # TODO - Start them eating and thinking.
    # TODO - Display how many times each philosopher ate, 
    #        how long they spent eating, and how long they spent thinking.
    class Waiter:
      # Control access to forks
      def __init__(self, num_forks):
          self.forks = [threading.Lock() for _ in range(num_forks)]  # One lock per fork
          self.lock = threading.Lock()  # Sync access to forks

      def request_forks(self, left, right):
          # Request to pick up forks
          with self.lock:  # Check for locked forks
              if not self.forks[left].locked() and not self.forks[right].locked():
                  self.forks[left].acquire()
                  self.forks[right].acquire()
                  return True
              return False

      def release_forks(self, left, right):
          # Release both forks
          self.forks[left].release()
          self.forks[right].release()

    
    class Philosopher(threading.Thread):
        # Philosopher thread that eats and thinks
        def __init__(self, id, waiter, left_fork, right_fork, meals_count):
            super().__init__()
            self.id = id
            self.waiter = waiter
            self.left_fork = left_fork
            self.right_fork = right_fork
            self.meals_count = meals_count
            self.eating_time = 0
            self.thinking_time = 0

        def run(self):
            while sum(self.meals_count) < MAX_MEALS:
                # Think for 1 to 3 seconds
                thinking_duration = random.uniform(1, 3)
                self.thinking_time += thinking_duration
                time.sleep(thinking_duration)

                # Attempt to eat
                while not self.waiter.request_forks(self.left_fork, self.right_fork):
                    time.sleep(random.uniform(1, 3))  # Wait before trying again

                # Eat for 1 to 3 seconds randomly
                eating_duration = random.uniform(1, 3)
                self.eating_time += eating_duration
                self.meals_count[self.id] += 1
                time.sleep(eating_duration)

                # Release forks
                self.waiter.release_forks(self.left_fork, self.right_fork)

    num_philosophers = PHILOSOPHERS
    waiter = Waiter(num_philosophers)
    meals_count = [0] * num_philosophers  # Track meals eaten philosophers

    # Create and start philosopher threads
    philosophers = []
    for i in range(num_philosophers):
        left_fork = i
        right_fork = (i + 1) % num_philosophers
        philosopher = Philosopher(i, waiter, left_fork, right_fork, meals_count)
        philosophers.append(philosopher)
        philosopher.start()

    # Wait for all philosophers to finish
    for philosopher in philosophers:
        philosopher.join()

    # Display results
    print("\nDining Summary:")
    for i, philosopher in enumerate(philosophers):
        print(
            f"Philosopher {i}: Ate {meals_count[i]} times, "
            f"Total Eating Time: {philosopher.eating_time:.2f}s, "
            f"Total Thinking Time: {philosopher.thinking_time:.2f}s"
        )


if __name__ == '__main__':
    main()
    create_signature_file("CSE251W25")
