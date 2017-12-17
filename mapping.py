#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 15 17:20:42 2017

@author: pesa
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
import seaborn as sns

# =============================================================================
# Load and Process Data
# =============================================================================

# reading the JSON data using json.load()
file = 'data/flatmates.json'
file2 = 'data/rooms.json'
with open(file) as flatmates_dict:
    flatmates_dict = json.load(flatmates_dict)
with open(file2) as rooms_dict:
    rooms_dict = json.load(rooms_dict)
    
# converting json dataset from dictionary to dataframe
mates_df = pd.DataFrame.from_dict(flatmates_dict['listings'], orient='index')
mates_areas_df = pd.DataFrame.from_dict(flatmates_dict['areas'], orient='index')
rooms_df = pd.DataFrame.from_dict(rooms_dict, orient='index') 

rental_price_change_df = pd.read_excel('data/rental_price_percentage_change_uk.xls', sheet_name=0, header=1)
#rental_price_change_df.head()

#print(rooms_df.head(5))

print(rooms_df['price'].describe())

# DATASET analysis
print('No of rooms: ', len(rooms_df)) # no of rows
for col in rooms_df.columns:
    print('{0} : {1}'.format(col, rooms_df[col].dtype) )
print()
print(rooms_df.describe())


# =============================================================================
# WordCloud Visualisation
# =============================================================================
'''
# Quick WordCloud Visualisation based on areas 
# that people looking for in South East London are
# selecting in their search

mates_df['matching_search_areas']

from wordcloud import WordCloud, STOPWORDS

# turn feature stored as a list into a separate dataframe with present elements
# represented as differet columns with a boolean value to mark their presence
search_areas_df = mates_df['matching_search_areas'].apply(lambda x: pd.Series(1,
            index=x)).fillna(0).astype(bool)

# Generate a word cloud image
word_cloud = WordCloud(width = 600, height=400, 
                      background_color='white',
                      colormap='copper',
                      max_words=100,
                      stopwords=STOPWORDS,
                      max_font_size=60,
                      min_font_size=20,
                      random_state=40).generate(search_areas_df.columns.str.cat(sep=' '))

word_cloud.words_

plt.figure(figsize=(5, 4), dpi=100)
plt.imshow(word_cloud, interpolation='bicubic')
plt.axis("off")
'''

# =============================================================================
# Time-Series / Line-Graph on Rental Price change
# =============================================================================
'''
from matplotlib.figure import SubplotParams as SPP

spp = SPP(left=None, bottom=None, right=0.7, 
                  top=None, wspace=None, hspace=None)

fig, ax = plt.subplots(figsize=(12,6), subplotpars=spp)

ax = rental_price_change_df['London'].plot(ax=ax)
ax = rental_price_change_df['England'].plot(ax=ax, linestyle='--')
ax.grid()
ax.set_yticks(np.arange(-5, 6, 0.5))
# draw vertical line from (-5,0) to (150, 0)
ax.plot([-5, 150], [0, 0], 'k-', linestyle='-')
ax.set_title('Rental Prices % change over 12 months, Jan 2007 to Nov 2017')


#handles, labels = ax.get_legend_handles_labels()

#ax.legend(handles, labels)
ax.legend(bbox_to_anchor=(1.0, 1.1))
'''

# =============================================================================
# Pie-Plots on: En-Suite Presence / Furnished Status
# =============================================================================

'''
print()
# Ensuite vs Non-Ensuite stats
total_new = rooms_df.ensuite.sum()
percentage_new = total_new / len(rooms_df) * 100
print('Total ensuite: {0}  | Percentage ensuite: {1}%'\
.format(total_new, percentage_new))

# Ensuite vs Non-Ensuite stats
total_new = rooms_df.furnished.sum()
percentage_new = total_new / len(rooms_df) * 100
print('Total furnished: {0}  | Percentage furnished: {1}%'\
.format(total_new, percentage_new))


fig2, (ax21, ax22) = plt.subplots(1, 2) # create a figure (window-object) with 2 subplots


# add a Pie showing the gender division of the survey 
en_count = pd.value_counts(rooms_df['ensuite'].values.flatten())
explode = (0.1, 0)
ax21.pie(en_count,
        explode=explode, autopct='%1.1f%%',
        shadow=True, startangle=90, colors = ['#d62728', '#0589f5']) # set subplot 'ax1' as a pie plot
ax21.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
ax21.legend(loc=2, labels=['Without Ensuite', 'With Ensuite']) # plot legend
ax21.set_title('% of Rooms with Ensuite')

# add a Pie showing the gender division of the survey 
fur_count = pd.value_counts(rooms_df['furnished'].values.flatten())
ax22.pie(fur_count,
        explode=explode, autopct='%1.1f%%',
        shadow=True, startangle=90, colors = ['#df884e','#be6fa6']) # set subplot 'ax1' as a pie plot
ax22.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
ax22.legend(loc=2, labels=['Furnished','Unfurnished']) # plot legend
ax22.set_title('% of Furnished Rooms')


fig2.set_size_inches(10, 6)
fig2.set_tight_layout(True) #avoid labels to be cut out of the image
'''
# =============================================================================
# Histogram: Price Distribution with Mean Annotated
# =============================================================================

'''
print(rooms_df['price'].describe())

fig3, ax3 = plt.subplots()

# make one histogram bin = £50
price_unit = 50
bins = np.arange(rooms_df['price'].min(), rooms_df['price'].max() + 1, price_unit)

prices = rooms_df['price']
ax3.hist(prices, bins=bins)
xlabels = np.arange(0, 3450, price_unit)
ax3.set_xticks(xlabels-75.)
ax3.set_xticklabels(xlabels, rotation='vertical')
ax3.set_yticks(np.arange(0, 500, 25))
ax3.set_ylabel('Number of rooms')
ax3.set_xlabel('Asking Price')
ax3.set_title('Room Rental Price Distribution in SE London ( Source: SpareRoom.co.uk 15/12/2017)')

mode = int(prices.mode()) # annotate the most common renatal price
ax3.annotate('mode: {m}'.format(m=mode), xy=(mode + 1, 5.5),xytext=(mode + 3, 6.2),
arrowprops=dict(facecolor='black', shrink=0.05))

fig3.set_size_inches(14, 10)
fig3.set_tight_layout(True) #avoid labels to be cut out of the image
'''

# =============================================================================
# Scatter-Plots Price vs Latitude & vs Longitude
# =============================================================================

'''
#rooms_df.plot.scatter('price', 'latitude') # simple plot
#sns.regplot(rooms_df['price'], rooms_df['latitude']) # with regression line

sns.lmplot(x='price', y='latitude', data = rooms_df, fit_reg = True) # with regression line
sns.lmplot(x='price', y='longitude', data = rooms_df, fit_reg = True) # with regression line
'''

# =============================================================================
# Bar-chart Average Price per postcode
# =============================================================================

'''
ppc = rooms_df['price'].groupby(rooms_df['postcode']).mean().sort_values()

fig4, ax4 = plt.subplots()

ax4 = ppc.plot.barh(rot=0)
ax4.set_xticks(np.arange(0, 950, 50))
ax4.set_title('Average Room Price per Postcode in SE London (Source: SpareRoom.co.uk 15/12/2017)')
ax4.set_ylabel('Postcode')
ax4.set_xlabel('Average Price')

fig4.set_size_inches(14, 10)
'''

# =============================================================================
# Bar-chart Average Price per ensuite & furnished
# =============================================================================

print()

ppf = rooms_df['price'].groupby(rooms_df['furnished'])
print(ppf.count())
print(ppf.mean())
print(ppf.median())
print(ppf.apply(pd.Series.mode))
print()
ppe = rooms_df['price'].groupby(rooms_df['ensuite'])
print(ppe.count())
print(ppe.mean())
print(ppe.median())
print(ppe.apply(pd.Series.mode))

# Median: not skewed so much by very large or small values

fig5, ax5 = plt.subplots(1,2)

ax5[0].bar(['Unfurnished', 'Furnished'], ppf.median(), color=['darkred', 'darkblue'])
ax5[0].set_yticks(np.arange(0, 950, 50))
ax5[0].set_title('Room Price Furnished / Unfurnished')
ax5[0].set_ylabel('Median Price across SE London')


ax5[1].bar(['Without Ensuite', 'With Ensuite'], ppe.median(), color=['darkred', 'darkblue'])
ax5[1].set_yticks(np.arange(0, 950, 50))
ax5[1].set_title('Room Price with / without Ensuite')
ax5[1].set_xlabel("")

fig5.set_size_inches(8, 8)

# =============================================================================
# Heat-Map on Geographical Area
# =============================================================================

import matplotlib.cm
sns.set(style="white", color_codes=True)

from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
from matplotlib.colors import Normalize
'''
-- Matplotlib Basemap --

To draw a map in Basemap I had to define a few things:

- Where I wanted the map to be centred
- The latitude and longitude of the lower left corner of the "bounding box" 
    around the area that I wanted to map.
- The latitude and longitude of the upper right corner of the bounding box 
    around this area
- Instead of the corners of the bounding box it is also possible to use the
     width and height of the area I wanted to map in metres.
     
To get the bounding box of the map I used the following website:
    http://boundingbox.klokantech.com/
    (use DublinCore coordinates type)
      
'''



plt.show()
