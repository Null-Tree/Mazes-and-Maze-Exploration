from support import *

import numpy as np
import tkinter as tk
import time
from matplotlib import colors
import random
from dataclasses import dataclass
import math
import os

from PIL import Image,ImageDraw, ImageFont, ImageOps,ImageTk #Pillow library

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

def tuple_append(tup,v,i=False):
    l=list(tup)
    if i :
        l.insert(i,v)
    else:
        l.append(v)
    return tuple(l)

def manhatten_dist(cord1:Cord,cord2:Cord):
    """returns manhatten dist"""
    d=cord1-cord2
    return (abs(d.x)+abs(d.y))

def euclid_dist(cord1:Cord,cord2:Cord):
    """returns euclid dist"""
    d=cord1-cord2
    return math.sqrt(abs(d.x**2)+abs(d.y**2))

class Walls2D:
    def __init__(self,cells:np.ndarray):
        """creates the wallsystem"""
        self.mcells=cells
        self.reset_walls()

                
    def reset_walls(self):
        """resets walls to a blank slates, with only walls on the very outside box"""
        shape=self.mcells.shape
        lr_border=np.ones((shape[0],1))
        ud_border=np.ones((1,shape[1]))

        self.vert_walls=np.concatenate([lr_border,np.zeros((shape[0],shape[1]-1)),lr_border],axis=1)
        self.hori_walls=np.concatenate([ud_border,np.zeros((shape[0]-1,shape[1])),ud_border],axis=0)
        # puts togethor wall matrix with edges having walls

        # if cell is not valid, create walls in all directions
        for rcord, v in np.ndenumerate(self.mcells):
            if v ==0: #if cell is not valid, create walls in all dir
                i1,i2=rcord
                self.vert_walls[i1,i2]=1
                self.vert_walls[i1+1,i2]=1
                self.hori_walls[i1,i2]=1
                self.hori_walls[i1,i2+1]=1
    
    def get_cell_walls(self,cord:Cord):
        """obtains all walls surrounding a cell"""
        c=cord
        wl=[]
        if self.vert_walls[c.i1,c.i2]:
            wl.append("l")
        if self.vert_walls[c.i1,c.i2+1]:
            wl.append("r")
        if self.hori_walls[c.i1,c.i2]:
            wl.append("u")
        if self.hori_walls[c.i1+1,c.i2]:
            wl.append("d")
        return wl

    def invert_walls(self):
        """invert all wall states, eg if wall-> no wall"""
        for wall in [self.hori_walls,self.vert_walls]:
            for ric,v in np.ndenumerate(wall):
                wall[ric]=1-v  

    def populate_all_walls(self):
        """makes a wall in every possible spot"""
        self.hori_walls=np.ones(self.hori_walls.shape)
        self.vert_walls=np.ones(self.vert_walls.shape)
    
    def edit_wall_between(self,c1:Cord,c2:Cord,v=1):
        """changes the wall state between 2 cell cords"""
        d=c1-c2

        if d.x and d.y:
            raise Exception("trying to create diagonal wall")
        c_wall=Cord((max(c1.x,c2.x),max(c1.y,c2.y)),"xy")
        if d.x:
            self.vert_walls[c_wall.i_tup]=v
        if d.y:
            self.hori_walls[c_wall.i_tup]=v

class Maze2D:
    def __init__(self,xyshape,res=10,padding=30,line_width=1,bg="grey",ani_walls=False,ani_cells=False,start=None,end=None,draw_explore=True,show_text=True):
        """
        initalises a maze system
        
        Args:
            xyshape (tuple): (x,y) maze will be x by y cells
            res (int): pixel resolution for every cell of a maze
            padding (int): pixel padding around the entire maze
            line_width (int): pixel width of maze wall lines
            bg (str): color of background
            ani_walls (bool): do you want the creation of walls to be animated
            ani_cells (bool): do you want the animation of maze exploration animated
            start (Cord): the cord for start of the maze  -> will default to random cord
            end (Cord): the end of the maze -> will default to random cord
            draw_explore: (bool): draw the highlighting for maze exploration of maze explore algorithm
            show_text (bool): choose if text label showing loading and algorithm performance information will be displayed
        
        """
        
        dtype="i1"
        # true if cell is a valid space, false if that space is filled
        # ndim=len(shape)
        ishape=xyshape[::-1]
        self.cells=np.ones(ishape,dtype)
        self.walls=Walls2D(self.cells)
        self.graphic=Graphic(self,res,padding,line_width,bg,ani_walls,ani_cells,show_text)
        self.navigation=Navigation(self,start,end,draw_explore)
    
    def get_rand_cord(self):
        return Cord(( rand_index(self.cells.shape[0]) , rand_index(self.cells.shape[0]) ))

class Graphic:
    def __init__(self,maze:Maze2D,res=10,padding=30,line_width=1,bg="grey",ani_walls=False,ani_cells=False,show_text=True):
        """creates the graphic system"""
        self.prev_t=time.time()
        self.maze=maze
        self.res=res
        self.padding=padding

        self.root = tk.Tk()
        self.root.title("Maze System by NullTree")
        self.root.configure(bg=bg)

        self.lines_of_text=6
        self.font_size=14
        self.show_text=show_text

        xdim,ydim=maze.cells.shape[::-1]
        self.bg=bg
        
        self.canvas_width=xdim*res+2*padding
        self.canvas_height=ydim * res+2*padding
        self.bg_rgb=self.get_rgb(self.bg)
        

        # color=self.bg_rgb
        self.image = Image.new(mode="RGB",size=(self.canvas_width,self.canvas_height,),color=self.bg_rgb)
        self.image_path='py_temporary/mazetemp.png'
        # self.save_image()
        self.photoImage_obj =ImageTk.PhotoImage(self.image)# tk.PhotoImage(self.image)
        

        print(type(self.photoImage_obj))     
        self.image_display=tk.Label(self.root, image=self.photoImage_obj)
        self.image_display.pack()
        

        if show_text:
            self.root.geometry(f"{self.canvas_width}x{self.canvas_height+self.lines_of_text*self.font_size}")
            # self.root.geometry(f"{canvas_width}x{canvas_height+padding*2+self.lines_of_text*self.font_size}")
            self.text_str_var=tk.StringVar()
            self.text_list=[]
            
            self.label=tk.Label(self.root,textvariable=self.text_str_var)
            self.label.config(font =("Courier", self.font_size))
            self.label.pack()
            self.label.config(bg=bg)
        
        

        self.linewidth=line_width
        self.animate={"walls":bool(ani_walls),"cells":bool(ani_cells)}

        self.cell_g_id_len=2

    def get_rgb(self,string:str):
        t=colors.to_rgb(string)

        return tuple([int(v*255) for v in t])
    
    
        

        



    # def open_image(self):
    
    def save_image(self):
        self.image.save(self.image_path)

    def refresh(self,force=False):
        self.prev_t
        self.t=time.time()
        d=self.t-self.prev_t

        self.fps=50
        # print(d)
        if force or d >1/self.fps:
            self.prev_t=self.t
            self.photoImage_obj =ImageTk.PhotoImage(self.image)
            self.image_display.config(image=self.photoImage_obj)
            self.root.update()


    def log(self,*args,end="\n"):
        print(*args)
        
        if not self.show_text:
            return
        newline=""
        for a in args:
            newline+=str(a)
        self.text_list.append(newline)
            
        s="\n".join(self.text_list)
        self.text_str_var.set(s)
    
    def remove_log(self,i=-1):
        if not self.show_text:
            return
        self.text_list.pop(i)
        s="\n".join(self.text_list)
        self.text_str_var.set(s)


    def get_pixel_xy(self,cord:Cord):
        """gets onscreen pixel tuple pf any in maze Cord"""
        c=cord
        return (int(c.x * self.res + self.padding), int(c.y*self.res+self.padding))
    
    def draw_line(self,cord1:Cord,cord2:Cord,color="black",width:int=None):
        """draws a line between cordinates"""
        if not width:
            width=self.linewidth
        
        draw = ImageDraw.Draw(self.image)
        xy_t0=self.get_pixel_xy(cord1)
        xy_t1=self.get_pixel_xy(cord2)
        # print([xy_t0,xy_t1],width,self.get_rgb(color))
        width=int(width)
        draw.line([xy_t0,xy_t1],width=width,fill=self.get_rgb(color))
        # self.save_image()
    
        
    def draw_wall(self,cord:Cord,w_side):
        """draws a wall"""
        draw = ImageDraw.Draw(self.image)


        res=self.res

        x,y=self.get_pixel_xy(cord)
        # this is top left of the cell
        adj=self.linewidth//2
        x0=x
        y0=y
        x1=x+res
        y1=y+res

        rgb=(0,0,0)

        if w_side == "r":            
            # canvas.create_line(x1,y0-adj,x1,y1+adj,width=self.linewidth)
            draw.line([(x1,y0-adj),(x1,y1+adj)],fill=rgb,width=self.linewidth)
        elif w_side == "l":
            # canvas.create_line(x0,y0-adj,x0,y1+adj,width=self.linewidth)
            draw.line([(x0,y0-adj),(x0,y1+adj)],fill=rgb,width=self.linewidth)
        elif w_side == "u":
            # canvas.create_line(x0-adj,y0,x1+adj,y0,width=self.linewidth)
            draw.line([(x0-adj,y0),(x1+adj,y0)],fill=rgb,width=self.linewidth)
        elif w_side == "d":
            # canvas.create_line(x0-adj,y1,x1+adj,y1,width=self.linewidth)
            draw.line([(x0-adj,y1),(x1+adj,y1)],fill=rgb,width=self.linewidth)













        # if w_side == "r":  
        #     self.draw_line(topleft,topleft+Cord.down())
        # elif w_side == "l":
        #     self.draw_line(topleft+Cord.right(),topleft+Cord.right()+Cord.down())
        # elif w_side == "u":
        #     self.draw_line(topleft,topleft+Cord.right())
        # elif w_side == "d":
        #     self.draw_line(topleft+Cord.down(),topleft+Cord.right()+Cord.down())

    def draw_cell_walls(self,cord:Cord):
        """draws allwalls for a given cell"""
        wall_l=self.maze.walls.get_cell_walls(cord)
        for w_side in wall_l:
            self.draw_wall(cord,w_side)

            # animate
            # print(self.animate["walls"])
            if self.animate["walls"]:
                self.refresh()
    

            
    def draw_on_cell(self,cord:Cord,shape="square",fill="light blue",prop=.8,outline=True,rpad=None,clearing=False):
        """draws a shape in a cell"""
        if not clearing:
            self.clear_cell(cord)

        c=cord
        p=(1-prop)/2
        # tl=Cord((c.i1+p,c.i2+p)) 
        # br=Cord((c.i1-p+1,c.i2-p+1))
        # print(tl,br)
        tl=c+Cord((p,p)) 
        br=c-Cord((p,p))   +Cord((1,1))
        # print(tl,br)
        # print()
        x0,y0=self.get_pixel_xy(tl)
        x1,y1=self.get_pixel_xy(br)
        if rpad==None:
            rpad=self.linewidth//2+2
        x0+=rpad
        y0+=rpad
        x1-=rpad
        y1-=rpad

        xy_tl=[(x0,y0),(x1,y1)]

        width=self.linewidth if outline else 0 
        draw = ImageDraw.Draw(self.image)
        g_id_l=[]
        if shape=="square":
            # g_id_l.append(self.canvas.create_rectangle(x0,y0,x1,y1,fill=fill,width=width))
            draw.rectangle(xy_tl,fill=fill,width=width)
            
        if shape=="cross":
            # g_id_l.append(self.canvas.create_line(x0,y0,x1,y1,width=self.linewidth))
            # g_id_l.append(self.canvas.create_line(x1,y0,x0,y1,width=self.linewidth))
            draw.line(xy_tl,fill=fill,width=width)
            draw.line([(x1,y0),(x0,y1)],fill=fill,width=width)
            
        if shape=="circle":
            # draw.circle()
            c=((x0+x1)//2,(y0+y1)//2)
            r=x1-x0
            draw.circle(c,radius=r,fill=fill,width=width)


        if self.animate["cells"]:
            self.refresh()
        




    def clear_cell(self,cord):
        """clear cell graphic for given cell"""
        self.draw_on_cell(cord,fill=self.bg,prop=1,clearing=True)

    
    def clear_all(self):
        """reset image"""
        draw=ImageDraw.Draw(self.image)
        draw.rectangle([(0,0), self.image.size], fill=self.bg_rgb)
        
    def reset_maze(self):
        self.clear_all()
        self.render_maze()

    def render_maze(self):
        """renders the maze walls"""
        for rcord, v in np.ndenumerate(self.maze.cells):
            if v:
                self.draw_cell_walls(Cord(rcord))
            else:
                # draw it with solid fill cause invalid space
                self.draw_on_cell(Cord(rcord),fill="black",prop=1,rpad=0)
        self.refresh(force=True)

    

    def start(self):
        """start the tk item"""
        self.root.mainloop()
    


class Navigation:
    def __init__(self,maze:Maze2D,start:Cord=None,end:Cord=None,draw_explore=True):
        """create navigation item"""
        self.shape=maze.cells.shape
        if start==None:
            start = maze.get_rand_cord()
        if end==None:
            end=maze.get_rand_cord()
            while (end == start):
                end=maze.get_rand_cord()
        
        self.maze=maze
        self.start=start
        self.end=end

        # 0 for invalid place, 1 for empty, 2 for traversed, 3 for start, 4 for end, 5 and 6 for planned(to be used by pathing)
        self.path_reset()

        self.draw_explore=draw_explore

        # print(start.x,start.y)
        # print(end.i_tup)

        self.draw_start_end()
        # print("making start end")
    
    # not useful
    # def pathCellM_copy(self):
    #     pc_copy=self.maze.cells.copy()
    #     pc_copy[self.start.i_tup]=3
    #     pc_copy[self.end.i_tup]=4      
    #     return pc_copy

    

    def path_reset(self):
        """reset path tracking amtrix"""
        self.path_cells=self.maze.cells.copy()
        self.path_cells[self.start.i_tup]=3
        self.path_cells[self.end.i_tup]=4
    
    def draw_start_end(self):
        """draws the start and end of maze onto graph"""
        self.maze.graphic.draw_on_cell(self.start,"circle","red",prop=.9)
        self.maze.graphic.draw_on_cell(self.end,"circle","green",prop=.9) 
        self.maze.graphic.refresh(force=True)
    
    def mark_as_explored(self,cord:Cord,color):
        """mark a cell as explored in path matrix and highlights it as marked"""
        
        for c in [self.start,self.end]:
            if cord ==c:
                draw_explore=False

        # if self.path_cells[cord.i_tup]==0:
        #     self.path_cells[cord.i_tup]=2
        
        self.path_cells[cord.i_tup]=2

        if self.draw_explore:
            self.maze.graphic.draw_on_cell(cord,fill=color,prop=.85,outline=False,rpad=1)

        return self.path_cells[cord.i_tup]

    def cord_is_inbounds(self,cord:Cord):
        """check if a cordinate is inbounds of the maze"""
        if cord.i1 >=0 and cord.i1 <= self.shape[0]-1:
            if cord.i2 >=0 and cord.i2 <= self.shape[1]-1:
                return True
        return False
    
    def wall_blocked(self,cord1:Cord,cord2:Cord):
        """checks if there is a wall between 2 adj cells"""
        d=cord1-cord2
        if d.x and d.y:
            raise Exception("diagonal wall check not supported")
        
        # if we are checking [] []
        if d.x:
            return self.maze.walls.vert_walls[Cord((max(cord1.x,cord2.x),cord1.y),"xy").i_tup]==1
        if d.y:
            return self.maze.walls.hori_walls[Cord((cord1.x,max(cord1.y,cord2.y)),"xy").i_tup]==1

    def get_unvisited_neighbours(self,cord:Cord,planning_n=5):
        """obtains all unvisited neighbours of a given cell, by defailt will not include any cell planned"""
        n_l=[]

        # if new cord in bounds, if it isnt restricted by a wall, and is currently valid, unvisited and unplanned
        tcl=[cord.left(),cord.right(),cord.up(),cord.down()]
        for tc in tcl:
            if self.cord_is_inbounds(tc) and not (self.wall_blocked(cord,tc)) and self.path_cells[tc.i_tup] not in [0,2,planning_n] and self.maze.cells[tc.i_tup]:
                n_l.append(tc)
        

        return n_l
    
    def draw_explore_path(self,c1,c2,linecolor,width:int,override=False):
        """draws path between 2 maze cells"""
        if self.draw_explore or override:
            self.maze.graphic.draw_line(c1+Cord((0.5,0.5)),c2+Cord((0.5,0.5)),linecolor,width=width)
    
    def DFS_wallmaker(self,render=True):
        """creates and renders the maze using dfs"""
        self.path_reset()

        self.maze.walls.reset_walls()
        
        linewidth=int(self.maze.graphic.res*.3)
        linecolor="#8fe493"

        prev_cell_M=np.zeros(tuple_append(self.shape,2),dtype=int)
        # has_prev_M=np.zeros(self.shape,dtype=int)
        # current=

        stack=[self.start]
        self.maze.graphic.log("Running DFS maze maker")
        
        while len(stack)>0:
            # current=stack.pop(rand_index(len(stack)))
            current=stack.pop(-1)

            # print(current,[str(v) for v in stack])
            neighbours=self.get_unvisited_neighbours(current,planning_n=None)
            random.shuffle(neighbours)
            for next in neighbours:
                
                # if not planned, not visited and not invaluid
                prev_cell_M[next.i_tup][:] = current.i1,current.i2
                # has_prev_M[next.i_tup]=1
                self.path_cells[next.i_tup]=5
                stack.append(next)
                    
            self.mark_as_explored(current,color=linecolor)
            
            # all visited nodes will have prev, except for start
            if not current == self.start:
                prev=Cord(prev_cell_M[current.i_tup][:])
                self.draw_explore_path(current,prev,linecolor,linewidth)
            
        self.draw_start_end()

        # pop all walls
        self.maze.walls.populate_all_walls()
        
        # removes walls if a path should exist between cords
        # print(self.maze.walls.hori_walls)
        for curr_r2ic,_ in np.ndenumerate(self.maze.cells):
            prev_r2ic=prev_cell_M[curr_r2ic]
            # all nodes apart frmo start will awyas have a rpev
            if Cord(curr_r2ic) != Cord(self.start.i_tup):
                c1=Cord(prev_r2ic)
                c2=Cord(curr_r2ic)
                # print(c1-c2)
                self.maze.walls.edit_wall_between(c1,c2,0)
        
        # i=input("next")
        if render:
            self.maze.graphic.render_maze()


        for curr_r2ic,_ in np.ndenumerate(self.maze.cells):
            prev_r2ic=prev_cell_M[curr_r2ic]
            # all nodes apart frmo start will awyas have a rpev
            if Cord(curr_r2ic) != Cord(self.start.i_tup):
                c1=Cord(prev_r2ic)
                c2=Cord(curr_r2ic)
                self.draw_explore_path(c1,c2,"red",linewidth,True)

        if render:
            self.maze.graphic.clear_all()
            self.maze.graphic.render_maze()
            self.draw_start_end()
        
        self.maze.graphic.remove_log()

    def Xfs(self,X:str="B"):
        """BFS or DFS, defaults to BFS"""
        self.path_reset()
        X=X.capitalize()
        if X=="B":
            takei=0
        elif X=="D":
            takei=-1
        else:
            raise Exception("invalid mode")
        linewidth=int(self.maze.graphic.res*.3)
        linecolor="#da96ac"
        
        prev_cell_M=np.zeros(tuple_append(self.shape,2),dtype=int)
        current=self.start
        
        l=[]
        found=False

        self.draw_start_end()
        n_it=0

        self.maze.graphic.log(f"Running {X.capitalize()}FS")
        # path find
        while not found:
            n_it+=1
            neighbours=self.get_unvisited_neighbours(current)
            for next in neighbours:
            
                # IF FOUND END REMOVE
                if self.path_cells[next.i_tup]==4:
                    self.draw_explore_path(next,current,linecolor,linewidth)
                    prev_cell_M[next.i_tup][:] = current.i1,current.i2
                    found=True
                    self.maze.graphic.log("Found End")
                    break
                
                
                # IF UN VISITED AND NOT PLANNED
                    
                prev_cell_M[next.i_tup][:] = current.i1,current.i2

                self.path_cells[next.i_tup]=5
                l.append(next)
                self.draw_explore_path(next,current,linecolor,linewidth)
                
            self.mark_as_explored(current,color=linecolor)
            
            if len(l)==0:
                self.maze.graphic.log("blocked off")
                return
            
            current=l.pop(takei)
            
        self.draw_start_end()
        dist=0
        # # back track
        current=self.end
        while current != self.start:
            prev=prev_cell_M[current.i_tup]
            prev=Cord(prev)
            # print(prev)
            self.draw_explore_path(prev,current,"red",linewidth,override=True)
            current=prev
            dist+=1
        
        for _ in range(2):
            self.maze.graphic.remove_log()
        self.maze.graphic.log(f"{X.capitalize()}FS dist: {dist}   after {n_it} steps")
        
        self.draw_start_end()


    def A_star(self,herustic_function=euclid_dist):
        """runs the A* pathing algorithm"""
        self.path_reset()
        linewidth=int(self.maze.graphic.res*.3)
        linecolor="#9688d8"
        
        prev_cell_M=np.zeros(tuple_append(self.shape,2),dtype=int)
        current=self.start
        
        pqueue=PriorityQueue()
        found=False

        self.draw_start_end()

        self.maze.graphic.log("Running A*")
        # path find
        n_it=0
        while not found:
            n_it+=1
            neighbours=self.get_unvisited_neighbours(current)
            for next in neighbours:
            
                # IF FOUND END REMOVE
                if self.path_cells[next.i_tup]==4:
                    self.draw_explore_path(next,current,linecolor,linewidth)
                    prev_cell_M[next.i_tup][:] = current.i1,current.i2
                    found=True
                    self.maze.graphic.log("Found End")
                    break
                
                
                # IF UN VISITED AND NOT PLANNED
                
                prev_cell_M[next.i_tup][:] = current.i1,current.i2

                self.path_cells[next.i_tup]=5

                # ultra greed
                herustic_dist_total=herustic_function(next,self.end)
                # guarentee correct but at this point jstu slightly better bfs
                # herustic_dist_total=manhatten_dist(next,self.end)+manhatten_dist(next,self.start)
                
                pqueue.pq_add(next,herustic_dist_total)
                self.draw_explore_path(next,current,linecolor,linewidth)
                
            self.mark_as_explored(current,color=linecolor)
            
            if (len(pqueue)==0):
                self.maze.graphic.log("blocked off")
                return
            
            current=pqueue.pq_get()
            # print(current)
            
        self.draw_start_end()
        # # back track
        current=self.end

        dist=0
        while current != self.start:
            prev=prev_cell_M[current.i_tup]
            prev=Cord(prev)
            # print(prev)
            self.draw_explore_path(prev,current,"#4627d1",linewidth,override=True)
            current=prev
            dist+=1
        for _ in range(2):
            self.maze.graphic.remove_log()
        self.maze.graphic.log(f"A* dist: {dist}  after {n_it} steps")
        self.draw_start_end()
    
    
    def double_A_star(self,herustic_function=euclid_dist):
        """runs A* algo from both ends of the graph"""
        self.path_reset()
        linewidth=self.maze.graphic.res*.3
        
        linecolor_l=["#71a3c1","#4f6979"]
        
        
        prev_cell_M_l=[np.zeros(tuple_append(self.shape,2),dtype=int),np.zeros(tuple_append(self.shape,2),dtype=int)]
        
        part_start_l=[self.start,self.end]
        current_l=part_start_l.copy()
        
        pqueue_l=[PriorityQueue(),PriorityQueue()]
        found=False

        self.draw_start_end()

        # meeting_point

        # path find
        n_it=0
        self.maze.graphic.log("Running Double A*")
        while not found:
            
            
            for side in [0,1]:
                n_it+=1
                my_pn=5+side
                other_pn=6-side
                current=current_l[side]
                neighbours=self.get_unvisited_neighbours(current,my_pn)
                
                linecolor=linecolor_l[side]
                for next in neighbours:
                
                    # IF FOUND END REMOVE
                    if self.path_cells[next.i_tup] == other_pn:
                        
                        self.draw_explore_path(next,current,linecolor,linewidth)
                        prev_cell_M_l[side][next.i_tup][:] = current.i1,current.i2
                        found=True
                        meeting_point=next
                        self.maze.graphic.draw_on_cell(next,"circle","orange")
                        self.maze.graphic.log("Found End")
                        break
                    
                    
                    # IF UN VISITED AND NOT PLANNED
                        
                    prev_cell_M_l[side][next.i_tup][:] = current.i1,current.i2

                    self.path_cells[next.i_tup]=my_pn
                    
                    herustic_dist_total=herustic_function(next,part_start_l[1-side]) 
                    
                    pqueue_l[side].pq_add(next,herustic_dist_total)
                    self.draw_explore_path(next,current,linecolor,linewidth)                
                self.mark_as_explored(current,color=linecolor_l[side])
                
                if (len(pqueue_l[side])==0):
                    self.maze.graphic.log("blocked off")
                    return
                
                current_l[side]=pqueue_l[side].pq_get()
            else:
                continue

            break
            # print(current)
            
        self.draw_start_end()
        # # back track
        dist=0
        for side in [0,1]:
            current=meeting_point
            # for i in range(99):
            while current != part_start_l[side]:
                prev=prev_cell_M_l[side][current.i_tup]
                prev=Cord(prev)
                # print(current,prev)
                self.draw_explore_path(prev,current,"blue",linewidth,override=True)
                current=prev
                dist+=1
        for _ in range(2):
            self.maze.graphic.remove_log()
        self.maze.graphic.log(f"Double A* dist: {dist}  after {n_it} steps")
            
        self.draw_start_end()
        self.maze.graphic.refresh(force=True)

















# ####################################################

def main():

    # this doesnt even work on this
    # seed=random.randint(0,9999)
    # random.seed=seed
    # print("seed=",random.seed)

    shape=(120,60)
    res=10
    padding=30
    line_width=1
    bg_color="grey"
    ani_walls=False
    ani_cells=True
    start=Cord((2,2))
    end=Cord(shape,"xy")-Cord((3,3))
    draw_explore=True
    show_text=True

    m=Maze2D(shape,res,padding,line_width,bg_color,ani_walls,ani_cells,start,end,draw_explore,show_text)

    
    ask()
    m.graphic.render_maze()
    

    # create walls
    
    m.navigation.DFS_wallmaker()
    # ask()
    time.sleep(3)
    
    
    # runs bfs
    m.graphic.reset_maze()
    m.navigation.Xfs("B")
    # ask()
    time.sleep(3)

    # runs A*
    m.graphic.reset_maze()
    m.graphic.render_maze()
    m.navigation.A_star()
    # ask()
    time.sleep(3)
    
    # runs double A*
    m.graphic.reset_maze()
    m.graphic.render_maze()
    m.navigation.double_A_star()
    



    m.graphic.start()

if __name__=="__main__":
    main()

