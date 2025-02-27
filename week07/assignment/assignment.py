'''
Requirements
1. Finish the team06 assignment (if necessary).
2. Change your program to process all 300 images using 1 CPU, then 2 CPUs, all the way up to the
   number of CPUs on your computer plus 4.
3. Keep track of the time it takes to process all 300 images per CPU.
4. Plot the time to process vs the number of CPUs.
5. COMMENT every line that you write yourself.
   
Questions:
1. What is the relationship between the time to process versus the number of CPUs?
   Does there appear to be an asymptote? If so, what do you think the asymptote is?
   >
   >
2. Is this a CPU bound or IO bound problem? Why?
   >
   >
3. Would threads work on this assignment? Why or why not? (guess if you need to) 
   >
   >
4. When you run "create_final_video.py", does it produce a video with the elephants
   inside of the screen?
   >
'''

from matplotlib.pylab import plt  # load plot library
from PIL import Image
import numpy as np
import timeit
import multiprocessing as mp
from cse251functions import *

# 4 more than the number of cpu's on your computer
CPU_COUNT = mp.cpu_count() + 4  

# TODO Your final video need to have 300 processed frames.  However, while you are 
# testing your code, set this much lower
FRAME_COUNT = 20

RED   = 0
GREEN = 1
BLUE  = 2


# def create_new_frame(image_file, green_file, process_file):
#     """ Creates a new image file from image_file and green_file """

#     # this print() statement is there to help see which frame is being processed
#     print(f'{process_file[-7:-4]}', end=',', flush=True)

#     image_img = Image.open(image_file)
#     green_img = Image.open(green_file)

#     # Make Numpy array
#     np_img = np.array(green_img)

#     # Mask pixels 
#     mask = (np_img[:, :, BLUE] < 120) & (np_img[:, :, GREEN] > 120) & (np_img[:, :, RED] < 120)

#     # Create mask image
#     mask_img = Image.fromarray((mask*255).astype(np.uint8))

#     image_new = Image.composite(image_img, green_img, mask_img)
#     image_new.save(process_file)

# Slightly changed create_new_frame() by only taking 1 arg and creating image files within the function
def create_new_frame(frame_number):
    image_file = rf'elephant/image{frame_number:03d}.png'
    green_file = rf'green/image{frame_number:03d}.png'
    process_file = rf'processed/image{frame_number:03d}.png'
    
    # this print() statement is there to help see which frame is being processed
    print(f'Processing frame {frame_number:03d}', end=',', flush=True)

    image_img = Image.open(image_file)
    green_img = Image.open(green_file)

    # Make Numpy Array
    np_img = np.array(green_img)

    # Mask pixels
    mask = (np_img[:, :, BLUE] < 120) & (np_img[:, :, GREEN] > 120) & (np_img[:, :, RED] < 120)

    # Create mask image   
    mask_img = Image.fromarray((mask * 255).astype(np.uint8))

    image_new = Image.composite(image_img, green_img, mask_img)
    image_new.save(process_file)


# TODO add any functions you need here
def process_frames_with_multiprocessing(cpu_count):
   #  Uses multiprocessing to process all frames in parallel
    start_time = timeit.default_timer()
    with mp.Pool(processes=cpu_count) as pool:
      #   Attempts to distribute frames across increasing amount of CPU cores with mp.pool
        pool.map(create_new_frame, range(1, FRAME_COUNT + 1))
    return timeit.default_timer() - start_time


if __name__ == '__main__':
    all_process_time = timeit.default_timer()

    # Use two lists: one to track the number of CPUs and the other to track
    # the time it takes to process the images given this number of CPUs.
    xaxis_cpus = []
    yaxis_times = []

    # process the 10th frame (TODO modify this to loop over all frames)

   # Test for efficiency in each CPU core
    for cpu_count in range(1, CPU_COUNT + 1):
        elapsed_time = process_frames_with_multiprocessing(cpu_count) # Keep track of time for plot
        print(f'\nTime with {cpu_count} CPUs = {elapsed_time} sec') # 20 total cores on my computer +4
        xaxis_cpus.append(cpu_count)
        yaxis_times.append(elapsed_time) 
        # I would have expected to put time on the x axis, but this works too

    print(f'Total Time for ALL processing: {timeit.default_timer() - all_process_time}')

    # create plot of results and also save it to a PNG file
    plt.plot(xaxis_cpus, yaxis_times, label=f'{FRAME_COUNT}')
    
    plt.title('CPU Core yaxis_times VS CPUs')
    plt.xlabel('CPU Cores')
    plt.ylabel('Seconds')
    plt.legend(loc='best')

    plt.tight_layout()
    plt.savefig(f'Plot for {FRAME_COUNT} frames.png')
    plt.show()
    
    create_signature_file("CSE251W25")
