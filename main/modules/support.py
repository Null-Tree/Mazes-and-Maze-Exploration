import numpy as np
import tkinter as tk
import time
from matplotlib import colors
import random
from dataclasses import dataclass
import math
import os
from PIL import Image,ImageDraw, ImageFont, ImageOps,ImageTk #Pillow library

def pprint_2dArray(l,align='r'):
    """prettily prints any 2d array, breaks on multiline"""
    # for every col
    if type(l[0]) in [list,tuple,set]:
        for coli in range(len(l[0])):
            longest=0
            for rowi in range(len(l)):
                longest=max(longest,len(str(l[rowi][coli])))
            
            
            for rowi in range(len(l)):
                nspace=(longest-len(str(l[rowi][coli])))
                if align=='l':
                    l[rowi][coli]= str(l[rowi][coli])+(" "*nspace)
                elif align=='r':
                    l[rowi][coli]= (" "*nspace)+str(l[rowi][coli])
                elif align=='m':
                    n_lspace=nspace//2
                    n_rspace=nspace-n_lspace
                    l[rowi][coli]= (" "*n_lspace)+str(l[rowi][coli])+(" "*n_rspace)

                else:
                    raise Exception()
    

        for i in range(len(l)):
            for j in range(len(l[0])):
                print(l[i][j],end="  ")
            print()
    else:
        for i in range(len(l)):
            print(l[i],end="  ")
        print()



class PriorityQueue(list):
    """list of arrays [(item,priority)]"""
    def pq_add(self,item,p_val):
        self.append((item,p_val))
        
    def pq_get(self,mode="min"):
        self.sort(key=lambda x:x[1])
        
        if mode=="min":
            return self.pop(0)[0]
        if mode=="max":
            return self.pop(-1)[0]
        


def rand_index(len):
    return random.randint(0,len-1)

def ask(t="press enter in terminal to continue:"):
    """used to stagger actions"""
    i=input(t)
    print("continuing...\n")




class Cord:
    def __init__(self,tup,mode:str="i1i2"):
        """input cordinate as a tuple eg Cord((1,2),mode="xy")"""
        # needs mode cause matrix[i1][i2] is matrix[y][x]
        if len(tup)!=2:
            raise Exception("coerd len err")
        if mode=="i1i2":
            self.i1,self.i2=tup
            self.y,self.x=tup
        if mode=="xy":
            self.x,self.y=tup
            self.i2,self.i1=tup
        self.i_tup=(self.i1,self.i2)
        # print(self.i1,self.i2,self.x,self.y)
    
    def __add__(self,cord2):
        new=Cord((self.i1+cord2.i1,self.i2+cord2.i2))
        return new
    def __sub__(self,cord2):
        new=Cord((self.i1-cord2.i1,self.i2-cord2.i2))
        return new
    def __eq__(self,cord2):
        if type(cord2)!=Cord:
            return False
        if self.i1 == cord2.i1 and self.i2 == cord2.i2:
            return True
        return False 
    def  __neq__(self,c2):
        return not self==c2
    
    def up(self=None):
        if self==None:
            self=Cord((0,0))
        return self+Cord((0,1),"xy")
    
    def down(self=None):
        if self==None:
            self=Cord((0,0))
        return self+Cord((0,-1),"xy")
    
    def left(self=None):
        if self==None:
            self=Cord((0,0))
        return self+Cord((-1,0),"xy")
    
    def right(self=None):
        if self==None:
            self=Cord((0,0))
        return self+Cord((1,0),"xy")
    def __str__(self):
        return f"Cord({str(self.i_tup)})"
    
    def __mul__(self,k):
        return Cord((int(self.i1*k),int(self.i2*k)))
    
    def __truediv__(self,k):
        return Cord((int(self.i1/k),int(self.i2/k)))


def manhatten_dist(cord1:Cord,cord2:Cord):
    """returns manhatten dist"""
    d=cord1-cord2
    return (abs(d.x)+abs(d.y))

def euclid_dist(cord1:Cord,cord2:Cord):
    """returns euclid dist"""
    d=cord1-cord2
    return math.sqrt(abs(d.x**2)+abs(d.y**2))

def tuple_append(tup,v,i=False):
    l=list(tup)
    if i :
        l.insert(i,v)
    else:
        l.append(v)
    return tuple(l)



def np_arr(shape,val=None,datatype="i"):
    arr=np.zeros(shape,dtype=datatype)
    for rc,v in np.ndenumerate(arr):
        arr[rc]=val
    return arr

def np_circle(shape,dtype,center:Cord,r,inside=1,outside=0):
    arr=np.zeros(shape,dtype=dtype)
    for rc,v in np.ndenumerate(arr):
        if euclid_dist(center,Cord(rc)) < r:
            arr[rc]=inside
        else:
            arr[rc]=outside
    return arr

def counter_file(filePath,n = None):
    if not n:                      # If not provided return file content
        with open(filePath, "r") as f:
            n = int(f.read())
            return n
    else:
        with open(filePath, "r") as f:
            n = int(f.read())
        with  open(filePath, "a") as f:# Create a blank file
            f.seek(0)  # sets  point at the beginning of the file
            f.truncate()  # Clear previous content
            f.write(f"{n+1}") # Write file
            return n+1