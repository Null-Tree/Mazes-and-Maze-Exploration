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