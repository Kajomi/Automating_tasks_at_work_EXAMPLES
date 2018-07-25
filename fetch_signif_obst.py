#************************************************************
# -*- coding: cp1252 -*-
#************************************************************
#-------------------------------------------------------------------------------
# Name:        fetch_signif_obst.py
#
# Purpose:     This script fetches all the flight obstacles from perusparannus
#              2018 data that are meant to be deleted from LER, marked as ready
#              ('yes') and are 100 meters or higher.
#
#              It consists of two functions: get_filepaths_as_list() and
#              get_deleted_obst() - functions. The script returns only one CSV -
#              file that contains information from all of Finland.
#
# Author:      Mira Kajo - Spring 2018
#
#-------------------------------------------------------------------------------

# Importing the necessary modules
import arcpy
import arcpy.da as da
import os
import csv
from datetime import datetime


# ==============================================================================

#                            DEFINE FUNCTIONS

# ==============================================================================


def get_filepaths_as_list():

    '''
    This function walks throug the root folder and its subfolders, fetching
    specific geodatabases and rows of data. It then creates a list of filepaths
    and returns it.

    PARAMETERS:
    -----------
        No input parameters required

    RETURNS:
    --------
        A list of filepaths
    '''

    # Define the source workspace
    spath = r'I:\GIS\Filepath_to_first_GDBs\INPUT_FOLDER'

    # Create an empty list
    aerodrome_list = []

    # Iterate over source workspace, subfolders and files and add to list
    for root, dirnames, filenames in da.Walk(spath, datatype='FeatureClass'):
        for filename in filenames:
            if filename.startswith('E'):
                newPath = os.path.join(root, filename)
                aerodrome_list.append(newPath)

    # Note: 'AUTOMAATTISET' and 'SQL' folders are excluded! Otherwise the length would be 39.
    #print('The length of the list is: ', len(aerodrome_list))   # Returns 37
    return aerodrome_list


def get_deleted_obst(workspace, output_csv):

    '''
    This function fetches rows of data that are marked with specific command,
    which means they are going to be deleted from LER. After fetching the
    specific rows it writes a CSV-file of the data.

    The function requires the use of get_filepaths_as_list() - function as an
    workspace parameter to loop over, so that one can fetch data from all folders
    (airports) at once.

    PARAMETERS:
    -----------
        A list of filepaths from get_filepaths_as_list() - function, an output
        CSV filepath.

    RETURNS:
    --------
        An CSV file with deleted flight obstacles that will be deleted from LER.
    '''

    # Open the output file and write data into it
    with open(output_csv, 'wb') as out_csv:
        writer = csv.writer(out_csv)
        writer.writerow(['OBST_ID', 'TYPE', 'AGL_M_M', 'READY', 'RETURN_CODE', 'PROCEDURE', 'SEGMENT', 'COORD_N', 'COORD_E' ])

        # Initialize the SQL statement
        sql = "(PROCEDURE = 'remove' OR PROCEDURE = 'dismantle' OR PROCEDURE = 'Out of date') AND (READY = 'yes' AND AGL_M_M >= 100)"

        # Loop over all filepaths one by one
        for fpath in workspace:
            print('processing: %s' % fpath)

            # Create a SearchCursor
            cursor = arcpy.SearchCursor(fpath, sql)

            # Iterate over the feature class provided as input
            for rivi in cursor:

                out_ID = str(rivi.ID)
                out_type = str(rivi.TYPE)
                out_agl = str(rivi.AGL_M_M)
                out_ready = rivi.READY.encode('latin-1')
                out_return = str(rivi.RETURN_CODE)
                out_procedure = str(rivi.PROCEDURE).encode('latin-1')
                out_segment = rivi.SEGMENT.encode('latin-1')
                coord_n = rivi.COORD_N
                coord_e = rivi.COORD_E

                data = [out_ID, out_type, out_agl, out_ready, out_return, out_procedure, out_segment, coord_n, coord_e]
                writer.writerow(data)


# ==============================================================================

#                      RUNNING THE SCRIPT

# ==============================================================================

# Add a timestamp to filename
time_stamp = datetime.now().strftime("_%Y%m%d_%H%M")

# Create the output CSV's for both LER and CSV flight obstacle data
outputLER_csv = r'I:\GIS\Filepath_to_ouput_file\significant_flight_obst' + time_stamp + '.csv'

# Run the get_filepaths_as_list() - function to acquire a list of filepaths
filepaths_list = get_filepaths_as_list()

# Run the get_deleted_obst() - function
get_deleted_obst(filepaths_list, outputLER_csv)


print('DATA PROCESS IS DONE!')