

from modules.support import *
from modules.classes import *

def main():

    # this doesnt even work on this
    # seed=random.randint(0,9999)
    # random.seed=seed
    # print("seed=",random.seed)

    xyshape=(140,60)
    # xyshape=(120,80)
    # xyshape=(1000,1000)
    
    start=Cord((10,10))
    end=Cord(xyshape,"xy")-start
    



    i1i2shape=xyshape[::-1]
    # 1 means valid cell

    # regular all cells valid maze
    cell_M=np.ones(i1i2shape,dtype="i1")

    # make it a circle lol
    # mid=Cord(xyshape,"xy")/2
    # cell_M=np_circle(i1i2shape,dtype="i1",center=mid,r=30)


    m=Maze2D(
                cell_M=cell_M,

                res=10,
                padding=30,
                line_width=1,

                bg="grey",

                ani_walls=False,
                ani_cells=True,

                start=start,
                end=end,

                draw_explore=True,
                show_text=True,
                graphic_cls=Graphic_IMG,
                render_window=True
             )


    
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
    m.graphic.save_image()
    time.sleep(3)
    
    # runs double A*
    m.graphic.reset_maze()
    m.graphic.render_maze()
    m.navigation.double_A_star()
    


    m.graphic.start()

main()
