'''
Created on Dec 22, 2016

@author: safdar
'''
import numpy as np
import matplotlib.pyplot as plt

class Plotter(object):
    def __init__(self):
        self.__drawer__ = ImageDrawer()
        
    def nextframe(self):
        return Frame(self.__drawer__)
    
class ImageDrawer(object):
    def __init__(self):
        self.__counter__ = 0
    
    def redraw(self, sections):
        self.__counter__ += 1
        print(".", end='', flush=True)
        if self.__counter__ % 100 == 0:
            print ("{}".format(self.__counter__))
        

class PyPlotter(object):
    def __init__(self):
        self.__figure__ = None
        self.__axes__ = None
        self.__axes_images__ = None
        self.__counter__ = 0
        self.__figure_text__ = None
        
    def redraw(self, sections):
        # If there's only one section, split it into rows/cols:
        h,v = None, None
        if len(sections)==1:
            N = len(sections[0])
            if (N > 0):
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
        if not v is None and not h is None:
            if self.__figure__ == None:
                self.__figure__, _  = plt.subplots (v, h)
                if self.__figure_text__ is None:
                    self.__figure_text__ = self.__figure__.suptitle("", fontsize=14, fontweight='bold')
                self.__axes_images__ = []
                for i in range(v):
                    self.__axes_images__.append([])
                    for j in range(h):
                        if j >= len(sections[i]):
                            break # We've finished one section (horizontal plots). Goto next i.
    
                        (image, cmap, title, stats) = sections[i][j]
                        idx = (i*h) + j
                        axes = self.__figure__.get_axes()[idx]
                        font = min (max (int( 100 / (np.sqrt(len(title)) * v * h)), 7), 15)
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
                        idx = (i*h) + j
                        axes = self.__figure__.get_axes()[idx]
                        
                        (image, cmap, title, stats) = sections[i][j]
                        axesimage = self.__axes_images__[i][j]
    #                     axesimage.autoscale()
                        axesimage.set_data(image)
                        font = min (max (int( 100 / (np.sqrt(len(title)) * v * h)), 7), 15)
                        axes.set_title(title, fontsize=font)
                        # TODO:
                        # Update stats?
                plt.ion()
                self.__figure__.canvas.draw()
                plt.pause(0.00001)
        self.__figure_text__.set_text("Frame: {}".format(self.__counter__))
        self.__counter__ += 1
        print(".", end='', flush=True)
        if self.__counter__ % 100 == 0:
            print ("{}".format(self.__counter__))
    
# A Frame represents state that is to be reflected in the current
# pyplot frame. The actual plotting is performed by the Plotter
class Frame(object):
    def __init__(self, plotter):
        self.__plotter__ = plotter
        self.__sections__ = []
    
    def add(self, image, cmap, title, stats):
        assert len(self.__sections__)>0, "Must invoke newsection() first before calling add()"
        self.__sections__[-1].append((image.copy(), cmap, title, stats))
    
    def newsection(self, name):
        self.__sections__.append([])
    
    def render(self):
        self.__plotter__.redraw(self.__sections__)
