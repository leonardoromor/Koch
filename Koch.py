#!/usr/bin/env python
"""
This code generate a vectorial image of the Koch parametrization
Requires numpy package and imagemagick
"""

import numpy as np
import os
import copy

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


def change_viewport(point,x1,x2,y1,y2,width,height):
    point[0] = (point[0]-x1)*(width)/(x2-x1)
    point[1] = (point[1]-y2)*(height)/(y1-y2)



def remap_figure(figure,x1,x2,y1,y2,width,height):
    for p in figure.points:
        change_viewport(p,x1,x2,y1,y2,width,height)

def cart_mapper(point, width, height, ptrasl = [0,0]):

    point[0] = width/2 + point[0] * width/2 +  ptrasl[0]
    point[1] = height/2 - point[1] * height/2 + ptrasl[1]

def p_sum(p1,p2):
    return [p1[0]+p2[0],p1[1]+p2[1]]

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

        svgp += "   \" style=\"fill:none;stroke:black;stroke-width:0.2\" />"

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
        self.structure.add([0,0])
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





class function:

    def __init__(self,func):
        self.f = func


    def s_to_point(self,s):

        return self.f(s)

    def to_PLine(self, points):
        poly = PLine()

        for i in np.linspace(0, 1, num=points):
            poly.add(self.s_to_point(i))
        return poly


class Composition:

    def __init__(self,koch , func, refinement=10000):
        self.structure = PLine()
        for i in np.linspace(0, 1, num=refinement):
            newp = p_sum(koch.s_to_point(i),func.s_to_point(i))
            newp[0] = newp[0]
            newp[1] = newp[1]
            self.structure.add(newp)




def quadrato(s):
    return [s,s*s]

def radice(s):
    return [s,np.sqrt(s)]

def retta5(s):
    return [s,5*s]

def retta10(s):
    return [s,10*s]

def seno(s):
    return [s,np.sin(2*np.pi*s)]

def test1(s):
    return [s,5*np.sqrt(s)]

#Init Koch
a = Koch()
#Number of updates
n = 6

for i in range(0,n):
    a.update()


################################################################################
#seno
################################################################################
w=900
h=768
scene0 = Scene('Seno',h,w)
f0 = function(seno)
atemp = copy.deepcopy(a)
func0 = f0.to_PLine(10000)
comp = Composition(atemp,f0)

x1=0
x2=2
y1=-1.5
y2=1.5

remap_figure(func0,x1,x2,y1,y2,w,h)
remap_figure(comp.structure,x1,x2,y1,y2,w,h)
remap_figure(atemp.structure,x1,x2,y1,y2,w,h)


scene0.add_pline(comp.structure)
scene0.write_svg(filename="Seno_unica.svg")
scene0.add_pline(func0)
scene0.add_pline(atemp.structure)

scene0.write_svg()
#scene0.display()

################################################################################
#quadrato
################################################################################
w=1000
h=500
scene1 = Scene('Quadrato',h,w)
f1 = function(quadrato)
atemp = copy.deepcopy(a)
func1 = f1.to_PLine(10000)
comp = Composition(atemp,f1)

x1=0
x2=2
y1=0
y2=1

remap_figure(func1,x1,x2,y1,y2,w,h)
remap_figure(comp.structure,x1,x2,y1,y2,w,h)
remap_figure(atemp.structure,x1,x2,y1,y2,w,h)


scene1.add_pline(comp.structure)
scene1.write_svg(filename="Quadrato_unica.svg")
scene1.add_pline(func1)
scene1.add_pline(atemp.structure)

scene1.write_svg()
#scene1.display()

################################################################################
#radice
################################################################################
w=1000
h=750
scene2 = Scene('Radice',h,w)
f2 = function(radice)
atemp = copy.deepcopy(a)
func2 = f2.to_PLine(10000)
comp = Composition(atemp,f2)

x1=0
x2=2
y1=0
y2=1.5

remap_figure(func2,x1,x2,y1,y2,w,h)
remap_figure(comp.structure,x1,x2,y1,y2,w,h)
remap_figure(atemp.structure,x1,x2,y1,y2,w,h)


scene2.add_pline(comp.structure)
scene2.write_svg(filename="Radice_unica.svg")
scene2.add_pline(func2)
scene2.add_pline(atemp.structure)

scene2.write_svg()
#scene2.display()
################################################################################
#retta5
################################################################################
w=600
h=800
scene3 = Scene('Retta5',h,w)
f3 = function(retta5)
atemp = copy.deepcopy(a)
func3 = f3.to_PLine(10000)
comp = Composition(atemp,f3)

x1=0
x2=3
y1=0
y2=5

remap_figure(func3,x1,x2,y1,y2,w,h)
remap_figure(comp.structure,x1,x2,y1,y2,w,h)
remap_figure(atemp.structure,x1,x2,y1,y2,w,h)


scene3.add_pline(comp.structure)
scene3.write_svg(filename="Retta5_unica.svg")
scene3.add_pline(func3)
scene3.add_pline(atemp.structure)

scene3.write_svg()
#scene3.display()
################################################################################
#retta10
################################################################################
w=600
h=800
scene4 = Scene('Retta10',h,w)
f4 = function(retta10)
atemp = copy.deepcopy(a)
func4 = f4.to_PLine(10000)
comp = Composition(atemp,f4)

x1=0
x2=5
y1=0
y2=10

remap_figure(func4,x1,x2,y1,y2,w,h)
remap_figure(comp.structure,x1,x2,y1,y2,w,h)
remap_figure(atemp.structure,x1,x2,y1,y2,w,h)


scene4.add_pline(comp.structure)
scene4.write_svg(filename="Retta10_unica.svg")
scene4.add_pline(func4)
scene4.add_pline(atemp.structure)

scene4.write_svg()
#scene4.display()

################################################################################
#test1
################################################################################
w=600
h=800
scene5 = Scene('Test1',h,w)
f5 = function(test1)
atemp = copy.deepcopy(a)
func5 = f5.to_PLine(10000)
comp = Composition(atemp,f5)

x1=0
x2=2.5
y1=0
y2=5

remap_figure(func5,x1,x2,y1,y2,w,h)
remap_figure(comp.structure,x1,x2,y1,y2,w,h)
remap_figure(atemp.structure,x1,x2,y1,y2,w,h)


scene5.add_pline(comp.structure)
scene5.write_svg(filename="Test1_unica.svg")
scene5.add_pline(func5)
scene5.add_pline(atemp.structure)

scene5.write_svg()
scene5.display()
