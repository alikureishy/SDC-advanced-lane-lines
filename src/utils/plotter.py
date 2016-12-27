'''
Created on Dec 22, 2016

@author: safdar
'''
import numpy as np
import matplotlib.pyplot as plt

class Plotter(object):
    def __init__(self):
        self.__figure__ = None
        self.__axes__ = None
        self.__axes_images__ = None
        self.__framecount__ = 0
        
    def nextframe(self):
        return Frame(self)
    
    def redraw(self, sections):
        # If there's only one section, split it into rows/cols:
        h,v = None, None
        if len(sections)==1:
            N = len(sections[0])
            h=int(round(np.sqrt(N)))
            v=int(np.ceil(N/h))
            diff = (h*v) - N
            sample = sections[0][0][0]
            for _ in range(diff):
                sections[0].append((np.zeros_like(sample), None, "--Blank--", None))
            sections = np.reshape(np.array(sections), (v,h,4))
        else:
            _, maxsection = max(enumerate(sections), key = lambda tup: len(tup[1]))
            h = len(maxsection)
            v = len(sections)

        # Plot:
        if self.__figure__ == None:
            self.__figure__, _  = plt.subplots (v, h)
            self.__axes_images__ = []
            for i in range(v):
                self.__axes_images__.append([])
                for j in range(h):
                    if j >= len(sections[i]):
                        break # We've finished one section (horizontal plots). Goto next i.

                    (image, cmap, title, stats) = sections[i][j]
                    idx = (i*h) + j
                    axes = self.__figure__.get_axes()[idx]
                    font = min (max (int( 100 / (np.sqrt(len(title)) * v * h)), 10), 30)
                    axes.set_title(title, fontsize=font)
                    axes.set_xticks([])
                    axes.set_yticks([])
                    
                    #TODO: Show stats?
                    axesimage = axes.imshow(image, cmap=cmap)
                    self.__axes_images__[i].append(axesimage)
            plt.ion()
            plt.show()
        else:
            for i in range(v):
                for j in range(h):
                    if j >= len(sections[i]):
                        break # We've finished one section (horizontal plots). Goto next i.
                    
                    (image, cmap, title, stats) = sections[i][j]
                    axesimage = self.__axes_images__[i][j]
#                     axesimage.autoscale()
                    axesimage.set_data(image)
                    # TODO:
                    # Update stats?
            self.__figure__.canvas.draw()
            plt.pause(0.00001)
            
        print ("Plotted frame: {}". format(self.__framecount__))
        self.__framecount__ += 1
    
# A Frame represents state that is to be reflected in the current
# pyplot frame. The actual plotting is performed by the Plotter
class Frame(object):
    def __init__(self, plotter):
        self.__plotter__ = plotter
        self.__sections__ = []
    
    def add(self, image, cmap, title, stats):
        assert len(self.__sections__)>0, "Must invoke newsection() first before calling add()"
        self.__sections__[-1].append((image, cmap, title, stats))
    
    def newsection(self, name):
        self.__sections__.append([])
    
    def render(self):
        self.__plotter__.redraw(self.__sections__)
