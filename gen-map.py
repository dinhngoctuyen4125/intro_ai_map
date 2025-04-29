from PIL import Image

# Mở ảnh
img = Image.open("./assets/imgs/2-color-map.png")

# Chuyển ảnh thành chế độ RGB (nếu chưa phải)
img = img.convert("RGB")

# Lấy kích thước ảnh
width, height = img.size

print(width, height)

a = [[0] * width for _ in range(height)]

with open('numerical-data.txt', 'w', encoding='utf-8') as file:

    # Duyệt qua từng pixel
    for y in range(height):
        for x in range(width):
            # Lấy giá trị pixel tại (x, y)
            pixel = img.getpixel((x, y))
            # print(type(pixel))

            if (pixel == (255, 255, 255)):
                file.write('1 ')
            else:
                file.write('0 ')

            # pixel trả về là một tuple (R, G, B)
            # print(f"Pixel tại ({x},{y}): {pixel}")
        
        file.write('\n')
