import matplotlib.pyplot as plt
from PIL import Image
import matplotlib.patches as patches
from heuristics import bfs
from getMap import get_array

cur_img = Image.open('./assets/imgs/cur-map.png')

fig, ax = plt.subplots()
ax.imshow(cur_img)

ban_do = get_array()

def onclick(event):
    x, y = event.xdata, event.ydata
    
    if x is not None and y is not None:

        print(x, y)
        
        ax.scatter(x, y, color='red', s=100)
        plt.draw()

fig.canvas.mpl_connect('button_press_event', onclick)


plt.title("Phường Láng Thượng, quận Đống Đa, thành phố Hà Nội")
plt.show()
