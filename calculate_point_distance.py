#************************************************************
# -*- coding: cp1252 -*-
#************************************************************
#-------------------------------------------------------------------------------
# Name:        calculate_point_distance.py
#
# Purpose:     The script consists of two functions: calculate_distance() and
#              get_distance_as_csv().
#
#              First function calculates the distance between two points from
#              two geodatabase/shapefile that have the same ID.
#
#              The second function creates a CSV - file with basic statistics.
#
# Author:      Mira Kajo - Spring 2018
#
#-------------------------------------------------------------------------------

# Importing necessary modules
import arcpy
from arcpy import env
import os
import csv
import numpy as np
from datetime import datetime


# ==============================================================================

#                            DEFINE FUNCTIONS

# ==============================================================================


def calculate_distance(workspace):
    '''
    Calculates the distance between two points which have the same ID. First, it
    fetches all rows (point ID and geometry) that have 'Relocated' as their status
    in PROCEDURE column from the first Geodatabase given as input (workspace),
    and from this information creates a list of lists.

    After this, the list of list is used to fetch matching IDs from the second
    GeoDatabase (point ID and geometry).

    The function returns a list, that has the point Id and distance between the
    two points in meters.

    PARAMETER:
    ----------
        Filepath to input Geodatabase/ Shapefile

    RETURN:
    -------
        A list of IDs that have 'Relocated' as PROCEDURE status and the difference
        in meters.

    '''
    # Defien the SQL -statement
    search_status = 'Relocated'
    sql = "PROCEDURE = '{0}'".format(search_status)

    # Create ArcPy SearchCursor, that fetches certain rows from the geodatabase
    # Returns information from columns 'ID' and 'Shape'
    cur = arcpy.da.SearchCursor(workspace, ['ID', 'SHAPE@'], sql)

    # Create two empty lists
    obst_list = []
    obst_dist_list = []

    # Iterate through the cursor, fetch data and append to an empty list
    for row in cur:
        obst = [row[0], row[1]]
        obst_list.append(obst)

    # From list, fetch ID and Shape values to separate variables
    for item in obst_list:
        ids = item[0]
        shape = item[1]

        # Define the filepath to geodatabase2 that has information form the previous
        # geodatbase and thus, previous obstacle locations
        gd2_fp = r'C:\TEMP\Export.gdb\Export_obs'

        # Create ArcPy SearchCursor for the second GeoDatabase
        with arcpy.da.SearchCursor(gdb2_fp, ['ID', 'SHAPE@']) as cur2:

            # fetch each obstacles ID
            for row in cur2:
                ID = int(row[0])

                # If the ID matches to an ID found in the first GeoDatabase - include
                # it in further analysis
                if ID == ids:

                    # Calculate the distance between points
                    dist = row[1].distanceTo(shape)
                    print("The distance is {0} meters for {1}".format(dist, ID))
                    # Save the information to the second empty list
                    obst_dist_list.append([ID, round(dist, 2)])

    # Return the second list
    return obst_dist_list


def get_distance_as_csv(list_of_lists, output_csv, apron):
    '''
    This function creates a CSV -file from a list given as input. Calculates
    basic statistics from fligth obstacles that have been relocated:

        - Number of relocated flight obstacles
        - Total amount of distance in meters
        - Shortest relocation (m)
        - Biggest relocation (m)
        - Mean
        - Median

    PARAMETER:
    ----------
        List created in calculate_distance() -function, filepath to output CSV
        -file, and the code name of the apron/airport under scrutiny.

    RETURN:
    -------
        Creates a CSV -file that contains IDs for flight obstacles that have a
        'Relocated' as their status in the first GeoDatabase, the distance in
        meters between the same point in first and second GeoDatabase, and some
        basic statistics to add more detail to further analysis.

    '''
    # open the file given as parameter
    with open(output_csv, 'wb') as outFile:
        writer = csv.writer(outFile)
        writer.writerow(["ID's that have been relocated: {0}".format(apron)])
        writer.writerow([])
        writer.writerow(['OBST_ID', 'DISTANCE (m)'])

        # Initialising variables to calculate simple stats for the area
        count = 0
        stats_list = []

        # Iterate through each row and write to file
        for item in list_of_lists:
            writer.writerow([item[0], item[1]])

            # Calculating simple stats
            stat = item[1]
            stats_list.append(stat)
            count += 1

        # Ccalculate some additional basic statistics
        writer.writerow([])
        writer.writerow(["Total amount of relocated flight obstacles:   {0}".format(count)])
        writer.writerow(["Total amount of distance in meters:   {0}".format(sum(stats_list))])
        writer.writerow(["Shortest relocation (m):   {0}".format(np.amin(stats_list))])
        writer.writerow(["Biggest relocation (m):   {0}".format(np.amax(stats_list))])
        writer.writerow(["Mean:   {0}".format(round(np.mean(stats_list), 2))])
        writer.writerow(["Median:   {0}".format(np.median(stats_list))])



# ==============================================================================

#                        INITIALIZING FILEPATH

# ==============================================================================

# --> CHANGE THE NAME OF THE SHAPEFILE HERE:
apron = 'EF_ACC_SECT_M'

# ----> CHANGE THE FILEPATH NAME TO MATCH THE GEODATABASES ONE IF THE FILE IS NOT
# NAMED IN THE SAME MANNER!
gdb1_fp = r'I:\GIS\Esterekisterin_perusparannus\Perusparannus 2018\KÄSITTELY\\' + apron + '\\' + apron + '.gdb\\' + apron

# Checking the filepath
# ---------------------------
    # First, check if the endfile already exists for the subject
if os.path.exists(r"I:\GIS\Esterekisterin_perusparannus\Perusparannus 2018\SELVITYS" + '\\' + apron):
    print('The folder already exists for {0}\n'.format(apron))
    os.chdir(os.path.join(r'I:\GIS\Esterekisterin_perusparannus\Perusparannus 2018\SELVITYS', apron))

    # If the file does not already exist, the script will create a new one and
    # will set it as the new directory
else:
    print('Creating a new directory for {0}\n'.format(apron))
    os.makedirs(r"I:\GIS\Esterekisterin_perusparannus\Perusparannus 2018\SELVITYS" + '\\' + apron)
    os.chdir(os.path.join(r'I:\GIS\Esterekisterin_perusparannus\Perusparannus 2018\SELVITYS', apron))

# Final file that will be saved , adding date stamp to the filename
save_time = datetime.now().strftime("_%Y%m%d_%H%M")
finalOutput = 'Relocated_' + apron + save_time + '.csv'


# ==============================================================================

#                      RUNNING THE SCRIPT

# ==============================================================================

# Run calculate_distance() - function
relocated_list = calculate_distance(mml_fp)

# Chech if the list is empty (--> does the file have any items that are defined
# as Relocated during the analysis phase)
# seuraavaan kohtaan ja ajaa get_distance_as_csv() - funktion
if len(relocated_list) == 0:
        print('List is empty - no relocations commited in the area')
else:
    get_distance_as_csv(relocated_list, finalOutput, apron)


print('DATA PROCESS IS DONE!')

