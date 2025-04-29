import matplotlib.pyplot as plt
from PIL import Image

# Mở ảnh bản đồ
cur_img = Image.open('./assets/imgs/cur-map.png')

fig, ax = plt.subplots()
ax.imshow(cur_img)

points = [(0, 0), (200, 500), (1000, 1000)]

for point in points:
    ax.scatter(point[0], point[1], color='red', s=30)


def onclick(event):
    x, y = event.xdata, event.ydata
    
    if x is not None and y is not None:
        points.append((x, y))

        print(x, y)
        
        ax.scatter(x, y, color='red', s=100)
        plt.draw()
        
# Gắn sự kiện nhấp chuột vào hình ảnh
fig.canvas.mpl_connect('button_press_event', onclick)

# Hiển thị bản đồ
plt.axis('off')
plt.show()
