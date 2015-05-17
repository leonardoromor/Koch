#!/usr/bin/env python
"""
This code generate a vectorial image of the Koch parametrization
Requires numpy package and imagemagick
"""

import numpy as np
import os

display_prog = 'display'

def colorstr(rgb): return "#%x%x%x" % (rgb[0]/16,rgb[1]/16,rgb[2]/16)


class Scene:
    """
    This class is a container to handle the scene.
    """
    def __init__(self,name="svg",height=768,width=1024):
        self.name = name
        self.items = []
        self.height = height
        self.width = width
        return

    def add(self,item): self.items.append(item)

    def add_figure(self, figure):
        for element in figure.structure:
            self.cart_mapper(element)
            self.items.append(element)

    def strarray(self):
        var = ["<?xml version=\"1.0\"?>\n",
               "<svg height=\"%d\" width=\"%d\" >\n" % (self.height,self.width),
               " <g style=\"fill-opacity:1.0; stroke:black;\n",
               "  stroke-width:1;\">\n"]
        for item in self.items: var += item.strarray()
        var += [" </g>\n</svg>\n"]
        return var

    def write_svg(self,filename=None):
        if filename:
            self.svgname = filename
        else:
            self.svgname = self.name + ".svg"
        file = open(self.svgname,'w')
        file.writelines(self.strarray())
        file.close()
        return

    def display(self,prog=display_prog):
        os.system("%s %s" % (prog,self.svgname))
        return


    def cart_mapper(self,element):
        element.start[0] = self.width/2 + element.start[0]*self.width/2
        #element.start[0] = (element.start[0] - 1) * self.width/2
        element.start[1] = self.height/2 - element.start[1] * self.height/2
        #element.start[1] = (element.start[1] - 1) * self.height/2

        element.end[0] = self.width/2 + element.end[0]*self.width/2
        #element.end[0] = (element.end[0] - 1) * self.width/2
        element.end[1] = self.height/2 - element.end[1] * self.height/2
        #element.end[1] = (element.end[1] - 1) * self.height/2


class Line:
    """
    Write a line in svg format
    """
    def __init__(self,start,end):
        self.start = start #xy list
        self.end = end     #xy list
        return

    def length(self):
        x2 = self.start[0]*self.start[0] +self.end[0]*self.end[0] - 2*self.start[0]*self.end[0]
        y2 = self.start[1]*self.start[1] +self.end[1]*self.end[1] - 2*self.start[1]*self.end[1]
        return np.sqrt(x2+y2)

    def lx(self):
        return self.end[0]-self.start[0]

    def ly(self):
        return self.end[1]-self.start[1]

    def strarray(self):
        return ["  <line x1=\"%d\" y1=\"%d\" x2=\"%d\" y2=\"%d\" />\n" %\
                (self.start[0],self.start[1],self.end[0],self.end[1])]



def gamma(line):
    """
    This function take a line ___ and return a list of lines _/\_
    """
    kblock = []
    l = line.length()
    piece = l / 4

    #First piece _
    kblock.append(Line(  [line.start[0] , line.start[1]]  ,  [line.start[0]+line.lx()/3 , (line.start[1]+line.ly()/3)]  ))

    #Second piece /
    point2x = line.start[0]+line.lx()*2/3
    point2y = line.start[1]+line.ly()*2/3
    newX = kblock[0].end[0] + (point2x-kblock[0].end[0])*0.5 - (point2y-kblock[0].end[1])*(np.sqrt(3)/2);
    newY = kblock[0].end[1] + (point2x-kblock[0].end[0])*(np.sqrt(3)/2) + (point2y-kblock[0].end[1])*0.5;

    kblock.append(Line(  [kblock[0].end[0] , kblock[0].end[1]]  ,  [newX , newY]  ))

    #Third piece \
    kblock.append(Line(  [kblock[1].end[0] , kblock[1].end[1]]  ,  [line.start[0]+line.lx()*2/3 , line.start[1]+line.ly()*2/3]  ))

    #Fourth piece _
    kblock.append(Line(  [kblock[2].end[0] , kblock[2].end[1]]  ,  [line.end[0] , line.end[1]]  ))

    return kblock


class Koch:
    def __init__(self):
        self.k = 0;
        self.structure = []
        self.structure.append(Line([-1,0],[1,0]))

    def update(self):
        """
        This function iterate over all the elements and apply the gamma function in each line
        """
        for i,item in enumerate(self.structure):
            self.structure[i] = gamma(item)

        #Flat the list from [[],[],[]] to [,,]
        self.structure = [val for sublist in self.structure for val in sublist]





#Init scene
scene = Scene('test')

#Init Koch
a = Koch()

#Number of updates
n = 3

for i in range(0,n):
    a.update()


scene.add_figure(a)
scene.write_svg()
scene.display()
