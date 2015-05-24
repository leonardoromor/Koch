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

    def add_pline(self, figure):
        self.items.append(figure)

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



def remap_figure(figure):
    for p in figure.points:
        cart_mapper(p,1024,768)

def cart_mapper(point, width, height, ptrasl = [0,0]):

    point[0] = width/2 + point[0] * width/2 +  ptrasl[0]
    point[1] = height/2 - point[1] * height/2 + ptrasl[1]



class PLine:
    """
    Write a polygon line in svg format
    """
    def __init__(self):
        self.points = []
        return

    def add(self, p):
        self.points.append(p)

    def length(self):
        return len(self.points)

    def strarray(self):
        svgp = "<polyline points=\""

        for p in self.points:
            svgp += "   " + str(p[0]) + "," + str(p[1]) + "\n"

        svgp += "   \" style=\"fill:none;stroke:black;stroke-width:20%\" />"

        return svgp

class Line:
    """
    Define a line
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



def gamma(line):
    """
    This function take a line ___ and return a list of lines _/\_
    """
    kblock = []
    l = line.length()
    piece = l / 4

    #First piece _
    kblock.append( [line.start[0] , line.start[1]] )
    kblock.append( [line.start[0]+line.lx()/3 , (line.start[1]+line.ly()/3)])

    #Second piece /
    point2x = line.start[0]+line.lx()*2/3
    point2y = line.start[1]+line.ly()*2/3
    newX = kblock[1][0] + (point2x-kblock[1][0])*0.5 - (point2y-kblock[1][1])*(np.sqrt(3)/2);
    newY = kblock[1][1] + (point2x-kblock[1][0])*(np.sqrt(3)/2) + (point2y-kblock[1][1])*0.5;

    kblock.append([newX , newY])

    #Third piece \
    kblock.append( [line.start[0]+line.lx()*2/3 , line.start[1]+line.ly()*2/3] )

    #Fourth piece _
    kblock.append( [line.end[0] , line.end[1]] )

    return kblock


class Koch:
    def __init__(self):
        self.structure = PLine()
        self.structure.add([-1,0])
        self.structure.add([1,0])

    def update(self):
        """
        This function iterate over all the elements and apply the gamma function in each line
        """
        i = 0

        while i < len(self.structure.points):
            if(i == 0):
                start = self.structure.points[i]
                i += 1
            else:

                new  =  gamma(Line(start,self.structure.points[i]))

                self.structure.points.insert(i,new[1])
                self.structure.points.insert(i+1,new[2])
                self.structure.points.insert(i+2,new[3])
                start = self.structure.points[i+3]
                i = i+4

        #Flat the list from [[],[],[]] to [,,]
        #self.structure = [val for sublist in self.structure for val in sublist]

    def s_to_point(self,s):

        N = self.structure.length() - 1
        sstep = 1.0/N

        stimes = s / sstep
        stimes = int(stimes)
        slength = s - (sstep * stimes)
        ratio = 0
        a =  self.structure.points[stimes]
        if(np.fabs(slength) > 1e-10):
            b = self.structure.points[stimes+1]

            line = Line(a,b)

            ratio = slength /  line.length()

            return p_sum(a,[line.lx()*ratio,line.ly()*ratio])

        return a


def p_sum(p1,p2):
    return [p1[0]+p2[0],p1[1]+p2[1]]

class function:

    def __init__(self,func):
        self.f = func


    def s_to_point(self,s):

        return [s*2-1,self.f(2*np.pi*s)]




#Init scene
scene = Scene('test')

#Init Koch
a = Koch()

#Number of updates
n = 5

for i in range(0,n):
    a.update()

#Composition with a function
f = function(np.sin)
composition = PLine()

refinement = 1000
for i in np.linspace(0, 1, num=1000):
    newp = p_sum(a.s_to_point(i),f.s_to_point(i))
    newp[0] = newp[0]/2
    newp[1] = newp[1]/2
    composition.add(newp)

remap_figure(composition)
remap_figure(a.structure)
scene.add_pline(a.structure)
scene.add_pline(composition)
scene.write_svg()
scene.display()
