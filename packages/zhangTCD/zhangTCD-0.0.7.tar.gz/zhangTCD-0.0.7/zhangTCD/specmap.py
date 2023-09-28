# from pyspectra.readers.read_spc import read_spc
# https://github.com/rohanisaac/spc
# $ cd ~/Downloads/spc-master/
# $ python setup.py install
# pip3 install opencv-python

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import cv2 
from matplotlib.patches import Circle
from mpl_toolkits.axes_grid1 import make_axes_locatable
import seaborn as sns
# from scipy import sparse
# from scipy.sparse.linalg import spsolve
# from scipy.signal import find_peaks 
import pickle
from contextlib import redirect_stdout
import io
import matplotlib.patheffects as PathEffects
from scipy.signal import savgol_filter
from .spc import File

class specmap():
    I_cri = 0 # Choose a value that just screens out the substrate signal
    pRangelim = 100 # the spectrum range for process a peak - beyond this range the spec plot will not draw shaded regions
    points = np.empty((0,2), np.uint8) # coordinates of the added points, as array index
    plotSize = (18,3.2)
    plotRatio = {'width_ratios': [1, 1, 3]} # For plot_peak
    color_palette = "crest" # "blue"
    isSmoothed = False
    smooth_order = 3 # Smoothing polynomial order
     
    def __init__(self, rawdatafile, mode = 'Raman', refpeak = None, isSmoothed = False, isSavefile = True):
        """
        rawdatafile is the spc file, which will be imported as self.data
            self.data.sub[index] is a one-dimensional array which stores all the spectra. 
            To get the index for position (row, column): index = column + row*Lines_per_Image
            f.sub[0]: Data(0,0); f.sub[1]: Data(0,1)
            Note: row - x; column - y
        """
        self.isSmoothed = isSmoothed
        self.file = rawdatafile
        self.mode = mode
        self.isSavefile = isSavefile
        
        try:
            # Import spc file
            with redirect_stdout(io.StringIO()) as f:
                self.spc = File(self.file + '.spc');
        except:
            print('I cannot find the ' + self.file + '.spc file')
            return None

        
        # Import experimental info
        self.info= {}
        try:
            # Import info file
            with open(rawdatafile + '.csv', 'r', encoding='utf-8-sig') as infile:
                lines = infile.readlines()
            for line in lines:
                line_info = line.split(":,")
                line_info[0] = line_info[0].split(" [")[0]
                line_info[0] = line_info[0].replace(' ', '_')
                line_info[1] = line_info[1].replace('\n', '')
                self.info[line_info[0]] = line_info[1]
        except:
            print('I cannot find the ' + self.file + '.csv file (or wrong format: it need to be utf-8-sig coded) ' )
            return None
        
        # Print information
        [print(k[0], ':',  k[1]) for k in list(self.info.items())[0:5]]
        
        # Scale/collate peak by the reference peak
        nData = len(self.spc.sub)
        
        self.x = self.spc.x
        self.refpeak = refpeak
        self.offset = np.zeros(nData, np.float32)
        self.refI = np.zeros(nData, np.float32)
       
        
        if refpeak is not None:
            pk_range = [refpeak[0]-refpeak[1], refpeak[0]+refpeak[1]]
            sx, ex = self.xRange_To_yIndice(pk_range)
               
            for i in range(nData):
                y = self.spc.sub[i].y.astype('float')
                self.refI[i] = float(np.max(y[sx:ex]))
                y = y/self.refI[i] # scaled_data = y  
                ref_shift = y[sx:ex].argmax() - int((ex-sx)/2)
                self.spc.sub[i].y = np.roll(y, -ref_shift)
                self.offset[i] = ref_shift
                #self.spc.sub[i].y[0:ref_shift] = self.spc.sub[i].y[ref_shift]
        
        # Parameters from the infomation: Scan_002 Information.txt
        self.Points_per_Line = int(self.info['Points_per_Line']);
        self.Lines_per_Image = int(self.info['Lines_per_Image']);
        self.Scan_Width = float(self.info['Scan_Width']);
        self.Scan_Height = float(self.info['Scan_Height']);
        self.Scan_Origin_X = float(self.info['Scan_Origin_X']);
        self.Scan_Origin_Y = float(self.info['Scan_Origin_Y']);
        
        self.Excitation_Wavelength = float(self.info['Excitation_Wavelength']);
        self.Raman_shift = self.spc.x
        self.Wavelength = 1/(1/self.Excitation_Wavelength - self.Raman_shift*1e-7)
        self.Energy = 1239.8/self.Wavelength
        self.xy_unit = ' ($\mu$m)'

        # Work out filed of view, Image resolution
        self.FOV = [self.Scan_Origin_X, self.Scan_Origin_X + self.Scan_Width, self.Scan_Origin_Y, self.Scan_Origin_Y + self.Scan_Height] # [left, right, bottom, top]
        self.imgRes = [self.Lines_per_Image, self.Points_per_Line] # lines_per_Image: rows; Points_per_Line:cols
        
        # add initial points on the mappy
        self.points = np.append(self.points, np.array([[min(15, self.Points_per_Line-1), min(15,self.Lines_per_Image-1)]]), axis =0)
        self.points = np.append(self.points, np.array([[max(0,self.Points_per_Line-15), max(0,self.Lines_per_Image-15)]]), axis =0)
        self.nPoints = 2
 
        # set x axis - mode = Raman, PLw, PLe
        self.mode = mode
        if mode == 'Raman':
            self.x = self.Raman_shift
            self.spc_x_unit = ' (cm$^{-1}$)'
            self.spc_x_label = 'Raman shift'
        elif mode == 'PLw':
            self.x = self.Wavelength
            self.spc_x_label = 'Wavelength'
            self.spc_x_unit = ' (nm)'
        elif mode == 'PLe':
            self.x = self.Energy
            self.spc_x_label = 'Energy'
            self.spc_x_unit = ' (eV)'
        self.spc_y_label = 'Arbitrary Intensity'
        self.spc_y_unit = '(a.u.)'

        
        # Generate the full range integrated spectrum and map
        self.overview = self.create_peak("Overview")
    
    # ======== Plotting ====================
    # Add an ax for colorbar
    def format_colorbar(self, ax):
        """
        add an ax besides the image map, i.e. resize the colorbar to fit the image
        """
        divider = make_axes_locatable(ax)
        return divider.append_axes("right", size="5%", pad=0.05)
    
    # List peak positions
    def list_points(self, peak):
        loc = np.empty((0,1))
        I = np.empty((0,1))
        label = np.empty((0,1))
        pos = np.empty((0,1))
        offset = np.empty((0,1))
        refI = np.empty((0,1))
        
        i = 0
        for sp in peak['points']:
            x, y = self.rc_to_xy(sp[0], sp[1])
            str_x = "{:.2f}".format(x); str_y = "{:.2f}".format(y)
            loc = np.append(loc, '(' + str_x + ', ' + str_y + ')')
            I = np.append(I, peak['I'][sp[0], sp[1]])
            pos = np.append(pos, peak['pos'][sp[0], sp[1]])
            label = np.append(label, chr(ord('@') + i + 1))
            offset = np.append(offset, peak['offset'][sp[0], sp[1]])
            refI = np.append(refI, peak['refI'][sp[0], sp[1]])
            i += 1  
        data = {
            "Location": loc,
            "Integrated I": I,
            "Peak position": pos,
            "Ref I": refI,
            "Ref offset": offset
            #"Peak position": [50, 40, 45],
        }
        poitProfile = pd.DataFrame(data, index = label)
        
        display(poitProfile)
        return poitProfile
    
    # Plot a map
    def plot_map(self, peak, ax, mode, Vmin = None, Vmax = None, pkA = None, pkB = None): 
        """
        ax, mode, Vmin, Vmax, pkA, pkB):
        """
        # spectra range for the map
        if mode == 'pos': # Calculate the map ranges for pos
            if peak['isCompPK'] == True: # The peak is a comparison of two peaks
                try:
                    Vmin = np.min(peak['pos'][peak['I']>0]) if Vmin is None else Vmin # Spec range for map
                except:
                    Vmin = None
                Vmax = np.max(peak['pos']) if Vmax is None else Vmax
            else: 
                Vmin = peak['spcRange'][0] if Vmin is None else Vmin
                Vmax = peak['spcRange'][1] if Vmax is None else Vmax
        else:
            try:
                Vmin = np.min(peak['I'][peak['I']>0]) if Vmin is None else Vmin  
            except:
                Vmin = None

        img = ax.imshow(peak[mode], extent=peak['FOV'], vmin=Vmin, vmax=Vmax)
        plt.colorbar(img, ax=ax, cax = self.format_colorbar(ax))
        ax.set_title(peak[mode + '_map_label'], fontsize = 16) # 'I_map_label'; 'pos_map_label'
        ax.set_xlabel('$x$ ' + peak['xy_unit'], fontsize = 16)
        ax.set_ylabel('$y$ ' + peak['xy_unit'], fontsize = 16)
        
        # add circle and letters to the maps
        #if peak['ID'] == 'Overview':
        #    return
        i = 1; rc = 1.2
        for sp in peak['points']:
            p_x, p_y = self.rc_to_xy(sp[0], sp[1])
            circle = Circle([p_x, p_y], rc, fill=False, linestyle='--', edgecolor='white')
            ax.add_patch(circle)
            txt = ax.text(p_x, p_y-rc, chr(ord('@')+i), color = 'white', ha='center', va='top', weight='bold',fontsize=16)
            txt.set_path_effects([PathEffects.withStroke(linewidth=1, foreground='k')])
            i += 1
    
    # plot curves
    def plot_curves(self, ax, peak, mode = 'spc', pmin = None, pmax = None, pkA = None, pkB = None):
        # spectra range for the x-y plot 
        
        if mode == 'spc':
            spec_width = (peak['spcRange'][1] - peak['spcRange'][0])/4
            pmin = peak['spcRange'][0] if pmin is None else pmin # Spec range for spectra
            pmax = peak['spcRange'][1] if pmax is None else pmax
        
        colors = sns.color_palette(self.color_palette, len(peak['points'])+1)
        ha = 'right' if peak['markpos'] == 'left' else 'left'
        
        if peak['ID'] == 'Overview':# Draw individual points for the overview spectrum
            ax.plot(self.x, peak['y'][0], color = colors[-1])
        else:
            i = 0; shift = 0
            for sp in peak['points']:
            # add spectra/annotation to the xy plot
                y = peak['y'][i]        
                ax.plot(self.x, y-shift, color = colors[i], label = chr(ord('@')+i+1))
                
                if peak['isCompPK'] != True: 
                    pkx = peak['pos'][sp[0],sp[1]]
                    pky = peak['maxI'][sp[0],sp[1]]-shift if peak['maxI'][sp[0],sp[1]] !=0 else y[0]
                else:
                    pkx = pkA['pos'][sp[0],sp[1]]
                    pky = pkA['maxI'][sp[0],sp[1]]-shift if pkA['maxI'][sp[0],sp[1]] !=0 else y[0]
                    pkxB = pkB['pos'][sp[0],sp[1]]
                    pkyB = pkB['maxI'][sp[0],sp[1]]-shift if pkB['maxI'][sp[0],sp[1]] !=0 else y[0]
                    if pkxB != 0:
                        ax.scatter(pkxB, pkyB, s=15, facecolors='none', edgecolors='black', alpha=0.8)

                if pkx != 0:
                    ax.scatter(pkx, pky, s=15, facecolors='none', edgecolors='black', alpha=0.8)
                
                if peak['isCompPK'] is True:
                    pktx = self.x[peak['spcIndice'][0]] if peak['markpos'] == 'left' else self.x[peak['spcIndice'][1]]
                else:
                    pktx = self.x[0] if peak['markpos'] == 'left' else self.x[-1]
                pkty = y[0]-shift if peak['markpos'] == 'left' else y[-1]-shift
                
                txt = ax.text(pktx, pkty, chr(ord('@')+i+1),color = 'black', ha= ha, va='bottom',weight='normal', fontsize=16) #weight='bold'
                # txt.set_path_effects([PathEffects.withStroke(linewidth=1, foreground='k')])
                shift = shift + (np.max(y) - np.min(y)) #can record this
                
                xs = peak['spcRange'][0] if pmin == None else pmin
                xe = peak['spcRange'][1] if pmax == None else pmax
                ax.axvspan(peak['spcRange'][0], peak['spcRange'][1], alpha=0.01, color='gray') # Range for analysing the peak
                ax.axvspan(xs, xe, alpha=0.01, color='blue') # range for showing the map/peak
                i += 1 # for the labels
        # Add peak name
        def get_note_xy(peak):
            if peak['title'] == 'Overview':
                row = int(self.Lines_per_Image/2); col = int(self.Points_per_Line/2)
                spy = peak['maxI'][row, col]
                spx = peak['pos'][row, col]
                return spx, spy
            
            for p in peak['points']:
                x = p[0]; y = p[1]
                if peak['I'][x,y] > 0:
                    spx = peak['pos'][x, y]
                    spy = peak['maxI'][x, y] # + peak['BK'][x,y] if self.isSmoothed is True else peak['maxI'][x,y]
                    return spx, spy
            spx = peak['pos'][0, 0]
            spy = peak['maxI'][0][0]
            return spx, spy
        
        if peak['isCompPK'] != True: 
            spx, spy = get_note_xy(peak)
            ax.text(spx, spy, peak['title'],color = 'black', ha= ha, va='top',weight='normal', fontsize=16) #weight='bold'
        else:
            spx, spy = get_note_xy(pkA)
            ax.text(spx, spy, pkA['title'],color = 'black', ha= 'left', va='top',weight='normal', fontsize=16) 
            spx, spy = get_note_xy(pkB)
            ax.text(spx, spy, pkB['title'],color = 'black', ha= 'right', va='top',weight='normal', fontsize=16) 
        
        ax.set_xlabel(peak['spc_x_label'], fontsize = 16)
        ax.set_ylabel(peak['spc_y_label'], fontsize = 16)
        #ax2.legend(loc='upper right', fancybox=True, framealpha=0.2)
        #ax.yaxis.set_ticklabels([])
            
        if peak['isCompPK'] is True:
            spec_width = (peak['spcRange'][1] - peak['spcRange'][0])/4
            ax.set_xlim([peak['spcRange'][0] - spec_width, peak['spcRange'][1]+ spec_width])
        
        if peak['refpeak'] is not None:
            ax.axvline(x = peak['refpeak'][0], color = 'black', linestyle = '--')
            ax.axvspan(peak['refpeak'][0]- peak['refpeak'][1], peak['refpeak'][0]+ peak['refpeak'][1], alpha=0.01, color='blue')
    
    # Plot peak structure - I/pos map and spectra of the selected points         
    def plot_peak(self, peak, mode = 'I', Imin=None, Imax = None, pmin=None, pmax=None, pkA = None, pkB = None):
        
        points = peak['points']
        
        fig, (ax0, ax1, ax2) = plt.subplots(1, 3, figsize = self.plotSize, gridspec_kw=self.plotRatio, constrained_layout=True)
        # fig.suptitle(peak['title'], fontsize=16)
        
        # plot I and pos map
        for para in zip([ax0, ax1], ['I', 'pos'], [Imin, pmin], [Imax, pmax]):
            self.plot_map(peak, ax=para[0], mode=para[1], Vmin=para[2], Vmax = para[3])

        self.plot_curves(ax2, peak, pmin = pmin, pmax = pmax, pkA = pkA, pkB = pkB)
        
        # plot spectra
        peak['pointProfile']=self.list_points(peak)
        return peak
    
    # Plot line profile
    def plot_lineprofile(self, peak, pmin=None, pmax=None):
        
        points = peak['points']

        fig, ax = plt.subplots(2, 2, figsize = (self.plotSize[0],self.plotSize[1]*2), gridspec_kw={'width_ratios': [1, 2]}, constrained_layout=True)
        
        self.plot_map(peak, ax=ax[0,0], mode='I')
        self.plot_map(peak, ax=ax[1,0], mode='pos')
        
        # Calculate/mark the coordinates of the start and end points
        start = points[0]; end = points[-1]
        sx, sy = self.rc_to_xy(start[0], start[1])
        ex, ey = self.rc_to_xy(end[0], end[1])
        ax[0,0].plot([sx, ex], [sy, ey], marker = 'o', linestyle='dotted', color="white")
        ax[0,1].plot(peak['ls_x'], peak['ls_I'], marker = 'o', linestyle='dotted')
        ax[1,0].plot([sx, ex], [sy, ey], marker = 'o', linestyle='dotted', color="white")
        ax[1,1].plot(peak['ls_x'], peak['ls_pos'], marker = 'o', linestyle='dotted')

        
        # Add marks in the line profiles
        ymin, ymax = ax[0,1].get_ylim()
        txtpyI = (ymin+ymax)/2
        ax[0,1].text(peak['ls_x'][0], txtpyI, 'A', ha='center', va='top', weight='bold',fontsize=16)
        ax[0,1].text(peak['ls_x'][-1], txtpyI, chr(ord('@')+len(peak['points'])), ha='center', va='top', weight='bold',fontsize=16)
        ax[1,1].set_ylim([pmin, pmax])
        ymin, ymax = ax[1,1].get_ylim()
        txtpyPos = (ymin+ymax)/2
        ax[1,1].text(peak['ls_x'][0], txtpyPos, 'A', ha='center', va='top', weight='bold',fontsize=16) 
        ax[1,1].text(peak['ls_x'][-1], txtpyPos, chr(ord('@')+len(peak['points'])), ha='center', va='top', weight='bold',fontsize=16) 
        
        ax[0,0].title.set_text(peak['I_ls_ylabel'])
        ax[0,1].set_xlabel('Position' + peak['xy_unit'], fontsize = 16)
        ax[0,1].set_ylabel(peak['I_ls_ylabel'], fontsize = 16)
        
        ax[1,0].title.set_text(peak['pos_ls_ylabel'])
        ax[1,1].set_xlabel('Position' + peak['xy_unit'], fontsize = 16)
        ax[1,1].set_ylabel(peak['pos_ls_ylabel'], fontsize = 16)
        return peak
    
    # ========= Peaks: maps ========================
    # Convert the spec positions (xRange) into corresponding indice of the f.y[index] array
    def xRange_To_yIndice(self, xRange):
        start = np.abs(self.x - xRange[0]).argmin()
        end = np.abs(self.x - xRange[1]).argmin()
        return [start, end] if self.mode != 'PLe' else [end, start]
    
    # Choose spec ranges for a known peak
    def select_xRange(self, spcRange=None, bkRange=None):
        if spcRange is None:
            spcRange = [self.x[0], self.x[-1]]
        indice = self.xRange_To_yIndice(spcRange)
        bkRange = spcRange if bkRange is None else bkRange
        bkIndice = self.xRange_To_yIndice(bkRange)
        return {'spcRange':spcRange, 'spcIndice': indice, 'bkRange':bkRange, 'bkIndice':bkIndice}
    
    # Get spectra for a selected point
    def get_spectra(self, row, col):
        index = col + row*self.Points_per_Line
        spectrum = self.spc.sub[index].y
        return spectrum
    
    def rc_to_xy(self, row, col):
        x = self.Scan_Origin_X+col*self.Scan_Width/self.Points_per_Line #sp[1] - col/x; sp[0] - row/y
        y = self.Scan_Height+self.Scan_Origin_Y-row*self.Scan_Height/self.Lines_per_Image
        return x, y
    
    # Process individual peaks
    def process_peak(self, data, peak):
        """
        data: the spectra, f.sub[index].y
        peak: the dictionary, generated by select_XRange
        mode: 'i' intensity; 'p' peak position
        """
        y = data[peak['spcIndice'][0]:peak['spcIndice'][1]]
        bk_input = data[peak['bkIndice'][0]:peak['bkIndice'][1]]
        
        # Smooth data
        if self.isSmoothed is True:
            y = savgol_filter(y, len(y), self.smooth_order)  
            
        nPoints = len(y)
        if peak['spcIndice'][0]==peak['bkIndice'][0] and peak['spcIndice'][1]==peak['bkIndice'][1]:
            bk = y[0]+ (y[-1]-y[0])*range(0, nPoints)/nPoints # Use a linear background
        else:
            bk = range(0, nPoints)*sum(bk_input)/len(bk_input)
            
        I = sum(y - bk)
        
        if I > peak['I_cri']:
            peakIndex = y.argmax() + peak['spcIndice'][0]
            pos = self.x[peakIndex] 
            maxI = data[peakIndex] # - peak['BK'][peakIndex]
            background = bk[y.argmax()]
        else:
            I = 0
            pos = 0
            maxI = 0
            background = 0
        return I, pos, maxI, background
        
         
    # Create maps
    def generate_map(self, peak):
        """
        peak: the dictionary defined by select_range
        mode: 'i' - integrated intensity; 'p' - peak position
        """
        # Initialise the map data
        peak['I']  = np.empty(self.imgRes, np.float32)
        peak['pos'] = np.empty(self.imgRes, np.float32)
        peak['maxI'] = np.empty(self.imgRes, np.float32)
        peak['BK'] = np.empty(self.imgRes, np.float32)
        peak['refI'] = np.empty(self.imgRes, np.float32)
        peak['offset'] = np.empty(self.imgRes, np.float32)
        
        for row in range(self.Lines_per_Image):
            for col in range(self.Points_per_Line):
                # Calculate index in the y array; the scan runs vertically here:
                # Image[row, col]: row - y, vertical; col - x, horitontal
                spectrum = self.get_spectra(row, col)
                [I, pos, maxI, background] = self.process_peak(spectrum, peak)
                peak['I'][row, col] = I
                peak['pos'][row, col] = pos
                peak['maxI'][row, col] = maxI
                peak['BK'][row, col] = background
                peak['refI'][row, col] =  self.refI[col + row*self.Points_per_Line]
                peak['offset'][row, col] = self.offset[col + row*self.Points_per_Line]
        return peak   
    
    # Create a peak dictionary and calculate/draw/save Intensity and position maps
    def create_peak(self, title, spcRange = None, bkRange=None, I_cri = None, markpos = 'left', plotpeak = True):
        # Set intensity criteron for peak recognation - if the overall intensity is less than I_cri, assign 0 for the point

        # set ranges
        if spcRange is None:
            spcRange = np.sort([self.x[0], self.x[-1]])
            
        # Generate Peak ID using the title, remove all latex formatting characters
        for ch in ['$', '_', '{', '}', '^']:
            pk_ID = title.replace(ch, '')
        pk_ID = pk_ID.replace(' ', '_')
            
        # Generate filename for the peak
        pk_filename = self.file + '_' + pk_ID + '-' + "{:.2f}".format(spcRange[0]) + '_' + "{:.2f}".format(spcRange[-1]) + '_Icr-' + "{:.2f}".format(self.I_cri) + '.pkm'
   
        try:
            with open(pk_filename, 'rb') as handle:
                peak = pickle.loads(handle.read())
            print('Use data from file: ' + pk_filename)
        except:
            print('Generate new data')
            peak = self.select_xRange(spcRange=spcRange, bkRange=bkRange)
            
            peak['title'] = title
            peak['ID'] = pk_ID
            peak['filename'] = pk_filename
            peak['refpeak'] = self.refpeak
            peak['isCompPK'] = False
            peak['I_cri'] = self.I_cri if I_cri is None else I_cri 
            
            # Peak units
            peak['spc_x_label'] = self.spc_x_label + self.spc_x_unit
            peak['spc_y_label'] = self.spc_y_label + self.spc_y_unit

            peak['xy_unit'] = self.xy_unit
            peak['I_map_label'] = 'Integrated intensity' + self.spc_y_unit
            peak['pos_map_label'] = 'Peak position' + self.spc_x_unit
            
            peak['I_ls_ylabel'] = peak['spc_y_label']
            peak['pos_ls_ylabel'] = peak['spc_x_label']
            
            peak['markpos'] = markpos
            peak['x'] = self.x
            peak['FOV'] = self.FOV
            
            # Generate 'I' and 'pos' field
            peak = self.generate_map(peak)
            
            # Generate data for xy plot
            if peak['ID'] =='Overview':
                row = int(self.Lines_per_Image/2); col = int(self.Points_per_Line/2)
                peak['points'] = [[row, col]]
                
                peak['y'] = np.zeros((len(peak['points']), len(self.x)))
                I = np.zeros_like(self.spc.sub[0], dtype='f')
                for data in self.spc.sub:
                    I = I + data.y
                peak['y'][0:] = I
                peak['maxI'][row, col]= np.max(I) #np.sum(peak['maxI']) if self.refpeak is not None else np.max(I)
                peak['pos_map_label'] = 'Max peak' + self.spc_x_unit
                if self.isSavefile is True:
                    self.save_peak(peak)
            else:
                peak['points'] = self.points # points selected from the map, i.e. physical position of the sample
                peak['y'] = np.zeros((len(peak['points']), len(self.x)))
                i = 0 # label for the points
                for sp in peak['points']:
                    peak['y'][i]= self.get_spectra(sp[0], sp[1]) # raw data
                    i += 1
            # peak = self.linescan(peak)
            
        if plotpeak is True:
            self.plot_peak(peak)
            
        return peak
            
    # save_peak
    def save_peak(self, peak):
        with open(peak['filename'], 'wb') as handle:
                pickle.dump(peak, handle)
    
    def load_peak(self, peakfile):
        try:
            with open(peakfile, 'rb') as handle:
                peak = pickle.loads(handle.read())
        except:
            print('I cannot find the file: ' + peakfile)
    
    # ======= Select/processing points =====================
    # Read the png file and select data point from the map
    def select_points(self, peak, mode = 'I', pkA = None, pkB = None):
        # Clear the existing points
        self.points = np.empty((0,2), np.uint8) # coordinates of the added points, as array index
        self.nPoints = 0
        imgRange = np.max(peak[mode])-np.min(peak[mode])
        img = (peak[mode]-np.min(peak[mode]))/imgRange if imgRange != 0 else 0

        def draw_circle(event, x,y, flags, param):
            global mouseX, mouseY
            if event ==cv2.EVENT_LBUTTONDOWN:
                r = 3
                cv2.circle(img, (x,y), r, (255,255,255), 2)
                Mark = chr(ord('@')+ self.nPoints +1)
                self.nPoints += 1
                cv2.putText(img, Mark, (x+r+1, y-r-1), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255),2)
                col, row = x, y # x-col; y-row
                self.points = np.append(self.points, np.array([[row, col]]), axis =0) # the point is described as [row, col]
        
        window = peak['ID']+'_' + mode
        cv2.namedWindow(window, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(window, draw_circle)

        while(1):
            cv2.imshow(window, img)
            k = cv2.waitKey(20) & 0xFF
            if k== 27:
                cv2.destroyAllWindows()
                cv2.waitKey(1)
                break
            elif k == ord('d'):
                img = (peak[mode]-np.min(peak[mode]))/imgRange if imgRange != 0 else 0
                self.points = np.empty((0,2), np.uint8)
                self.nPoints = 0
            
        if self.nPoints == 0: # if no selection, add the default points
            self.points = np.append(self.points, np.array([[min(15, self.Points_per_Line-1), min(15,self.Lines_per_Image-1)]]), axis =0)
            self.points = np.append(self.points, np.array([[max(0,self.Points_per_Line-15), max(0,self.Lines_per_Image-15)]]), axis =0)
                
        peak_marked = peak.copy()
        peak_marked['ID'] = peak['ID'] + '_marked'
        peak_marked['filename'] = peak['filename']+'_' + mode + "_marked.pkm"
        peak_marked['points'] = self.points
        peak_marked['y'] = np.zeros((len(peak_marked['points']), len(self.x)))
        i = 0 # label for the points
        for sp in peak_marked['points']:
            peak_marked['y'][i]= self.get_spectra(sp[0], sp[1]) #  - peak_marked['BK'] # [row, col] = [y, x] of mouse points
            i += 1
        self.plot_peak(peak_marked, pkA = pkA, pkB = pkB)
        return peak_marked
    
    def linescan(self, peak, mode = 'I', points = None, pkA = None, pkB = None):
        if points == 'new':
            peak = self.select_points(peak, mode, pkA = pkA, pkB = pkB)
        
        points = peak['points']
        
        if len(points) < 2:
            print('Please choose at lease 2 points')
            return {}
        
        # Linescan from the point selected
        start = points[0]; end = points[-1]
        Nx = abs(end[0] - start[0]) + 1; Ny = abs(end[1] - start[1]) + 1
        xstep = 1 if start[0]<end[0] else -1
        ystep = 1 if start[1]<end[1] else -1
        dx = np.arange(start[0], end[0]+xstep, step = xstep)
        dy = np.arange(start[1], end[1]+ystep, step = ystep)
        if Nx > Ny:
            x = np.arange(start[0], end[0]+xstep, step = xstep) # set data points for position
            line_I = np.ones_like(x, dtype='f')
            line_pos = np.ones_like(x, dtype='f')
            distance = np.ones_like(x, dtype='f')

            y = np.ones_like(x, dtype='int')*start[1]   
            if start[1]==end[1]:
                for i in range(Nx):
                    line_I[i] = peak['I'][y[i], x[i]] # sees right this way, from images
                    line_pos[i] = peak['I'][y[i], x[i]]
            else:   
                step_y = (end[1]-start[1])/(Nx-1)
                y = np.arange(start[1], end[1]+step_y, step = step_y)

                for i in range(Nx-1):
                    closest = np.abs(dy - y[i]).argmin() 
                    index = closest-1 if (dy[closest]-y[i])*ystep > 0 else closest
                    w = y[i]- dy[index]
                    line_I[i] = (1-w)*peak['I'][dy[index], x[i]] + w*peak['I'][dy[index+1], x[i]]
                    line_pos[i] = (1-w)*peak['pos'][dy[index], x[i]] + w*peak['pos'][dy[index+1], x[i]]
                line_I[Nx-1]=peak['I'][dy[Ny-1],x[Nx-1]]
                line_pos[Nx-1]=peak['pos'][dy[Ny-1],x[Nx-1]]
        else:
            y = np.arange(start[1], end[1]+ystep, step = ystep)
            line_I = np.ones_like(y, dtype='f')
            line_pos = np.ones_like(y, dtype='f')
            distance = np.ones_like(y, dtype='f')

            x = np.ones_like(y, dtype='int')*start[0]
            if start[0]==end[0]:
                for i in range(Ny):
                    line_I[i] = peak['I'][y[i], x[i]] # sees right this way, from images
                    line_pos[i] = peak['pos'][y[i], x[i]]
            else:   
                step_x = (end[0]-start[0])/(Ny-1)
                x = np.arange(start[0], end[0]+step_x, step = step_x)

                for i in range(Ny-1):
                    closest = np.abs(dx - x[i]).argmin() 
                    index = closest-1 if (dx[closest]-x[i])*xstep > 0 else closest
                    w = x[i]- dx[index]
                    line_I[i] = (1-w)*peak['I'][y[i], dx[index]] + w*peak['I'][y[i], dx[index]]
                    line_pos[i] = (1-w)*peak['pos'][y[i], dx[index]] + w*peak['pos'][y[i], dx[index]]
                line_I[Ny-1]=peak['I'][y[Ny-1],dx[Nx-1]]
                line_pos[Ny-1]=peak['pos'][y[Ny-1],dx[Nx-1]]

        x_unit = float(self.Scan_Width/self.Points_per_Line)**2
        y_unit = float(self.Scan_Height/self.Lines_per_Image)**2
        for i in range(max(Nx,Ny)):
            distance[i]=np.sqrt((x[i]-start[0])**2*x_unit+(y[i]-start[1])**2*y_unit)   
        
        peak['ls_x'] = distance
        peak['ls_I'] = line_I
        peak['ls_pos'] = line_pos
        
        self.plot_lineprofile(peak)
        return peak

    
    def compare_pks(self, pkA, pkB):
        # put peak with larger position first
        spc_s = min(pkA['spcRange'][0], pkB['spcRange'][0])
        spc_e = max(pkA['spcRange'][1], pkB['spcRange'][1])

        pkNote = pkA['ID'] + '_vs_' + pkB['ID']
        peak = self.create_peak(pkNote, spcRange = [spc_s, spc_e], plotpeak = False)

        peak['I'] = np.divide(pkA['I'], pkB['I'], out=np.zeros_like(pkA['I']), where=pkB['I']!=0)
        peak['pos'] = np.subtract(pkA['pos'], pkB['pos'], out=np.zeros_like(pkA['pos']), where= pkB['pos']!=0)
        peak['pos'][peak['pos']<0]=0
        # peak['pos'][peak['pos']<0]=0

        peak['I_ls_ylabel'] = 'peak ratio'
        peak['pos_ls_ylabel'] = 'peak difference'
        peak['I_map_label'] = ' intensity ratio'
        peak['pos_map_label'] = 'peak difference '
        peak['isCompPK'] = True
        self.plot_peak(peak, pkA = pkA, pkB = pkB) 

        return peak
    