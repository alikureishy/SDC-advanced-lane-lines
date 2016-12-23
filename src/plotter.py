'''
Created on Dec 22, 2016

@author: safdar
'''
import numpy as np
import matplotlib.pyplot as plt

class Plotter(object):
    def __init__(self, realtime=True):
        self.__isrealtime__ = realtime
        self.__chains__
        raise "Not implemented"

    def register(self, chain):
        raise "Not implemented"

    def nextframe(self):
        raise "Not implemented"
    
# Each instance is for a new set of frames
class Plot(object):
    def __init__(self, params):
        raise "Not implemented"
    
    def render(self):
        raise "Not implemented"
    
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
    
    # Plot the result
    plots = []
    for i in range(x):
        for j in range(y):
            idx = (i*y) + j
            if idx >= N:
                break
            info = images[idx]
            plot = plt.subplot2grid((x,y),(i, j))
            plot.imshow(info[0], cmap=info[2])
            title = 'Image: {} ({})'.format(idx, info[1])
            font = min (max (int( 100 / (np.sqrt(len(title)) * N)), 10), 30)
            plot.set_title(title, fontsize=font)
            plot.set_xticks([])
            plot.set_yticks([])
            plots.append(plot)

#     plt.tight_layout()
    plt.show()