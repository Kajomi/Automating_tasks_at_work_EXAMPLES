#************************************************************
# -*- coding: cp1252 -*-
#************************************************************
#-------------------------------------------------------------------------------
# Name:        Visual_Surface_Segment_obst.py
#
# Purpose:     Processing the flight obstacles within a certain area that penetrate
#              a pregiven surface height and thus can be hazardous to flight operations.
#
#              The data comes in a text file for each area separately and has varying
#              number of flight obstacles. The input text file consists of standard
#              information that does not vary between different text files.
#
#              In order to have a CSV -file with all obstacles and coordinates in
#              decimal degrees - two functions are introduced in this Python script.
#              The first, convert_txt_to_df(), processes the input txt-file and returns
#              a pandas DataFrame that will be further processed with the second
#              function, convert_to_DesDeg(). The second function returns a CSV-file.
#
# Author:      Mira Kajo - Summer 2018
#
#-------------------------------------------------------------------------------

# Import necessary modules
import pandas as pd
import arcpy
import itertools
import csv

def convert_txt_to_df(input_fp):
    '''
    The purpose of this function is to clean and process an text -file that contains
    information on obstacles that penetrate a surface segment in certain height, and
    thus can be hazards to flight operations within the area.

    After the text file is processed, the list of lists is converted into pandas
    DataFrame.

    PARAMETERS
    ----------
    The function requires one parameter - the filepath for the input text-file.

    RETURNS
    -------
    The function returns a pandas DataFrame that contains, the data of the flight
    obstacles that are now ready to be processed more efficiently.
    '''
    # Open the input file and loop through the text file
    with open(fp, 'r') as ins:
        array = []
        count = 37

        # Skip the first 40 lines as they are not needed and are standard in all files
        # Count the number of lines in the first section of the text file (this number
        # is the same as the latter part of the file that we are interested in
        for line in itertools.islice(ins, 40, None):
        # Count lines till there is an empty line
            if line == '\n':
                break
            else:
                count += 1
                # Select all the rows in the latter part according to the count done before
                for line2 in itertools.islice(ins, count, None):
                    cond = '---------------------------------------------------------------------------'
                    cond2 = '--------------------------------------------------------------------------'
                    if cond in line2:
                        continue
                    if cond2 in line2:
                        continue

                    # As the data has whitespaces between items that belong together
                    # and between separate items, as well as some extra items that
                    # do not match with the headers, etc, some extra cleaning is needed!

                    # remove extra whitespaces, and add commas between items
                    line3 = ' '.join(line2.split())
                    line3 = line3.replace(' ', ',')

                    # Check which items are digits and which are strings
                    lst_int = [int(x) if x.isdigit() else x for x in line3.split(',')]

                    # Add to the list
                    array.append(lst_int)

    # Iterate each list within the array one by one
    for lst in array:
        # Skip the first row (Header)
        if lst == ['Dist', 'Trk', 'N', 'E', 'H(ft)', 'T', 'Nimi', 'Id']:
            continue
        # Remove the first item from every list and join the items consisting
        # the 'Nimi' column together (nimi translates to name)
        else:
            lst.pop(0)
            lst[6:8] = [''.join(lst[6:8])]

    # Pop out the headers of the data into its own variable
    headers = array.pop(0)
    # Create a pandas DataFrame from the array and add headers as column names
    vss_df = pd.DataFrame(array, columns = headers)
    print(vss_df)

    return vss_df



def convert_to_DecDeg(data, output_csv):
    '''
    This function takes pandas DataFrame as input and converts coordinates into
    decimal degrees. The results are saved in a CSV -file from where they can be
    added to ArcMAp with AddXY -tool.

    PARAMETERS
    ----------
    Takes two parameters - First, a dataFrame created with the convert_txt_to_df()
    -function and second, an output CSV -file, where results will be saved.

    RETURNS
    -------
    An CSV -file with new columns for coordinates in decimal degrees (columns
    'Latitude' and 'Longitude', and string versions of the original coordinates
    N and E.
    '''
    # Create empty columns for Lat and Lon values
    data['Latitude'] = None
    data['Longitude'] = None
    # Convert existing coordinates to strings
    data['N_str'] = data['N'].astype(str)
    data['E_str'] = data['E'].astype(str)

    # Iterate over the rows in order to slice degrees, minutes and seconds
    for idx, row in data.iterrows():
        N_deg = row['N_str'][0:2]
        N_min = row['N_str'][2:4]
        N_sec = row['N_str'][4:6]

        E_deg = row['E_str'][0:2]
        E_min = row['E_str'][2:4]
        E_sec = row['E_str'][4:6]

        # Calculate the Decimal Degree values for both N and E
        dd_N = float(N_deg) + (float(N_min) / 60) + (float(N_sec) / 3600)
        dd_E = float(E_deg) + (float(E_min) / 60) + (float(E_sec) / 3600)

        # Save the decimal degree values in proper column and row
        data.loc[idx, 'Latitude'] = dd_N
        data.loc[idx, 'Longitude'] = dd_E

    #print(data)
    data.to_csv(output_csv, sep=',', index=False)


# ==============================================================================

# Set input and output filepaths
fp = r"C:Path_to_input_file\EFKE_VSS_36.txt"
output_csv = r'C:Path_to_output_file\coordinates_DataFrame.csv'

# Run both functions in right order
data_df = convert_txt_to_df(fp)
convert_to_DecDeg(data_df, output_csv)


print('DATA PROCESSING IS READY!')























