
# coding: utf-8

# This notebook describes the steps taken to clean the Dublin Pedestrian footfall index?
# 
# 
# 

# When we open the file in Excel we can see the following::
# ![image.png](attachment:image.png)
# 
# 
# Each sheet contains the following identifiers::
# * Hourly By Entrance (present on every sheet)
# * Location Address: (present on every sheet)
# * Entrance Name: (present on every sheet and multiple times per sheet)
# 
# The data tables consist of::
# * Day of the week
# * Time
# * Direction (In / Out)

# The entrances names are repeated over and over:
# ![image.png](attachment:image.png)

# The aim of this project is to output a .csv file with the following data table::
# 
# |Attribute | Type | Description|
# | :---         |     :---:      |          ---: |
# |Sheet Number | String | The name and number of the sheet (indiacates the numeric week)|
# |Entrance |String | The name where the number of pedestrians was recorded|
# |Time |String | The hour of the day of the observations|
# |Day	Direction |String | The direction of the observations|
# |Value |Integer | The number of observered pedestrians|
# 

# ## Additional cleanup
# 
# I was looking at the filesizes and was trying to figure out why some files were much smaller than other ones.
# 
# ![image.png](attachment:image.png)
# 

# When I opened the files and inspected them again I saw that up to 2011 they were only recording the data in one direction (thus the column of 0's)
# 
# ![image.png](attachment:image.png)

# ### Reading the data

# In[3]:


from pandas import DataFrame, read_csv
import matplotlib.pyplot as plt
import pandas as pd 
import numpy as np
import time
import os


# In[76]:


"""
This will get a list of all .xls(x) files to parse
#there was one file that was .xls not .xlsx so we wildcard for that with *xls*
"""

list_of_files = get_ipython().getoutput('ls input/*xls*')


# In[78]:


#check the list of files in the folder input/
list_of_files


# ### Get a list of the entrances

# In[79]:


#Check to see the different entrances that we need to get the data for

#use the name of the sheet from the excel observed above
worksheet = 'Week_1_2007'
week = pd.read_excel(list_of_files[0], sheet=worksheet)

week.set_index(week.columns[0],inplace=True)            


entrances = week.index[week.index.str.match('Entra',na=False)]
for entrance in entrances:
    print(entrance)
    
print("\nThe number of entrances are lucky: ", len(entrances))    


# This is a failrly monolithic loop of an algorithim with all the error handling contained within.
# 
# The approach is to open each sheet within each file collect the data as a dataframe and append all the dataframes. 
# * For file in files
# *    For sheet in sheets
# *        For entrance in entrances
#         
# ![image.png](attachment:image.png)

# 
# The flow diagram
# 
# We described the dataset above. Essentially we have a 14 * 24 grid that we want to store in a df
# 
# The time is used as an index. We loop of the entrances appending them to another dataframe.
# 
# ![image.png](attachment:image.png)

# In[83]:


x_headers = ["Time","Mon:In","Mon:Out","Tues:In","Tues:Out","Weds:In","Weds:Out",
           "Thurs:In","Thurs:Out","Fri:In","Fri:Out","Sat:In","Sat:Out","Sun:In","Sun:Out","Entrance","Sheet Number"]

stuff_heads = ['Mon:In', 'Mon:Out', 'Tues:In', 'Tues:Out', 'Weds:In', 'Weds:Out', 'Thurs:In', 'Thurs:Out', 'Fri:In', 
            'Fri:Out', 'Sat:In', 'Sat:Out', 'Sun:In', 'Sun:Out']

for file in list_of_files:
    print("*** Parsing:", file)
    input_file = file
    
    #remove the folder path
    output_file = input_file.split('/')[1]

    #rename the .xls(x) file as a csv file
    output_file = 'output/' + output_file.split('.')[0] + '.csv'
    
    #open the file with read_excel with sheet_name=None to get all the available sheets
    df = pd.read_excel(input_file, sheet_name=None)

    #create a blank dataframe which we will reset for each file
    #TODO get a better name than blank_loop
    blank_loop = pd.DataFrame()
    
    """ the next section deals with how dirty the files are and attempts to gracefully clean them """
    for key, value in df.items():
        
        #Some of the sheets are incorrectly formatted and may have a blank column "Unnamed: 0"
        try:
            if value.columns[0] == "Unnamed: 0":    
                value = value.drop("Unnamed: 0", axis=1)
                print(" Sheet: ", key, " had an empty first column.")
            else:
                value = value.drop("Unnamed: 0", axis=1)
                print(" Sheet: ", key, " had an empty first column! Deleted in else")
        except:
            pass

        try:
            #reset the index of the dataframe
            value.reset_index(drop=True)
        except:
            print("Could not reset index for sheet: ", key)


        try:
            #print("Try and set the index")
            value.set_index(value.columns[0],inplace=True)            
        except:
            #this mitigates a sheet having a name but being empty
            print(" Sheet: ", key, " is blank.")            
            break

            
        #get a list of entraces for the current worksheet
        entrances = value.index[value.index.str.match('Entra',na=False)]

        #initialise/reset the data list (will use this to store all the sheets entrace data)
        #TODO update the data list to df_sheet
        data=[]  

        for entrance in entrances:

            #Initialise array for this entrance
            #TODO update the stuff list/dataframe to df_entrance
            stuff = []
            
            #we get the name of the entrance and strip any whitespaces
            ent = entrance.split(":")
            ent = ent[-1].lstrip()
            
            #we get a position value for the location of the entrance
            try:
                position = value.index.get_loc(entrance)
            except:
                print(" Sheet: ", key, " had a problem with entrance: ", ent)

            #using the position with iloc to offset here (explained the Figure. X) create a df
            stuff = pd.DataFrame(value.iloc[position+3:position+27, 0:14])

            #reset the index
            stuff.reset_index()
            
            #give the dataframe column headings
            stuff.columns = stuff_heads
            
            #create a column with the entrance
            stuff['Entrance'] = ent
            
            #create a column with the  shee
            stuff['Sheet Number'] = key
            
            #create a column with the time
            stuff['Time'] = stuff.index.tolist()
            
            #add the stuff dataframce to the list data
            data.append(stuff)
                
        #append all the sheets data to the master df
        blank_loop = blank_loop.append(data,ignore_index=True)

    #we want to melt the data with sheet number, entrances and times
    melted_df = pd.melt(blank_loop, id_vars=['Sheet Number', 'Entrance', 'Time'], var_name='Day/Direction')
    
    #we will drop day/direction after we split it into separate columns
    melted_df['Day'] = melted_df['Day/Direction'].str.split(':').str[0]
    melted_df['Direction'] = melted_df['Day/Direction'].str.split(':').str[-1]
    melted_df = melted_df.drop('Day/Direction', axis=1)
    
    #we pop the value to the end
    value = melted_df.pop('value')
    melted_df['Value'] = value
        
    try:
                
        melted_df.to_csv(output_file, index=False)
        print("Saving file:", output_file ," ***\n")
    except:
        print("There was a problem saving: ", output_file)
    


# In[25]:


blank_loop['Entrance'].value_counts()


# In[54]:


#this jumbles everything into one file
"""

x_headers = ["Time","Mon:In","Mon:Out","Tues:In","Tues:Out","Weds:In","Weds:Out",
           "Thurs:In","Thurs:Out","Fri:In","Fri:Out","Sat:In","Sat:Out","Sun:In","Sun:Out","Entrance","Sheet Number"]

stuff_heads = ['Mon:In', 'Mon:Out', 'Tues:In', 'Tues:Out', 'Weds:In', 'Weds:Out', 'Thurs:In', 'Thurs:Out', 'Fri:In', 
            'Fri:Out', 'Sat:In', 'Sat:Out', 'Sun:In', 'Sun:Out']

for file in list_of_files:
    print("*** Parsing:", file)
    input_file = file
    #rename the .xls(x) file as a csv file
    output_file = input_file.split('.')[0] + '.csv'

    #open the file with read_excel with sheet_name=None to get all the available sheets
    df = pd.read_excel(input_file, sheet_name=None)

    #we need to get a list of sheets from the index
    for key, value in df.items():
        #print(key)
        worksheet = key
    
    #create a blank dataframe which we will reset for each file
    #alley_cat = pd.DataFrame()
    for key, value in df.items():

        #So of the sheets are incorrectly formatted and may have a blank column "Unnamed: 0"
        try:
            if value.columns[0] == "Unnamed: 0":    
                value = value.drop("Unnamed: 0", axis=1)
                print("This sheet had a blank first column:", key)
            else:
                value = value.drop("Unnamed: 0", axis=1)
        except:
            pass


        try:
            #print("Try reset index")
            value.reset_index(drop=True)
        except:
            print("Could not set index")


        try:
            #print("Try and set the index")
            value.set_index(value.columns[0],inplace=True)            
        except:
            print("Couldn't set the index so breaking at sheet:", key)
            break

        #of all the files that I spot checked they all contained this entrance
        test_ent = "Entrance Name: O'Connell Street at Clerys"

        try:
            position = value.index.get_loc(test_ent)
            #print("test ok for: " +str(key))
        except:
            print("test FAILED for: " +str(key))
            #value.set_index(value.columns[1],inplace=True)

        entrances = value.index[value.index.str.match('Entra',na=False)]

        #reset the data list
        data=[]  

        for entrance in entrances:

            #Initialise array for this entrance
            stuff = []
            ent = entrance.split(":")
            ent = ent[-1].lstrip()
            try:
                position = value.index.get_loc(entrance)
                #print("Position" +str(position))
            except:
                print("problem with position")

            stuff = pd.DataFrame(value.iloc[position+3:position+27, 0:14])
            #print(stuff)
            stuff.reset_index()
            stuff.columns = stuff_heads
            stuff['Entrance'] = ent
            stuff['Sheet Number'] = key
            stuff['Time'] = stuff.index.tolist()
            data.append(stuff)
        alley_cat = alley_cat.append(data,ignore_index=True)

output_file = "all ped data.csv"
m = pd.melt(alley_cat, id_vars=['Sheet Number', 'Entrance', 'Time'], var_name='Day/Direction')
m['Day'] = m['Day/Direction'].str.split(':').str[0]
m['Direction'] = m['Day/Direction'].str.split(':').str[-1]
m = m.drop('Day/Direction', axis=1)
x = m.pop('value')
m['Value'] = x
try:
    print("Saving file:", output_file)
    m.to_csv(output_file, index=False)
except:
    print("There was a problem saving: ",output_file)


"""


# We can see there were 624 oberstaions at Grafton St at Korkys, which no longer exists.
