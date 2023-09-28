import cv2 
from matplotlib import pyplot as plt
import numpy as np
from scipy.signal import find_peaks
import pickle
from matplotlib.gridspec import GridSpec
from pathlib import Path
from IPython.display import display, HTML
import pandas as pd
pd.options.display.float_format = '{:,.2f}'.format

# apply CLAHE to raw image
def CLAHE(filename):
    img = cv2.imread(filename+'.tif', 1)
    lab_img= cv2.cvtColor(img, cv2.COLOR_BGR2LAB)

    l, a, b = cv2.split(lab_img)

    equ = cv2.equalizeHist(l)
    updated_lab_img1 = cv2.merge((equ,a,b))
    hist_eq_img = cv2.cvtColor(updated_lab_img1, cv2.COLOR_LAB2BGR)

    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    clahe_img = clahe.apply(l)
    updated_lab_img2 = cv2.merge((clahe_img,a,b))
    CLAHE_img = cv2.cvtColor(updated_lab_img2, cv2.COLOR_LAB2BGR)

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(10, img.shape[0]*10/img.shape[1]))
    ax1.imshow(img)
    ax1.set_title("original")
    ax1.axis("off")
    ax2.imshow(hist_eq_img)
    ax2.set_title("global he")
    ax2.axis("off")
    ax3.imshow(CLAHE_img)
    ax3.set_title("clahe")
    ax3.axis("off")
    cv2.imwrite(filename+"_clahe.tif", CLAHE_img)
    return CLAHE_img

# rotate image
def rotate_img(filename):
    raw_img = cv2.imread(filename+"_clahe.tif", 1)
    align_img = np.copy(raw_img)

    def draw_circle(event, x,y, flags, param):
        global mouseX, mouseY
        if event ==cv2.EVENT_LBUTTONDBLCLK:
            cv2.circle(align_img, (x,y), 5, (255,0,0), 2)
            mouseX, mouseY = x, y

    cv2.namedWindow('image', cv2.WINDOW_NORMAL)
    cv2.setMouseCallback('image', draw_circle)

    num = 0
    p = np.empty((0,2), np.uint8)
    while(1):
        cv2.imshow('image', align_img)
        k = cv2.waitKey(20) & 0xFF
        if k==27:
            cv2.destroyAllWindows()
            break
        elif k == ord('a'):
            p = np.append(p, np.array([[mouseX, mouseY]]), axis =0)
            cv2.putText(align_img, "+", (mouseX, mouseY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255),2)
    
    if len(p) >=2:
        # Linear fit the line and work out the angle to be adjusted

        model = np.polyfit(p[:, 0], p[:,1],1)

        angle = np.arctan(model[0])*180/np.pi

        adj = angle+90 #adjust this +90 or -90
        
        if adj > 90:
            adj = 180 - adj

        height, width = raw_img.shape[:2]
        centerX, centerY = (width // 2, height // 2)
        M = cv2.getRotationMatrix2D((centerX, centerY), adj, 1.0)
        rotated = cv2.warpAffine(raw_img, M, (width, height))

        margin_x = int(height*np.tan(adj*np.pi/180))
        margin_y = int(width*np.tan(adj*np.pi/180))
       
        rotated_img = rotated[margin_y:height-margin_y,margin_x:width-margin_x,:]
        fig, ax = plt.subplots(1, 2, figsize=(10, raw_img.shape[0]*10/raw_img.shape[1]))
        ax[0].imshow(raw_img)
        ax[0].set_title("clahe")
        ax[0].axis("off")
        ax[1].imshow(rotated_img)
        ax[1].set_title("vertically aligned" + ", by {:.2f} rads".format(adj))
        ax[1].axis("off")
        cv2.imwrite(filename+"_rotated.tif", rotated_img)
    else:
        print("You need to select at least 2 points")
        adj = 0
        rotated_img = None
    return rotated_img, adj

# Function to find borders - use the integrated intensity along the vertical dimension
def findborder(img, channel = 'r', p = 2, n=0, width = 50): # p is for peak prominence
    b, g, r = cv2.split(img) # use blue channel to find border
    
    if channel =='b':
        img_to_analyse = b;
    elif channel == 'g':
        img_to_analyse = g;
    elif channel == 'r':
        img_to_analyse = r;
        
    vsum = np.sum(img_to_analyse, axis = 0) # intergrate vertical pixels
    profile = abs(np.gradient(vsum)) # take grident
    borders, _ = find_peaks(profile, prominence=max(profile)/p)
    
    width = 50 # um The width of the physical pattern
    w = np.mean(np.gradient(borders))
    calibration = width/w # pixel to real dimension

    dx = int(w)
    xmin = max(0, borders[n] - dx)
    xmax = min(img.shape[1], borders[n] + dx)
    
   
    if len(borders) >0:
        fig = plt.figure(figsize=(10, 4))
        gs = GridSpec(nrows=2, ncols=2)
        ax0 = fig.add_subplot(gs[:, 0])
        ax0.imshow(img, cmap='gray')
        ax0.plot(img.shape[0]-profile*img.shape[0]/(max(profile)-min(profile)))
        ax0.vlines(borders, 0, img.shape[0], linestyles ="dotted", colors ="w")
        ax0.set_title("{:.0f} borders, 1 pixel = {:.2f}um".format(len(borders), calibration))
        ax0.axis('off')
        for b in borders:
            ax0.text(b-25, img.shape[0]+30, str(np.where(borders == b)[0][0]), fontsize = 8)

        ax1 = fig.add_subplot(gs[0, 1])
        ymin = 0
        ymax = xmax-xmin # 0 - vertical, 1 - horizontal
        ax1.imshow(img[ymin:ymax, xmin:xmax])
        ax1.vlines(borders[n]-xmin, ymin, ymax, linestyles ="dotted", alpha=0.7, colors ="w")
        ax1.set_title ("border {}".format(n))
        ax1.axis('off')
        ax2 = fig.add_subplot(gs[1, 1])
        ymin = int(img.shape[0]-xmax+xmin)
        ymax = img.shape[0]
        ax2.imshow(img[ymin:ymax, xmin:xmax])
        ax2.vlines(borders[n]-xmin, 0, ymax-ymin, linestyles ="dotted", alpha=0.7, colors ="w")
        ax2.axis('off')
        fig.tight_layout(pad=0)
        
    else:
        print('Can NOT find any border. Try adjusting p and redo this')
    
    dimension = {'width': width, 'calib': calibration, 'borders':borders}
    print(dimension)
    return dimension

# Find borders using file name
def find_borders(filename, channel = 'r', p = 2, n = 0, width = 50):
    rotated_img = cv2.imread(filename+"_rotated.tif", 1)
    dimension = findborder(rotated_img, channel, p, n)
    with open(filename + '_rotated.txt', 'wb') as handle:
        pickle.dump(dimension, handle)
    return dimension

# Crop images
def crop_img(filename, sb = 0, eb = -1): # sb: starting index, eb: end index of the borders
    with open(filename+'_rotated.txt', 'rb') as handle:
        dim = pickle.loads(handle.read())
    img = cv2.imread(filename+"_rotated.tif", 1)
    cropped = np.array(img[:,dim["borders"][sb]:dim["borders"][eb],:], copy = True)
    dimension = findborder(cropped, p=2, n=1)
    # Save data and image
    flakes = []
    rawfile = filename + '_cropped.tif'
    with open(filename + '_cropped.txt', 'wb') as handle:
        pickle.dump([rawfile, flakes, dimension], handle)

    cv2.imwrite(filename + "_cropped.tif", cropped)

# Load image file and Identify flakes
def add_flake(filename):
    path = Path('./'+ filename + '_processed.txt')

    if path.is_file():
        data = filename + '_processed'
    else:
        data = filename + '_cropped'

    with open(data+'.txt', 'rb') as handle:
        [rawfile, flakes, dimension] = pickle.loads(handle.read())

    img = cv2.imread(data +'.tif', 1)
    proc_img = img.copy()
    proc_copy = img.copy()

    def draw_circle(event, x,y, flags, param):
        global mouseX, mouseY
        if event ==cv2.EVENT_LBUTTONDBLCLK:
            cv2.circle(proc_img, (x,y), 5, (255,0,0), 2)
            mouseX, mouseY = x, y
    cv2.namedWindow('image', cv2.WINDOW_NORMAL)

    cv2.setMouseCallback('image', draw_circle)

    num = len(flakes)
    p = np.empty((0,2), np.uint8)
    while(1):
        cv2.imshow('image', proc_img)
        k = cv2.waitKey(20) & 0xFF
        if k== 27:
            cv2.destroyAllWindows()
            break
        elif k == ord('a'):
            if len(p)==3:
                print("more than 3 points are added. press 't' to add a triangle.")
            else:
                p = np.append(p, np.array([[mouseX, mouseY]]), axis =0)
                cv2.putText(proc_img, "+", (mouseX, mouseY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255),2)
        elif k == ord('d'):
            if len(p) == 0:
                print("Nothing to delete from this session")
                p = np.empty((0,2), np.uint8)
            else:
                cv2.putText(proc_img, "+", p[-1], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0),2) 
                p = np.delete(p, -1, axis = 0)
                if len(p) == 0:
                    p = np.empty((0,2), np.uint8)
        elif k == ord('t') and len(p) ==3: # adding triangles
            cv2.drawContours(proc_copy, [p], 0, (0,0,255), -1) 
            cv2.addWeighted(proc_copy, 0.4, proc_img, 1 - 0.2, 0)
            cv2.drawContours(proc_img, [p], 0, (0,0,255), 0)

            # Find centeroid etc.
            tmp_img = np.zeros((proc_img.shape[0], proc_img.shape[1]), np.uint8)
            cv2.drawContours(tmp_img, [p], 0, (255,255,255), -1)

            Moments = cv2.moments(tmp_img)
            x0 = int(Moments["m10"]/Moments["m00"])
            y0 = int(Moments["m01"]/Moments["m00"])
            #cv2.circle(proc_img, (x0,y0), 5, (255,255,255), 2)
            cv2.putText(proc_img, str(num), (x0,y0), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255),2)
            flakes.append({'apex': p, 'cen': np.array([x0, y0])})
            p = np.empty((0,2), np.uint8)
            num += 1

    with open(filename + '_processed.txt', 'wb') as handle:
        pickle.dump([rawfile, flakes, dimension], handle)
    cv2.imwrite(filename+"_processed.tif", proc_img)
    print("There are {} flakes.".format(len(flakes)))

# delete flake
def delete_flake(filename, num):
    with open(filename + '_processed.txt', 'rb') as handle:
        [rawfile, flakes, dimension] = pickle.loads(handle.read())
    if num < len(flakes):
        flakes.pop(num) # Remove a flake
    else:
        print('Flake num out of range. There are {} flakes. The index should be less than {}.'.format(len(flakes), None if len(flakes) == 0 else len(flakes)-1))
    
    with open(filename + '_processed.txt', 'wb') as handle:
        pickle.dump([rawfile, flakes, dimension], handle)
    proc_img = draw_flakes(filename)
    print("There are {} flakes.".format(len(flakes)))
        
# update the image: draw flakes
def draw_flakes(filename, category = 'A', mode = 'n'): 
    # Mode: n, mark flakes using array index; c, marked by a circle
    # catogory: "A", all flakes
    with open(filename + '_processed.txt', 'rb') as handle:
        [rawfile, flakes, dimension] = pickle.loads(handle.read())
        
    if category == "E":
        selected = [i for i in flakes if i["type"] == 'E']
        flake_type = "on etched regions"
        imgfile = filename+"_processed_" + category + ".tif"
    elif category == "U":
        selected = [i for i in flakes if i["type"] == 'U']
        flake_type = "on unetched regions"
        imgfile = filename+"_processed_" + category + ".tif"
    elif category == "B":
        selected = [i for i in flakes if i["type"] == 'Eb' or i["type"] =='Ub']
        flake_type = "on boundary regions"
        imgfile = filename+"_processed_" + category + ".tif"
    elif category == 'A':
        selected = flakes
        flake_type = "all regions"
        imgfile = filename+"_processed.tif"
    with open(filename + '_processed.txt', 'rb') as handle:
        [rawfile, flakes, dimension] = pickle.loads(handle.read())
        
    img = cv2.imread(filename + '_cropped.tif', 1)
    proc_img = img.copy()
    proc_copy = img.copy()

    num = 0 
    for flake in selected:
        cv2.drawContours(proc_copy, [flake["apex"]], 0, (0,0,255), -1) 
        cv2.addWeighted(proc_copy, 0.4, proc_img, 1 - 0.2, 0)
        cv2.drawContours(proc_img, [flake["apex"]], 0, (0,0,255), 0)
        # Show center
        if mode == 'n':
            cv2.putText(proc_img, str(num), flake["cen"], cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255),2)
        else:
            cv2.circle(proc_img, flake["cen"], 5, (255,255,255), 2)
        num += 1

    cv2.namedWindow('checkflakes', cv2.WINDOW_NORMAL)
    cv2.imshow('checkflakes', proc_img)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.imwrite(imgfile, proc_img)
    return proc_img

# Draw individual flake
def draw_flake(filename, num):
    with open(filename + '_processed.txt', 'rb') as handle:
        [rawfile, flakes, dimension] = pickle.loads(handle.read())
    img = cv2.imread(filename + '_cropped.tif', 1)
    w = np.mean(np.gradient(dimension["borders"])) # the average width of the pattern
    d = int(w/2)
    if num < len(flakes):
        flake = flakes[num]
        find_intercepts(flake, dimension)
        sv = max(flake["range"][1][0]-d,0); ev = min(flake["range"][1][1] + d, img.shape[0]);
        sh = max(flake["range"][0][0]-d,0); eh = min(flake["range"][0][1] + d, img.shape[1]); 

        # draw contours
        for part in flake["parts"]:
            colour = (0,0,255) if part["type"] == "U" else (0,255,255)
            cv2.drawContours(img, [np.rint(part["apex"]).astype(int)], 0, colour, -1) 
        
        # draw angles
        topindex=flake["apex"][:,1].argmin()
        top = flake["apex"][topindex]
        cv2.line(img, flake["cen"], top, color=(255,255,255), thickness=1) 
        cv2.line(img, flake["cen"], (flake["cen"][0], top[1]), color=(255,255,255), thickness=1)
        
        fig, ax = plt.subplots()
        ax.imshow(img[sv:ev, sh:eh, :]) # the first index is for vertical direction
        ax.vlines([flake["cuts"]-sh], 0, ev-sv, linestyles ="dotted", alpha=0.8, colors ="w") # the first para is horizontal
        cen = plt.Circle(flake["cen"]-(sh, sv), 3, color='r', fill=False)
        ax.add_patch(cen)
        for corner in flake["apex"]:
            corner_c =  plt.Circle(corner-(sh, sv), 3, color='b', fill=False)
            ax.add_patch(corner_c)
        for interc in flake["intercepts"]:
            interc_c = plt.Circle(interc-(sh, sv), 3, color='y', fill=False)
            ax.add_patch(interc_c)
        ax.axis('off')
        ax.set_title("flake {}: totArea = {:.2f} (E,{:.2f} + U,{:.2f}), angle = {:.2f}".format(num, flake["totArea"], flake["E_area"], flake["U_area"], flake["orient"]))
        return img[sv:ev, sh:eh, :]
    else:
        print('Flake num out of range. There are {} flakes. The index should be less than {}.'.format(len(flakes), None if len(flakes) == 0 else len(flakes)-1))
        return None
    

# handle border cut through a flake
def find_intercepts(flake, dimension):
    v = flake["apex"][:,1]; vmax = max(v); vmin = min(v)
    h = flake["apex"][:,0]; hmax = max(h); hmin = min(h) # the first index represents horizontal direction
    flake["range"] = np.array([[hmin, hmax], [vmin, vmax]])

    borders = dimension["borders"]
    flake["cuts"] = borders[(borders>[hmin])*(borders <[hmax])] 
    
    # Find the intercept
    def solve_y(x, p1, p2):
        if p2[0] != p1[0]:
            y = (p2[1]-p1[1])*(x-p1[0])/(p2[0]-p1[0]) + p1[1]
        elif p1[0] == x: # if the line through the two apexes is vertical and pass through the vertical line, return the two apexes 
            y = p1[1], p2[1] 
        else:
            y = -1E9 # if the line through the two apexes is vertical and not pass through the vertical line, the cut at infty
        return y

    flake["intercepts"] = np.empty((0,2), np.uint8)
    for cut in flake["cuts"]:
        y = np.array([solve_y(cut, flake["apex"][0], flake["apex"][1])])
        y = np.append(y, [solve_y(cut, flake["apex"][1], flake["apex"][2])])
        y = np.append(y, [solve_y(cut, flake["apex"][2], flake["apex"][0])])
        ycut = y[(y>=vmin)*(y<=vmax)]
        if len(ycut) > 0:
            flake["intercepts"] = np.append(flake["intercepts"], [[cut, cut_y] for cut_y in ycut] , axis =0)
        else:
            print(flake)

# sort points anticlockwise for contours
def sort_points(points, cen):
    sorted_points = np.array(points, copy = True)
    angle = []
    for point in sorted_points:
        if point[1] == cen[1]:
            if point[0] < cen[0]:
                angle.append(-np.pi/2)
            else:
                angle.append(np.pi/2)
        else:
            a = np.arctan((point[0]-cen[0])/(point[1]-cen[1]))
            if point[1] > cen[1]:
                angle.append(a+np.pi)
            else:
                angle.append(a)
    angle = np.array(angle)
    angle = np.reshape(angle, (points.shape[0], 1))
    
    sorted_points = np.append(sorted_points, angle, axis=1)
    sorted_points = np.array(sorted_points[sorted_points[:,2].argsort()])
    return  np.delete(sorted_points, -1, axis=1)

# Classify flakes and calculate orientations, area etc.
def analysis(filename, first='E', cri_dx=0.5):
    #first = 'E' - etched; 'U' - unetched
    #cri_dx = 8 # boundary extension
    with open(filename + '_processed.txt', 'rb') as handle:
        [rawfile, flakes, dimension] = pickle.loads(handle.read())
    cri_dx = cri_dx/dimension["calib"] # convert to pixels
    w = np.mean(np.gradient(dimension["borders"])) # borders in dimensions are in pixels
    # dimension["width"] = 50
    
    for flake in flakes:
         # Assign flake type: U, E, Ub, Eb
        flake["offset"] = flake["cen"][0] % w  # distance to the previous edge
        flake["numBlocks"] = np.round((flake["cen"][0]-flake["offset"])/w)
        if int(flake["numBlocks"])%2 == 0:
            flake['type'] = first 
        else:           
            flake['type'] = 'U' if (first == 'E') else 'E'
            
        if flake["offset"] > w/2: 
            flake["offset"] = w-flake["offset"]
        if abs(flake["offset"]) < cri_dx:
            flake['type'] = flake['type'] + 'b'
        
        if flake['type'] == 'U': # Unetched offsets is negative
            flake["offset"] = - flake["offset"]

        # Orientation: topmost and centre points
        topindex=flake["apex"][:,1].argmin()
        top = flake["apex"][topindex]
        if float(top[0]-flake["cen"][0]) != 0:
            a = np.arctan(float(top[0]-flake["cen"][0])/float(top[1]-flake["cen"][1]))
            flake["orient"] = a*180/np.pi
            if flake["type"] == "Ub":
                flake["orient"] = - flake["orient"]
        else:
            flake["orient"] = 0

        # Total area
        #contour = np.array(flake["apex"]).reshape(len(flake["apex"]), 1, 2)
        flake["totArea"] = cv2.contourArea(flake["apex"])

        # work out parts, divided by the borders, and their types: U or E
        find_intercepts(flake, dimension)
        num_parts = len(flake["cuts"]) + 1
        flake["parts"] = [{}] * num_parts

        points = np.array(flake["intercepts"], copy = True)
        points = np.append(points, flake["apex"], axis=0)
        points = np.array(points[points[:, 0].argsort()], copy = True)
        #points = np.sort(points, axis = 0) # check axis 0 - horizontal
        flake["E_area"] = 0
        flake["U_area"] = 0
        num = 0
        if num_parts == 1: # no border cut
            flake["parts"][0] = {'apex': flake['apex'], 'area': flake['totArea'], 'type': flake['type']}
        else:
            # Work out part types - on U or E
            area_type = ['']*num_parts
            cut_cen = np.array(flake["cuts"], copy = True)
            cut_cen = np.append(cut_cen, flake["cen"][0])
            cut_cen = np.sort(cut_cen)
            pos_cen = np.where(cut_cen == flake["cen"][0])
            cri = pos_cen[0][0] % 2
            for i in range(num_parts):
                if i % 2 == cri:
                    area_type[i] = flake['type'][0]
                else:
                    area_type[i] = "U" if (flake['type'][0] == "E") else "E"
            # Create parts
            sp = 0
            for cut in flake["cuts"]:
                p_cut = np.where(points[:,0] == cut)
                ep = p_cut[0][-1] + 1
                apex = sort_points(points[sp:ep],  flake["cen"])
                contour = np.array(apex , copy = True, dtype = np.intc) #, dtype=np.uint8
                flake["parts"][num] = {'apex':apex, 'area': cv2.contourArea(contour), 'type': area_type[num]}
                sp = p_cut[0][0]
                num += 1
            apex = sort_points(points[sp:],  flake["cen"])
            contour = np.array(apex, copy = True, dtype = np.intc)
            flake["parts"][num] = {'apex':apex, 'area': cv2.contourArea(contour), 'type': area_type[num]}
        E_parts = [i for i in flake["parts"] if i["type"] == 'E']
        flake["E_area"]=sum(item['area'] for item in E_parts)

        U_parts = [i for i in flake["parts"] if i["type"] == 'U']
        flake["U_area"]=sum(item['area'] for item in U_parts)
    with open(filename + '_processed.txt', 'wb') as handle:
        pickle.dump([rawfile, flakes, dimension], handle)
    
    All = statistics(filename)
    Etched = statistics(filename, category = 'E')
    Unetched = statistics(filename, category = 'U')
    Border = statistics(filename, category = 'B')
    
    # Cacluate the total areas of the substrates
    borders = All["data"]["borders"]
    numBorders = len(borders)
    numBlocks = numBorders + 1
    num1stBlocks = np.ceil(numBlocks/2)
    num2ndBlocks = np.floor(numBlocks/2)
    img = cv2.imread(filename + '_cropped.tif', 1)
    img_height =img.shape[0]*All["data"]["dimension"]["calib"]
    
    sw = dimension["width"] - 2*cri_dx*dimension["calib"]
    Block_area = sw*img_height

    if first == 'E':
        E_sub_area = num1stBlocks*Block_area + Block_area
        U_sub_area = num2ndBlocks*Block_area + Block_area
    else:
        E_sub_area = num2ndBlocks*Block_area 
        U_sub_area = num1stBlocks*Block_area
    B_sub_area = 2*numBlocks*cri_dx**dimension["calib"]*img_height

    All["summary"]["subArea"] = img.shape[0]*img.shape[1]*All["data"]["dimension"]["calib"]**2
    All["summary"]["density"] =  All["summary"]["totNum"]/All["summary"]["subArea"]
    Etched["summary"]["subArea"] = E_sub_area
    Etched["summary"]["density"] = Etched["summary"]["totNum"]/Etched["summary"]["subArea"]
    Unetched["summary"]["subArea"] = U_sub_area
    Unetched["summary"]["density"] = Unetched["summary"]["totNum"]/Unetched["summary"]["subArea"]
    Border["summary"]["subArea"] = B_sub_area
    Border["summary"]["density"] = Border["summary"]["totNum"]/Border["summary"]["subArea"]
    
    with open(filename + '_analysed.txt', 'wb') as handle:
        pickle.dump([All, Etched, Unetched, Border], handle)
    
    summary = pd.DataFrame()
    for data in [All, Etched, Border, Unetched]:
        s = [summary, pd.DataFrame(data["summary"], index = [0])]
        summary = pd.concat(s)
    display(HTML(summary.to_html(index=False)))

    return True

# Collect data from the given sets
def statistics(filename, category='A'):
    with open(filename + '_processed.txt', 'rb') as handle:
        [rawfile, flakes, dimension] = pickle.loads(handle.read())
    xpos = np.empty((0,2), np.uint8)
    ypos = np.empty((0,2), np.uint8)
    offsets = np.empty((0,2), np.uint8)
    orient = np.empty((0,2), np.float16)
    totArea = np.empty((0,2), np.float16)
    U_ratio = np.empty((0,2), np.float16)
    E_ratio = np.empty((0,2), np.float16)
    
    if category == "E":
        selected = [i for i in flakes if i["type"] == 'E']
        flake_type = "Etched"
    elif category == "U":
        selected = [i for i in flakes if i["type"] == 'U']
        flake_type = "Unetched"
    elif category == "B":
        selected = [i for i in flakes if i["type"] == 'Eb' or i["type"] =='Ub']
        flake_type = "Boundary"
    elif category == 'A':
        selected = flakes
        flake_type = "All"

    if len(selected) == 0 :
        print("No " + flake_type + "flake")
        summary = {'flake_type':flake_type, 'totNum':0, 'totArea_avg':0, 'totArea_std':0, 'orient_avg':0, 'orient_std':0, 'U_ratio_avg': 0, 'U_ratio_std': 0, 'E_ratio_avg': 0, 'E_ratio_std': 0}
        data = {'rawfile': rawfile, 'category': category, 'dimension':dimension,'flakes':[], 'borders':dimension["borders"]*dimension["calib"], 'xpos': [], 'ypos': [],'offsets': offsets, 'totArea': [], 'orient': [], 'U_ratio': [], 'E_ratio': []}
        return {'summary': summary, 'data': data}
    totNum = len(selected)

    for flake in selected:
        # Collect center positions
        xpos = np.append(xpos, flake["cen"][0]*dimension["calib"])
        ypos = np.append(ypos, flake["cen"][1]*dimension["calib"])
        offsets = np.append(offsets, flake["offset"]*dimension["calib"])
        totArea = np.append(totArea, flake["totArea"]*dimension["calib"]**2)
        orient = np.append(orient, flake["orient"])
        U_ratio = np.append(U_ratio, flake["U_area"]/flake["totArea"])
        E_ratio = np.append(E_ratio, flake["E_area"]/flake["totArea"])
    
    totArea_avg = np.average(totArea); totArea_std = np.std(totArea)
    orient_avg = np.average(orient);   orient_std = np.std(orient)
    U_ratio_avg = np.average(U_ratio); U_ratio_std = np.std(U_ratio)
    E_ratio_avg = np.average(E_ratio); E_ratio_std = np.std(E_ratio)

    summary = {'flake_type':flake_type, 'totNum':totNum, 'totArea_avg':totArea_avg, 'totArea_std':totArea_std, 'orient_avg':orient_avg, 'orient_std':orient_std, 'U_ratio_avg': U_ratio_avg, 'U_ratio_std': U_ratio_std, 'E_ratio_avg': E_ratio_avg, 'E_ratio_std': E_ratio_std}
    data = {'rawfile': rawfile, 'category': category, 'dimension':dimension,'flakes':selected,'borders':dimension["borders"]*dimension["calib"], 'xpos': xpos, 'ypos': ypos, 'offsets': offsets, 'totArea': totArea, 'orient': orient, 'U_ratio': U_ratio, 'E_ratio': E_ratio}
    return {'summary': summary, 'data': data}

def plot_statistics(filename, category = 'A'):
    with open(filename + '_analysed.txt', 'rb') as handle:
        [All, Etched, Unetched, Border]= pickle.loads(handle.read())
    if category == "E":
        data = Etched["data"]
        summary = Etched["summary"]
    elif category == "U":
        data = Unetched["data"]
        summary = Unetched["summary"]
    elif category == "B":
        data = Border["data"]
        summary = Border["summary"]
    elif category == 'A':
        data = All["data"]
        summary = All["summary"]
    # plot statistics
    borders = data["borders"]
    fig, ax = plt.subplots(2,3, figsize=(10,4))
    y, x, _ = ax[0][0].hist(data["xpos"], edgecolor='black', linewidth=0, alpha=0.5, bins = 200); # bins: total number of bins 
    ax[0][0].vlines(borders, 0, y.max(), linestyles ="dotted", alpha=0.2, colors ="b")
    ax[0][0].set_title('Number of flakes - horizontal')
    ax[0][1].hist(data["orient"], edgecolor='black', linewidth=0.5, alpha=0.5);
    ax[0][1].set_title('Orientation, {:.2f} +/- {:.2f} D'.format(summary["orient_avg"], summary["orient_std"]))
    ax[0][2].hist(data["totArea"], edgecolor='black', linewidth=0.5, alpha=0.5);
    ax[0][2].set_title('flake area, {:.2f} +/- {:.2f}  um2'.format(summary["totArea_avg"], summary["totArea_std"]))

    ax[1][0].hist(data["ypos"], edgecolor='black', linewidth=0, alpha=0.5, bins = 200); # bins: total number of bins 
    ax[1][0].set_title('Number of flakes - vertical')
    ax[1][1].hist(data["U_ratio"], edgecolor='black', linewidth=0.5, alpha=0.5);
    ax[1][1].set_title('Unetched/Total, {:.2f} +/- {:.2f} D'.format(summary["U_ratio_avg"], summary["U_ratio_std"]))
    ax[1][2].hist(data["E_ratio"], edgecolor='black', linewidth=0.5, alpha=0.5);
    ax[1][2].set_title('Etched/Total, {:.2f} +/- {:.2f} D'.format(summary["E_ratio_avg"], summary["E_ratio_std"]))

    fig.suptitle(summary["flake_type"]+ " : " + str(summary["totNum"]) + " flakes", fontsize=16)
    fig.tight_layout() 
    return True

def plot_distribution(filename):
    with open(filename + '_analysed.txt', 'rb') as handle:
        [All, Etched, Unetched, Border] = pickle.loads(handle.read())

    data = All["data"]

    # Unetched offsets is negative
    center =  data["dimension"]["width"]/2
    fig, ax = plt.subplots(1,1, figsize=(10,4))
    ax.hist(data["offsets"], bins = 10, edgecolor='black', linewidth=0.5, alpha=0.5);
    ax.vlines([-center, center], 0, ax.get_ylim()[1]/2, linestyles ="dotted", alpha=1, colors ="g")
    ax.vlines([0], 0, ax.get_ylim()[1], linestyles ="solid", alpha=0.75, colors ="g")
    ax.set_title("Flake distribution at the border")
    ax.text(-center/2, ax.get_ylim()[1]*3/4, 'Unetched', horizontalalignment='center')
    ax.text(center/2, ax.get_ylim()[1]*3/4, 'Etched', horizontalalignment='center')
    ax.text(-center, ax.get_ylim()[1]/2, 'centre', horizontalalignment='center')
    ax.text(center, ax.get_ylim()[1]/2, 'centre', horizontalalignment='center')
    ax.text(0, ax.get_ylim()[1]/2, 'border', horizontalalignment='center')
    return True