

from support import *
from classes import *

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
    graphic_sys=Graphic_IMG         #Graphic_TK or Graphic_IMG

    m=Maze2D(shape,res,padding,line_width,bg_color,ani_walls,ani_cells,start,end,draw_explore,show_text,graphic_sys)

    
    # ask()
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

main()
