'''
Created on Dec 21, 2016

@author: safdar
'''
import matplotlib
# matplotlib.use('TKAgg')
matplotlib.use('TKAgg')
import matplotlib.image as mpimg
from matplotlib import pyplot as plt
import numpy as np
import cv2

# Import everything needed to edit/save/watch video clips

def process_thresholding (image):
    # Run the functions
#     image = dir_binary = dir_threshold(image, sobel_kernel=15, thresh=(0.7, 1.3))
#     image = grad_binary = abs_sobel_thresh(image, orient='x', thresh=(20, 100))
#     image = mag_binary = mag_thresh(image, sobel_kernel=3, mag_thresh=(30, 100))
#     image = r_binary = color_threshold(image, RGB.Red, (200, 255))
    
#     plot_multiple(*((image, "Original", None),\
#                   (grad_binary, "Gradient Threshold", 'gray'),\
#                   (mag_binary, "Magnitude Threshold", 'gray'),\
#                   (dir_binary, "Direction Threshold", 'gray'),\
#                   (r_binary, "Red Threshold", 'gray')))

    return image

# Workflow
# 2 utilities:
#    - Calibrator
#    - LaneFinder
#        - Individual image input
#        - Folder of images input
#        - Video input

if __name__ == '__main__':

#     image = mpimg.imread('test_images/solidWhiteRight.jpg')
#     image = dir_binary = dir_threshold(image, sobel_kernel=15, thresh=(0.7, 1.3))
#     image = grad_binary = abs_sobel_thresh(image, orient='x', thresh=(20, 100))
#     image = mag_binary = mag_thresh(image, sobel_kernel=3, mag_thresh=(30, 100))
#     image = r_binary = color_threshold(image, RGB.Red, (200, 255))
#     plot_multiple((image, "Title", 'gray'))
    
    input_file = '../challenge_video.mp4'
    cap = cv2.VideoCapture(input_file)
    i = 0
    while(cap.isOpened()):
        ret, image = cap.read()
        if not ret:
            break
#         image = dir_binary = dir_threshold(image, sobel_kernel=15, thresh=(0.7, 1.3))
        image = grad_binary = abs_sobel_thresh(image, orient='x', thresh=(20, 100))
    #     image = mag_binary = mag_thresh(image, sobel_kernel=3, mag_thresh=(30, 100))
#         image = r_binary = color_threshold(image, RGB.Red, (200, 255))
        print("{}: {}".format(i, (image==0).sum()))
        cv2.imshow ('frame', image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
#         plot_multiple((image, "Title", 'gray'))
        i+=1
         
    cap.release()
    cv2.destroyAllWindows()
    
#################

# List of (image, title, cmap) tuples
def plot_multiple(*images, shape=None):
    N = len(images)
    x,y = None, None
    if shape==None:
        x=int(round(np.sqrt(N)))
        y=int(np.ceil(N/x))
    else:
        x = shape[0]
        y = shape[1]
        assert x*y >= N, "Shape provided ({}) is too small to fit {} images".format(shape, N)
    
    # Frame the result
    plots = []
    for i in range(x):
        for j in range(y):
            idx = (i*y) + j
            if idx >= N:
                break
            info = images[idx]
            frame = plt.subplot2grid((x,y),(i, j))
            frame.imshow(info[0], cmap=info[2])
            title = 'Image: {} ({})'.format(idx, info[1])
            font = min (max (int( 100 / (np.sqrt(len(title)) * N)), 10), 30)
            frame.set_title(title, fontsize=font)
            frame.set_xticks([])
            frame.set_yticks([])
            plots.append(frame)

#     plt.tight_layout()
    plt.show()
    
    
def nothing():
    cols = ['Column {}'.format(col) for col in range(1, 4)]
    rows = ['Row {}'.format(row) for row in ['A', 'B', 'C', 'D']]
    
    fig, axes = plt.subplots(nrows=4, ncols=3, figsize=(12, 8))
    
    for ax, col in zip(axes[0], cols):
        ax.set_title(col)
    
    for ax, row in zip(axes[:,0], rows):
        ax.set_ylabel(row, rotation=0, size='large')
    
    fig.tight_layout()
    plt.show()
    
    
    #----
    
    import matplotlib.pyplot as plt
    import numpy as np
    
    images = np.random.uniform(0, 255, size=(40, 50, 50))
    
    fig, ax = plt.subplots()
    
    im = ax.imshow(images[0])
    fig.show()
    for image in images[1:]:
        im.set_data(image)
        fig.canvas.draw()