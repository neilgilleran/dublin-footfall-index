# coding: utf-8

# ## Creating dates
# 
# What is the problem?
# 
# We have the data melted from the excel files. However we do not have a date.
# 
# Currently we have the week number and abbreviated day of week. We can get hte year from the filename.
# 
# We need to reverse engineer the date. 
# 
# We can use strptime
# 
# We need to create a column with the week number (which we get from the sheet name)
# *WARNING in hte first week of the year there is a potential to have week 53 and week 1. 53 would be from the previous year.
# 
# 

import pandas as pd
from datetime import datetime
import os
from os import listdir

#files = get_ipython().getoutput('ls output/pedestrianfootfall*csv*')
files = os.listdir("output/")
print(files[:-1])
file = files[:-1]

for file in file:

        df = pd.read_csv('output/'+file)


        #use some regex to get the year from the filename
        import re
        get_year = re.compile('\d{4}', re.IGNORECASE)
        year = get_year.search(file)
        print(year[0])
        df['year'] = year[0]



        def get_week(vals):                
                pattern = r'\d+'
                #pattern = r'((Week)|(week))(\_|\s)(\d+)'
                x = re.findall(pattern, vals)
                if x :
                        return(x[0])

        df['week_number'] = df['Sheet Number'].apply(get_week)
        df['week_number'] = df['week_number'].str.strip('keeWw _')


        # ## Issue with abbreviated days
        # 
        # The issue encountered here was days were as such::
        # {'Fri', 'Mon', 'Sat', 'Sun', 'Thurs', 'Tues', 'Weds'}
        # 
        # When they should be::
        # ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        # 
        # Created a replace map to update the values


        import calendar
        abbreviated_days = list(calendar.day_abbr)



        set(df['Day'])


        """ we only need to update The,Tue and Wed """
        replace_map = {'Mon':'Mon','Tues':'Tue','Weds':'Wed','Thurs':'Thu','Fri':'Fri','Sat':'Sat','Sun':'Sun'}

        df['day']=df['Day'].map(replace_map)

        df = df.drop('Day', axis=1)

        df['day'].value_counts()

        df['raw_date'] = df['day'] +' '+df['week_number']+' '+df['year']

        """
        We are going to convert to a date from Raw date which is e.g. Mon 1 2007("%a %W %Y")
        %a - Abbreviated Day e.g. Mon/Tue
        %W - Week Number (starting 1 at first Monday)
        %Y - Year

        This will output a date
        """

        def convert_to_date(vals):
                date_object = datetime.strptime(vals, "%a %W %Y")
                #print(date_object)
                if date_object:
                        return(date_object)

        df['date'] = df['raw_date'].apply(convert_to_date)

        df = df.drop(['Sheet Number','year','raw_date','week_number'], axis=1)

        df = df.sort_values(by=['date','Time','Direction','Entrance'])

        output_path = 'final_output/'
        output_file = 'pedestrian-footfall-data'+year[0]+'.csv'

        df.to_csv(output_path+output_file, index=False)


# # Conlcusion
# 
# Tidy up
# 
# #TODO
# * merge this clean up file into the previous one
# * complete all into the one
# * update the output folder
# * rename the first sheet of the tricky 2014 one
# * 
# * screenshots from tableau/power BI
# * pust to git
# 
# 
