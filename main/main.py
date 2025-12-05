

from modules.support import *
from modules.classes import *

def main():

    # this doesnt even work on this
    # seed=random.randint(0,9999)
    # random.seed=seed
    # print("seed=",random.seed)

    xyshape=(120,80)
    res=10
    padding=30
    line_width=1
    bg_color="grey"
    ani_walls=False
    ani_cells=True
    start=None
    end=None
    draw_explore=True
    show_text=True
    graphic_sys=Graphic_IMG         #Graphic_TK or Graphic_IMG

    i1i2shape=xyshape[::-1]
    # 1 means valid cell
    # cell_M=np.ones(i1i2shape,dtype="i1")

    # make it a circle lol
    mid=Cord(xyshape,"xy")/2

    cell_M=np_circle(i1i2shape,dtype="i1",center=mid,r=30)


    m=Maze2D(cell_M,res,padding,line_width,bg_color,ani_walls,ani_cells,start,end,draw_explore,show_text,graphic_sys)
    
    # ask()
    m.graphic.render_maze()
    
    
    
    # create walls
    
    m.navigation.DFS_wallmaker()
    # ask()
    time.sleep(3)
    
    m.graphic.save_image()
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
