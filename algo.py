from PIL import Image
from math import sqrt , floor
import numpy as np

path = input("Enter picture path including it's name: ")

mode = int(input("For Horizontal reduction enter 0 and for vertical reduction enter 1: "))
if mode == 1:
    raw_img = Image.open(path)
    raw_img = raw_img.rotate(90 , expand=True)
    raw_img.save(path)    

raw_image = Image.open(path)
raw_image_width = raw_image.size[0]
raw_image_hight = raw_image.size[1]
reduce_amount =  int(input("Reduce amount: "))
#energy-map image output path
energy_output_path = "energy_map.png"

#implement Dual-gradient algorithm function to measure energy
def energy(x,y,pix):
    

    width = raw_image_width
    hight = raw_image_hight

    R=pix[x,y][0]
    G=pix[x,y][1]
    B=pix[x,y][2]
    
    Xd = x-1
    Xe = x+1
    Yd = y-1
    Ye = y+1

    if x==0:
        Xd = x
    if x==width-1:
        Xe = x
    if y==0:
        Yd = y
    if y==hight-1:
        Ye = y
    
    Rx=pix[Xd,y][0] - pix[Xe,y][0]
    Gx=pix[Xd,y][1] - pix[Xe,y][1]
    Bx=pix[Xd,y][2] - pix[Xe,y][2]

    Ry=pix[x,Yd][0] - pix[x,Ye][0]
    Gy=pix[x,Yd][1] - pix[x,Ye][1]
    By=pix[x,Yd][2] - pix[x,Ye][2]

    DELTAx = Rx*Rx + Gx*Gx + Bx*Bx
    DELTAy = Ry*Ry + Gy*Gy + By*By

    e = sqrt(DELTAx + DELTAy)
    return e
    #maximum amount of e is 624.6 and the minimum is 0

#implement energy_map function wich creates an b-w image to show energy of each pixel.(more energy , more white)
def energy_map():
    raw_img = Image.open(path)
    raw_pix = raw_img.load()
    blank_image = Image.new('RGB', (raw_image_width, raw_image_hight))
    blank_pix = blank_image.load()

    for w in range (0,raw_image_width):
        for h in range (0,raw_image_hight):
            energy255 = (energy(w,h,raw_pix)*255)/624.7
            energy255 = floor(energy255)
            blank_pix[w,h] = (energy255,energy255,energy255)

    blank_image.save("energy_map.png")
    return True

#measure lowest-cost for each pixel to rech the bottom of the image using dynamic programming(matrix as DP table)
def create_dp_table():
    energy_img = Image.open("energy_map.png")
    energy_pix = energy_img.load()
    size = (raw_image_hight,raw_image_width)
    dp_table = np.zeros(size)

    for i in range(0,raw_image_width):
        dp_table[raw_image_hight-1][i] = energy_pix[i, raw_image_hight-1][0]

    for h in range(raw_image_hight-2, -1, -1):
        for w in range (0,raw_image_width):
            if w == 0:
                dp_table[h][w] = min(dp_table[h+1][w], dp_table[h+1][w+1]) + energy_pix[w,h][0]
            elif w == raw_image_width - 1:
                dp_table[h][w] = min(dp_table[h+1][w], dp_table[h+1][w-1]) + energy_pix[w,h][0]
            else:
                dp_table[h][w] = min(dp_table[h+1][w], dp_table[h+1][w+1], dp_table[h+1][w-1]) + energy_pix[w,h][0]

    return dp_table



#find lowest-cost path(seam) and show it on image
def find_lowest_cost_seam():
    energy_img = Image.open("energy_map.png")
    energy_pix = energy_img.load()
    dp_table = create_dp_table()
    start_pixel_value = min(dp_table[0])
    path_pixels = []

    for i in range(0,raw_image_width):
        if dp_table[0][i] == start_pixel_value:
            dp_table[0][i] = 1000000000000
            start_pixel_xy = [0,i]
            path_pixels.append(start_pixel_xy)
            break

    for h in range(1,raw_image_hight):
        previous_pixel = path_pixels[ len(path_pixels)-1 ]

        if previous_pixel[1] == 0:
            candidate_pixels = [ dp_table[h][previous_pixel[1]], dp_table[h][previous_pixel[1]+1] ]
            next_pixel_value = min( candidate_pixels )
            if candidate_pixels[0] == next_pixel_value:
                path_pixels.append([h, previous_pixel[1]])
            elif candidate_pixels[1] == next_pixel_value:
                path_pixels.append([h, previous_pixel[1]+1])
                
        
        elif previous_pixel[1] == raw_image_width - 1:
            candidate_pixels = [ dp_table[h][previous_pixel[1]-1], dp_table[h][previous_pixel[1]] ]
            next_pixel_value = min( candidate_pixels )
            if candidate_pixels[1] == next_pixel_value:
                path_pixels.append([h, previous_pixel[1]])
            elif candidate_pixels[0] == next_pixel_value:
                path_pixels.append([h, previous_pixel[1]-1])

        else:
            candidate_pixels = [ dp_table[h][previous_pixel[1]-1], dp_table[h][previous_pixel[1]], dp_table[h][previous_pixel[1]+1] ]
            next_pixel_value = min( candidate_pixels )
            if candidate_pixels[1] == next_pixel_value:
                path_pixels.append([h, previous_pixel[1]])
            elif candidate_pixels[0] == next_pixel_value:
                path_pixels.append([h, previous_pixel[1]-1])
            elif candidate_pixels[2] == next_pixel_value:
                path_pixels.append([h, previous_pixel[1]+1])
    
    for p in path_pixels:
        w = p[1]
        h = p[0]
        energy_pix[w,h] = (255,0,0)

    energy_img.save("energy_map.png")          
    return path_pixels

#reshape the original image to reduce dimensions
def reshape():
    raw_img = Image.open(path)
    raw_pix = raw_img.load()

    energy_img = Image.open("energy_map.png")
    energy_pix = energy_img.load()

    for h in range(0,raw_image_hight):
        red_detected = 0
        for i in range(0,reduce_amount):
            red_detected = 0
            for w in range(0,raw_image_width):
                if energy_pix[w,h][0] == 255:
                    red_detected = 1

                if red_detected == 0:
                    raw_pix[w,h] = raw_pix[w,h]
                    energy_pix[w,h] = energy_pix[w,h]

                else:
                    if w == raw_image_width-1:
                        raw_pix[w,h] = (0,255,0)
                        energy_pix[w,h] = (0,255,0)
                    else:
                        raw_pix[w,h] = raw_pix[w+1,h]
                        energy_pix[w,h] = energy_pix[w+1,h]

    raw_img.save("new_image.png")
    energy_img.save("new_energy.png")
    img_left = Image.open("new_image.png")   
    img_left_area = (0, 0, raw_image_width-reduce_amount-1, raw_image_hight)
    img_left = img_left.crop(img_left_area)
    img_left.save("new_image.png")

    #final rotation
    if mode == 1 :
        raw_img = Image.open(path)
        raw_img = raw_img.rotate(270 , expand=True)
        raw_img.save(path)

        out_img = Image.open("new_image.png")
        out_img = out_img.rotate(270 , expand=True)
        out_img.save("new_image.png")

        new_energy_img = Image.open("new_energy.png")
        new_energy_img = new_energy_img.rotate(270 , expand=True)
        new_energy_img.save("new_energy.png")

        energy_img = Image.open("energy_map.png")
        energy_img = energy_img.rotate(270 , expand=True)
        energy_img.save("energy_map.png")
    return True

#calling all the functions
triger1 = energy_map()
print('energy-map image created, please wait...')
for i in range(0,reduce_amount):
    triger2 = find_lowest_cost_seam()
print('seams found, please wait...')
triger3 = reshape()
print('Finished')
