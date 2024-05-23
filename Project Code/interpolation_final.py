import numpy as np
import re
from scipy.interpolate import griddata

# Global variables
# Directories
FILTER_DIRECTORY = r"C:\Users\Adam\Desktop\Bachelor\Filtre handpicked"
FILTER_DIRECTORY_MAIN_L = r"C:\Program Files\EqualizerAPO\config\L Placeholder.txt"
FILTER_DIRECTORY_MAIN_R = r"C:\Program Files\EqualizerAPO\config\R Placeholder.txt"
# Misc
ALPHABET_CAPS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" #Use to translate num to alphabet

# Markers
MARKER_AMOUNT_X = 5
MARKER_AMOUNT_Y = 5

MARKER_DIST_X = 0.6175
MARKER_DIST_Y = 0.5
MARKER_DIST_START_Y = 1.0

# Interpolation specific
RESOLUTION = 199

# Filter specific
FREQUENCIES = [69,90,110,118,126,131,141,147,153,165,175,199,225,350,620,1000,3000,6000,10000,16000]
FILTER_AMOUNT = len(FREQUENCIES)

def dict_num_to_alphabet():
    num_to_alpha = {}
    for i, j in zip(range(len(ALPHABET_CAPS)), ALPHABET_CAPS):
        num_to_alpha[i] = j 
    return num_to_alpha

def find_closest_filter(x_coord_found,y_coord_found,x_coordinates,y_coordinates): # Finds closest x and y-value
    closest_x = (np.abs(x_coordinates - x_coord_found)).argmin()
    closest_y = (np.abs(y_coordinates - y_coord_found)).argmin()
    closest_pooled = [closest_x, closest_y]
    print("Closest x- and y-coordinate is found.")
    return closest_pooled
  
def create_coordinate_spaces(): # Creates x, y for the system an interpolation
    x = np.linspace(-((MARKER_DIST_X*MARKER_AMOUNT_X)/2), 
                    (MARKER_DIST_X*MARKER_AMOUNT_X)/2, 
                    MARKER_AMOUNT_X) # Assumes symmetry for speaker rotation
    y = np.linspace(MARKER_DIST_START_Y, 
                    MARKER_DIST_START_Y+MARKER_DIST_Y*(MARKER_AMOUNT_Y-1), 
                    MARKER_AMOUNT_Y)

    # New points, "resolution" of interpolation. 
    xi = np.linspace(-((MARKER_DIST_X*MARKER_AMOUNT_X)/2), 
                    (MARKER_DIST_X*MARKER_AMOUNT_X)/2, 
                    RESOLUTION) # Assumes symmetry for speaker rotation
    yi = np.linspace(MARKER_DIST_START_Y, 
                     MARKER_DIST_START_Y+MARKER_DIST_Y*(MARKER_AMOUNT_Y-1), 
                     RESOLUTION)
    
    coordinates_pooled = [x,y,xi,yi]

    print("Coordinates created.")
    return coordinates_pooled

def extract_filters_from_txt(): # Gives us a juicy array of all the filters from text docs
    num_to_alpha = dict_num_to_alphabet()
    filter_array_gain_l = np.full((FILTER_AMOUNT,MARKER_AMOUNT_Y,MARKER_AMOUNT_X),0.0) # Split l and r for ease
    filter_array_gain_r = np.full((FILTER_AMOUNT,MARKER_AMOUNT_Y,MARKER_AMOUNT_X),0.0) 

    filter_array_q_l = np.full((FILTER_AMOUNT,MARKER_AMOUNT_Y,MARKER_AMOUNT_X),0.0) # Split gain and q to keep my sanity
    filter_array_q_r = np.full((FILTER_AMOUNT,MARKER_AMOUNT_Y,MARKER_AMOUNT_X),0.0)

    filter_grouped_gain = [filter_array_gain_l, filter_array_gain_r]
    filter_grouped_q = [filter_array_q_l, filter_array_q_r]

    for y in range(MARKER_AMOUNT_Y): # This here is done to make gridding easier, aka makes a 5x5 grid
        for x in range(MARKER_AMOUNT_X):
            # Logical ex: x goes to 5 (ABCDE), then loops back to 0 and y goes to 1 for next line (FGHIJ)
            # y is multiplied by 5 to increment the letters easier
            updated_filter_dir_l = FILTER_DIRECTORY + "\\L" + num_to_alpha[y*MARKER_AMOUNT_Y+x] + ".txt" 
            updated_filter_dir_r = FILTER_DIRECTORY + "\\R" + num_to_alpha[y*MARKER_AMOUNT_Y+x] + ".txt"
            
            with open(updated_filter_dir_l, "r") as left_file: # Left side grouped by line, "left_file[0] is 1st line"
                left_lines = left_file.readlines()
            
            with open(updated_filter_dir_r, "r") as right_file: # Right side grouped by line
                right_lines = right_file.readlines()

            lines = [left_lines, right_lines] 

            for i in range(2): # Transfers the filter from txt file to array
                filter_line_start = 1 
                # Starts with 1 since first line contains "Filter". 
                # We also have to check where to start just in case extra lines are added in the filter.
                while True:
                    if "Filter" in lines[i][filter_line_start]:
                        break # Stops the while loop when "Filter" is found and stops incrementing
                    filter_line_start += 1 
                
                for j in range(FILTER_AMOUNT): # Here we make filters line by line as an array
                        gain_value = 0
                        q_value = 0
                        
                        if "None" not in lines[i][filter_line_start+j]: # Skips this filter and stays at 0 
                            gain_match = re.search("Gain(.*)dB",lines[i][filter_line_start+j])
                            gain_value = float(gain_match.group(1).strip())

                            q_match = re.search("Q(.*)",lines[i][filter_line_start+j])
                            q_value = float(q_match.group(1).strip())

                        # i chooses l or r, j chooses which filter plane we are on, 
                        #y chooses height from speaker, x chooses row
                        filter_grouped_gain[i][j][y][x] = gain_value
                        filter_grouped_q[i][j][y][x] = q_value
    filter_grouped = [filter_grouped_gain, filter_grouped_q]
    print("Filters extracted from text documents.")
    return filter_grouped # First call will be gain or q, second will be l or r, and third will be the filter num plane

def bicubic_interpolation_one_plane(array_of_plane, x_coords, y_coords, xi_coords, yi_coords): # Only insert one plane(ex: only filter1)
            # Has to be a set distance between markers for this code.
            # Create grid coordinates for the original data
            X, Y = np.meshgrid(x_coords, y_coords)
            points = np.array([X.flatten(), Y.flatten()]).T
            values = array_of_plane.flatten()
 
            # Create grid coordinates for the interpolated data
            Xi_coords, Yi_coords = np.meshgrid(xi_coords, yi_coords)
            i_points = np.array([Xi_coords.flatten(), Yi_coords.flatten()]).T

            # Interpolate using griddata
            znew = griddata(points, values, i_points, method='cubic')
            print(znew)
    
            

def bicubic_interpolation_all_planes(filter_array, x, y, xi, yi):
    # These could have been made from the beginning, but that makes code harder to read.
    i_filter_array_gain_l = np.full((FILTER_AMOUNT,RESOLUTION,RESOLUTION),0.0)
    i_filter_array_gain_r = np.full((FILTER_AMOUNT,RESOLUTION,RESOLUTION),0.0)
    i_filter_array_gain = [i_filter_array_gain_l, i_filter_array_gain_r]

    i_filter_array_q_l = np.full((FILTER_AMOUNT,RESOLUTION,RESOLUTION),0.0)
    i_filter_array_q_r = np.full((FILTER_AMOUNT,RESOLUTION,RESOLUTION),0.0)
    
    i_filter_array_q = [i_filter_array_q_l, i_filter_array_q_r]
    i_filter_array = [i_filter_array_gain, i_filter_array_q]
    
    # We're going to read each value
    for i in range(2): # gain or q
        for j in range(2): # l or r
            for k in range(FILTER_AMOUNT): # which filter layer
                # Here the filters are being made

                i_filter_array[i][j][k] = bicubic_interpolation_one_plane(filter_array[i][j][k],x, y, xi, yi)
    print("Filters have been sucessfully interpolated.")
    return i_filter_array

def create_filter_txt_doc(xy_of_array, filter_array): # Creates the filter ready to be made into a text document
    # The x and y is for the array itself, not the "real" xy
    # x and y has to be in an array

    filter_l = ['Filter Settings file\n',
                        '\n', 'Room EQ V5.31.1\n',
                          'Dated: Mar 21, 2024 3:51:14 PM\n',
                            '\n', 'Notes:\n', 'Channel: L\n',
                              'Equaliser: Generic\n','R F Apr 24\n']
    filter_r = ['Filter Settings file\n',
                        '\n', 'Room EQ V5.31.1\n',
                          'Dated: Mar 21, 2024 3:51:14 PM\n',
                            '\n', 'Notes:\n', 'Channel: R\n',
                              'Equaliser: Generic\n','R F Apr 24\n']
    filter_combined = [filter_l, filter_r] # Makes loop good

    for i in range(FILTER_AMOUNT): 
        for j in range(2): # l and r
            frequency = FREQUENCIES[i]
            # indexes: gain/q, l/r, filter plane, y, x
            gain = round(filter_array[0][j][i][xy_of_array[1]][xy_of_array[0]], 2)
            q = round(filter_array[1][j][i][xy_of_array[1]][xy_of_array[0]], 3)
            if q < 0.0:
                q = 0.0
            #filter_line_template = f"Filter  {str(i+1)}: ON  PK       Fc   {frequency} Hz  Gain  {gain} dB  Q  {q}\n"  

            if gain == 0 and q == 0:
                filter_line_template = f"Filter {str(i+1)}: ON None"
                filter_combined[j].append(filter_line_template)    
            else:
                filter_line_template = f"Filter {str(i+1)}: ON PK Fc {frequency} Hz Gain {gain} dB Q {q}\n"  
                filter_combined[j].append(filter_line_template)  
    
    
    with open(FILTER_DIRECTORY_MAIN_L, "w") as file_l:
        file_l.write("".join(filter_combined[0]))

    with open(FILTER_DIRECTORY_MAIN_R, "w") as file_r:
        file_r.write("".join(filter_combined[1]))
    
    print("Filters have been applied to speakers.")

def main():
    coordinate_spaces = create_coordinate_spaces()
    x = coordinate_spaces[0]
    y = coordinate_spaces[1]
    xi = coordinate_spaces[2]
    yi = coordinate_spaces[3]

    filters = extract_filters_from_txt()
    i_filters = bicubic_interpolation_all_planes(filters, x,y,xi,yi)

    while True:
        print("Normal or interpolated (n/i)? 'q' to quit: ")
        filter_choice = input()
        
        if filter_choice == "i":
            print("x-coordinate: ")
            found_this_x = float(input())

            print("y-coordinate: ")
            found_this_y = float(input())

            closest_xy = find_closest_filter(found_this_x, found_this_y, xi, yi)
            print(closest_xy)
            create_filter_txt_doc(closest_xy, i_filters)
        
        elif filter_choice == "n":
            print("x-coordinate: ")
            found_this_x = float(input())

            print("y-coordinate: ")
            found_this_y = float(input())

            closest_xy = find_closest_filter(found_this_x, found_this_y, x, y)
            print(closest_xy)
            create_filter_txt_doc(closest_xy, filters)
            
        else:
            print("Terminating program. Have a nice day!")
            return()
       
main()