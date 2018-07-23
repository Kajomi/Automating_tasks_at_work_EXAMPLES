#!/usr/bin/env python
# -*- coding: cp1252 -*-
#************************************************************
#-------------------------------------------------------------------------------
# Name:        get_unclear_obst.py
#
# Purpose:     The purpose of the script is to fetch all rows that have been
#              described as 'unclear', and write the resulting rows into
#              a CSV - file.
#
#              The data consists of obstacles in Finland and their associated
#              information. The data is in two Geodatabses witch need to be combined
#              according to corresponding ID values.
#
#              The script consists of three functions that are explained below.
#
# Author:      Mira Kajo - Spring 2018
#-------------------------------------------------------------------------------

# Import all necessary modules
import arcpy
from arcpy import env
import os
import csv
import codecs
from datetime import datetime


# ==============================================================================

#                            DEFINE FUNCTIONS

# ==============================================================================

def get_GDB1_ID_s(inputFC, out_dict):
    '''
    This function fetches all rows from given filepath witch PROCEDURE - column
    value is set to 'Unclear'. The function fetches these rows and creates an
    Dictionary, where the obstacle ID is the key and other items in the row are
    values.

    PARAMETERS:
    -----------
        Takes twi parameters - filepath to Geodatabase/ Shapefile and the Dictionary
        taht will be returned.

    RETURNS:
    --------
        A Dictionary where the obstacle ID is the key and other items in the row
        are values.
    '''

    # Defien the SQL -statement
    haku_nimi = 'Epäselvä'
    sql = "F_TOIMENPIDEKOODI = '{0}'".format(haku_nimi)

    # Create ArcPy SearchCursor, that fetches certain rows from the geodatabase
    with arcpy.da.SearchCursor(inputFC, ['ID', 'TYPE', 'AGL_M_M', 'READY',
                                'RETURN_CODE', 'SEGMENT' ], sql) as cur:

        # Iterate through the cursor and fetch items to own variables
        for row in cur:

            out_ID = str(row[0])
            out_type = str(row[1])
            out_agl = str(row[2])
            out_ready = row[3]
            out_returncode = str(row[4])
            out_segment = row[5]

            # Save each rows data into a variable data as list
            data = [out_ID, out_type, out_agl, out_ready, out_returncode, out_segment]

            # Create a dictionary and check if that ID (key) already exists, if
            # it does not, create a new key and save that rows information to the
            # dictionary.
            if out_ID not in out_dict.keys():
                out_dict[out_ID] = data

            else:
                out_dict[out_ID].append(data)

        # Return dictionary
        return out_dict


def get_related_records(inputFC, related_dict):
    '''
    This function fetches DIAARI -values from another Geodatabase which ID
    matches that of an ID given as parameter. The DIAARI values are added to a
    dictionary created with ger_GDB1_ID_s() -function.

    PARAMETERS:
    -----------
        Takes two parameters - Filepath to second Geodatabase that has the DIAARI
        values and a dictionary created in the precious function (get_GDB1_ID_s())

    RETURNS:
    --------
        A dictionary to which is added DIAARI value for every ID from the second
        Geodatabse.
    '''

    # # Create ArcPy SearchCursor, that fetches certain rows from the geodatabase
    with arcpy.da.SearchCursor(inputFC, ['ID', 'OWNER', 'DIAARI']) as cur:

        # Iterate through each row and save each item to a variable
        for row in cur:
            ID = int(row[0])
            ID_s = str(ID)
            owner = row[1]
            diaari = row[2]
            keys_list = related_dict.keys()

            # Check if the ID given as parameter is found from the second
            # geodatabase
            if ID_s in keys_list:
                # If the ID is found - add it to the dictionary with a matching
                # ID (key)
                related_dict[ID_s].append(owner)
                related_dict[ID_s].append(diaari)

        # Return updated dictionary
        return related_dict



def write_csv_from_dict(input_dict, output_csv):
    '''
    Writes a CSV-file from a dictionary given as input.

    PARAMETERS:
    -----------
        Takes two parameters - the dictionary that has the values one wants to
        save to CSV -file, and an output filepath where the file will be saved.

    RETURNS:
    --------
        CSV - file
    '''

    # Open the filepath given as input
    with open(output_csv, 'wb') as out_csv:

        # Initialize writer and add header
        w = csv.writer(out_csv, delimiter=",")
        # Note: Excel will fail to open Python generated CSVs if the first line
        # is 'ID' in all caps!
        w.writerow(['OBST_ID', 'TYPE', 'AGL_M_M', 'READY', 'RETURN_CODE',
                        'SEGMENT', 'OWNER', 'DIAARI'])

        print('Unclear: ')
        print('----------')

        # Iterate through the dictioanry key by key and write data into a CSV
        # -file
        for row in input_dict.items():
            row_only = row[1]
            print(row_only)
            w.writerow(row_only)

        print('\n ---> CSV - file is ready!')
        print('\n ---> DATA PROCESSING IS DONE!')



# ==============================================================================

#                        INITIALIZING FILEPATH

# ==============================================================================

# --> CHANGE THE NAME OF THE SHAPEFILE HERE:
shapef = 'EF_ACC_SECT_M'

# ----> CHANGE THE FILEPATH NAME TO MATCH THE GEODATABASES ONE IF THE FILE IS NOT
# NAMED IN THE SAME MANNER!
gdb1_fp = r'C:filepath_to_first_geodatabase_here\\' + shapef + '\\' + shapef + '.gdb\\' + shapef
gdb2_fp = r'C:\TEMP\Export.gdb\Export_obs'

# Checking the filepath
# ---------------------------
    # First, check if the endfile already exists for the subject
if os.path.exists(r"C:filepath_to_first_geodatabase_here\outputfiles" + '\\' + shapef):
    print('---> The folder already exists for {0}\n'.format(shapef))
    os.chdir(os.path.join(r'C:filepath_to_first_geodatabase_here\outputfiles', shapef))

    # If the file does not already exist, the script will create a new one and
    # will set it as the new directory
else:
    print('---> Creating a new directory for {0}\n'.format(kentta))
    os.makedirs(r"C:filepath_to_first_geodatabase_here\outputfiles" + '\\' + kentta)
    os.chdir(os.path.join(r'C:filepath_to_first_geodatabase_here\outputfiles', kentta))

# Final file that will be saved , adding date stamp to the filename
save_time = datetime.now().strftime("_%Y%m%d_%H%M")
finalOutput = 'Unclear_IDs_' + shapef + save_time + '.csv'


# ==============================================================================

#                      RUNNING THE SCRIPT

# ==============================================================================

# Create an empty Dictionary
outputDict = {}

# Run the get_GDB1_ID_s() - function to get the data of rows that are defined as
# 'Unclear'
gdb1_Data = get_GDB1_ID_s(gdb1_fp, outputDict)

# Chech if the dictionary is empty (--> does the file have any items that are defined
# as unclear during the analysis phase)
if len(gdb1_Data) == 0:
    print('---> The region has no unclear obsticles --> CSV-file cannot be created')

else:
    # Run the get_related_records() -function, where the second parameter is the
    # dictionary created in previous step --> gdb1_Data
    gdb_1_2_DATA = get_related_records(gdb2_fp, gdb1_Data)

    # Finally run the write_csv_from_dict() - funktion, where the second parameter
    # is the updated dictionary created is previous step --> gdb_1_2_DATA
    write_csv_from_dict(gdb_1_2_DATA, finalOutput)


print('DATA PROCESS IS DONE!')
