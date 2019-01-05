
# coding: utf-8

# # Assignment 2
# 
# Before working on this assignment please read these instructions fully. In the submission area, you will notice that you can click the link to **Preview the Grading** for each step of the assignment. This is the criteria that will be used for peer grading. Please familiarize yourself with the criteria before beginning the assignment.
# 
# An NOAA dataset has been stored in the file `data/C2A2_data/BinnedCsvs_d400/9ea1109f79cbb97b7c1ffa5279925674c0cd8f1f85ccfdd1cd56b5cf.csv`. The data for this assignment comes from a subset of The National Centers for Environmental Information (NCEI) [Daily Global Historical Climatology Network](https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt) (GHCN-Daily). The GHCN-Daily is comprised of daily climate records from thousands of land surface stations across the globe.
# 
# Each row in the assignment datafile corresponds to a single observation.
# 
# The following variables are provided to you:
# 
# * **id** : station identification code
# * **date** : date in YYYY-MM-DD format (e.g. 2012-01-24 = January 24, 2012)
# * **element** : indicator of element type
#     * TMAX : Maximum temperature (tenths of degrees C)
#     * TMIN : Minimum temperature (tenths of degrees C)
# * **value** : data value for element (tenths of degrees C)
# 
# For this assignment, you must:
# 
# 1. Read the documentation and familiarize yourself with the dataset, then write some python code which returns a line graph of the record high and record low temperatures by day of the year over the period 2005-2014. The area between the record high and record low temperatures for each day should be shaded.
# 2. Overlay a scatter of the 2015 data for any points (highs and lows) for which the ten year record (2005-2014) record high or record low was broken in 2015.
# 3. Watch out for leap days (i.e. February 29th), it is reasonable to remove these points from the dataset for the purpose of this visualization.
# 4. Make the visual nice! Leverage principles from the first module in this course when developing your solution. Consider issues such as legends, labels, and chart junk.
# 
# The data you have been given is near **Chicago, Illinois, United States**, and the stations the data comes from are shown on the map below.

# In[1]:

import matplotlib.pyplot as plt
import mplleaflet
import pandas as pd

def leaflet_plot_stations(binsize, hashid):

    df = pd.read_csv('data/C2A2_data/BinSize_d{}.csv'.format(binsize))

    station_locations_by_hash = df[df['hash'] == hashid]

    lons = station_locations_by_hash['LONGITUDE'].tolist()
    lats = station_locations_by_hash['LATITUDE'].tolist()

    plt.figure(figsize=(8,8))

    plt.scatter(lons, lats, c='r', alpha=0.7, s=200)

    return mplleaflet.display()

leaflet_plot_stations(400,'9ea1109f79cbb97b7c1ffa5279925674c0cd8f1f85ccfdd1cd56b5cf')


# In[ ]:

#read in data
df = pd.read_csv('data/C2A2_data/BinnedCsvs_d400/9ea1109f79cbb97b7c1ffa5279925674c0cd8f1f85ccfdd1cd56b5cf.csv')
#take out all Feb. 29th
df=df[-df.Date.str.contains('02-29')]
#make separate dataframe for 2015 data and limit it to Date, Value columns
fifteen=df[df.Date.str.contains('2015')]
fifteen=fifteen[['Date', 'Data_Value']]
#create data frame of all the TMIN values and retain only the columns you need
temp_min=df.loc[df.Element=='TMIN']
temp_min=temp_min[['Date', 'Data_Value']]
#create data frame of all the TMAX values and retain only the columns you need
temp_max=df.loc[df.Element=='TMAX']
temp_max=temp_max[['Date', 'Data_Value']]

#Date is a string and Data_Value is int64
#convert date to just have the month and day
temp_min['Date']=temp_min['Date'].str[5:]
temp_max['Date'] = temp_max['Date'].str[5:]
#reset indexes to start at 0 
temp_min=temp_min.reset_index(drop=True)
temp_max=temp_max.reset_index(drop=True)
#do the same with the 2015 data
fifteen['Date']=fifteen['Date'].str[5:]
fifteen=fifteen.reset_index(drop=True)

#groupby day of year and find max value in each. Gets a series with the date as index. Create data frame from that and make index ('Date') into a column
#then sort by date and then reset index to start from 0
temp_max=temp_max.groupby(['Date'], sort=False)['Data_Value'].max()
temp_max=pd.DataFrame(temp_max).reset_index().sort_values(by='Date').reset_index(drop=True)
#groupby day of year and find min value in each. Gets a series with the date as index. Create data frame from that and make index ('Date') into a column
#then sort by date and then reset index to start from 0
temp_min=temp_min.groupby(['Date'], sort=False)['Data_Value'].min()
temp_min=pd.DataFrame(temp_min).reset_index().sort_values(by='Date').reset_index(drop=True)
#then do the same to create dataframes for min and max of values in 2015
fifteen_max=fifteen.groupby(['Date'], sort=False)['Data_Value'].max()
fifteen_max=pd.DataFrame(fifteen_max).reset_index().sort_values(by='Date').reset_index(drop=True)
fifteen_min=fifteen.groupby(['Date'], sort=False)['Data_Value'].min()
fifteen_min=pd.DataFrame(fifteen_min).reset_index().sort_values(by='Date').reset_index(drop=True)
#divide all Data_Values by 10 since they are in tenths of degree
temp_max['Data_Value']=temp_max['Data_Value']/10
temp_min['Data_Value']=temp_min['Data_Value']/10
fifteen_max['Data_Value']=fifteen_max['Data_Value']/10
fifteen_min['Data_Value']=fifteen_min['Data_Value']/10
#find where max, min values in 2015 are also in the max, min for all years. Get NaN and some numbers in each
fifteen_min=fifteen_min.where(fifteen_min['Data_Value']==temp_min['Data_Value'])
fifteen_max=fifteen_max.where(fifteen_max['Data_Value']==temp_max['Data_Value'])
#create a list (must be a list of the dates
dates=pd.to_datetime(temp_max.Date, format='%m-%d')
dates=list(dates)
#insert Date column in 2015 data frames
fifteen_min['Date']=dates
fifteen_max['Date']=dates
#merge the two 2015 dataframes
fifteen_merged=pd.merge(fifteen_max, fifteen_min, on='Date')
#add across rows, ie make a column that has combines the columns
fifteen_merged['Data_Value'] = fifteen_merged[['Data_Value_x','Data_Value_y']].sum(axis=1)
#take just the date and combined column for the info you want to plot
fifteen_merged=fifteen_merged[['Date', 'Data_Value']]
------------------------------------------------------------------------------------------
#plot with fill_between 
plt.figure()
#x val, y val, type, x val, y val, type, make points smaller than default
#set colors you want for the line plots
plt.gca().set_color_cycle(['red', 'blue'])
#line plot. Note: '-o' makes plot of connected points rather than line plot. That won't work with the scatter plot
plt.plot(dates, temp_max.Data_Value, dates, temp_min.Data_Value, markersize=2, alpha=0.5)
#scatterplot
plt.scatter(dates, fifteen_merged.Data_Value, color='black', s=10)
plt.gca().fill_between(dates, 
                       temp_min.Data_Value, temp_max.Data_Value, 
                       facecolor='blue', 
                       alpha=0.25)
plt.ylabel('Degrees in Celsius')
plt.xlabel('Day of the Year')
#set the format of the x vals on the major ticks to be just their month in string format
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b'))
#set the major ticks to go by month
plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
plt.legend(['Record High', 'Record Low', 'High/Low falling in 2015'], loc=4, frameon=False)
plt.title('Record High and Low Temperature for Each Day of the Year (2005-2014)')
#save as png file. Then click File -> Open and you'll see it saved there
plt.savefig('Assignment 2')
#if you just want to show in Jupyter notebook
#plt.show()