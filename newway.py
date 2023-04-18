# -*- coding: utf-8 -*-
"""NewWAY.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1PPuaoGLxK_bBKrRYPPikuNdHN2mZjccK
"""

!pip install markovify
!pip install modules
!pip install haversine

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import pandas as pd
import time, calendar, datetime
import matplotlib.pyplot as plt
# %matplotlib inline
# %pylab inline
import glob
from sklearn.cluster import DBSCAN
from sklearn import metrics, preprocessing
from geopy.distance import great_circle
import random
import plotly.express as px
import folium
from folium.plugins import AntPath
import matplotlib.cm as cm
from haversine import haversine
import matplotlib.colors as colors
from collections import Counter

#loading the csv file by using pandas
df=pd.read_csv('/content/df.csv')

#if the number of data is less then 5 then prediction cannot be done
if(len(df)<5):
  print("Data is to less to predict")

#adding the new column in data frame  whose name is Event
intension = ['Personal', 'Family', 'Event', 'Organisation']
l=[]
for i in range(0, len(df['lat'])):
  x = random.choice(intension)
  l.append(x)

df['Event']=l

#printing the first five row of the data frame
df.head()

# Extract latitude and longitude coordinates from the dataframe and store as numpy array
coords = df[['lat', 'long']].values 

# Set the radius of the Earth in kilometers (for use in haversine distance calculation)
kms_rad = 6371.088

# Set the maximum distance between two points to be considered part of the same cluster
# In this case, it is set to 100 kilometers, converted to radians using the Earth's radius
epsilon = 100/ kms_rad

# Perform DBSCAN clustering on the latitude and longitude coordinates using haversine distance metric
# Require at least 50 points in a cluster to be considered a cluster
db = DBSCAN(eps=epsilon, min_samples=5, metric="haversine").fit(np.radians(coords))

# Retrieve the cluster labels assigned by DBSCAN
cluster_labels = db.labels_

# Count the number of clusters found (excluding noise points with label -1)
num_clusters = len(set(cluster_labels)) 

# Print the total number of points and the number of clusters found
print('Clustered ' + str(len(df)) + ' points to ' + str(num_clusters) + ' clusters.')

#printing the all cluster value which is assigned to the lat and long
cluster_labels

#Assigned the cluster value to data frame whose column name is clusters
df['clusters']=cluster_labels

zoom = 4
x=df['lat'].median()
y=df['long'].median()
center = [x,y]
# Create the map object
india_map = folium.Map(location=center, zoom_start=zoom)

x = np.arange(num_clusters)
ys = [i + x + (i*x)**2 for i in range(num_clusters)]
colors_array = cm.rainbow(np.linspace(0, 1, len(ys)))
rainbow = [colors.rgb2hex(i) for i in colors_array]

lat = df.lat
long = df.long

for i in range(1, len(df)):

  

    # Create a green marker for this location with the tooltip text
 
  folium.CircleMarker([df.lat[i], df.long[i]], radius=5, color=rainbow[df.clusters[i]-1]).add_to(india_map)


india_map

from shapely.geometry import MultiPoint
from geopy.distance import great_circle

# Define a function to get the centermost point of a cluster
def get_centremost_point(cluster):
    # Calculate the centroid of the cluster
    centroid = (MultiPoint(cluster).centroid.x, MultiPoint(cluster).centroid.y)
    
    # Find the point in the cluster that is closest to the centroid
    centermost_point = min(cluster, key=lambda point: great_circle(point, centroid).m)
    
    # Return the coordinates of the centermost point
    return tuple(centermost_point)

#Another methode of finding the centroid of the cluster
#centroids = [np.median(i, axis=0) for i in clusters]

clusters = pd.Series([coords[cluster_labels == n] for n in range(num_clusters)])
# Apply the get_centremost_point function to each cluster and extract the coordinates of the centermost point
centermost_points = clusters.map(get_centremost_point)

# Unpack the coordinates into separate latitude and longitude tuples
lats, longs = zip(*centermost_points)

# Create a new DataFrame to hold the representative points
rep_points = pd.DataFrame({"lat": lats, "long": longs})

# Print the representative points DataFrame
centroid_list = []
for i in range(num_clusters):
    centroid = (rep_points['lat'][i], rep_points['long'][i])
    centroid_list.append(centroid)

#Arrange the centroide value according  to the data set on the bases of index
# Initialize an empty dictionary
dict = {}

# Iterate through centroid_list
for i in range(0, len(centroid_list)):
  
   # Find the index value of the row in df where the lat value matches the lat value of the current centroid
   index_value = df.loc[df['lat'] == centroid_list[i][0]].index.values[0]
   
   # Create a tuple (l,p) using the current centroid's lat and long values
   l=centroid_list[i][0]
   p=centroid_list[i][1]
   
   # Add the (l,p) tuple as a key in the dictionary with the corresponding index value as the value
   dict[(l,p)]=(index_value)
   
# Sort the dictionary by value and store the sorted keys in centroid_list
dict = sorted(dict, key=dict.get) 
centroid_list=[]
for i in dict:
  centroid_list.append(i)

# Define the center of the map and the initial zoom level
x=df['lat'].median()
y=df['long'].median()
center = [x, y]
zoom = 4

# Create the map object
india_map = folium.Map(location=center, zoom_start=zoom)

# Create a marker for the first location in centroid_list
folium.CircleMarker(location=[centroid_list[0][0], centroid_list[0][1]],popup='present Location').add_to(india_map)

# Loop through each location in centroid_list
for i in range(1, len(centroid_list)):
    
    # Calculate the distance between this location and the previous one
    prev_location = (float(centroid_list[i-1][0]), float(centroid_list[i-1][1]))
    curr_location = (float(centroid_list[i][0]), float(centroid_list[i][1]))
    distance = haversine(prev_location, curr_location)
    
    # Create a tooltip text for the line connecting the locations
    tooltip_text = f"Distance from previous location: {distance:.2f} km"
    
    # Create a polyline connecting the previous location to this location
    line_coords = [prev_location, curr_location]
    folium.plugins.AntPath(locations=line_coords, color='blue', tooltip=tooltip_text,
                         dash_array=[10, 20], weight=5, delay=800, arrow_style='end').add_to(india_map)
    if(centroid_list[i]==centroid_list[-1]):
       folium.Marker(location=[centroid_list[i][0], centroid_list[i][1]],
                  color=rainbow[i-1],
                  popup='lastloaction').add_to(india_map)
    else:
    
    # Create a green marker for this location with the tooltip text
      folium.CircleMarker(location=[centroid_list[i][0], centroid_list[i][1]],
                  color=rainbow[i],
                  popup=tooltip_text).add_to(india_map)

# Display the map
folium.Marker([centroid_list[-1][0], centroid_list[-1][1]],popup='Lastlocation').add_to(india_map)
india_map

latlong=np.array(df[['lat','long']])

#find all the unique lat and long from the data set
# Initialize an empty list to store locations where the distance between two consecutive points is greater than 5 km
uniplaces=[]

# Iterate through each row in df starting from the second row (index 1)
for i in range(1, len(df)):
    
    # Get the lat and long values of the previous location and the current location
    prev_location = (df.lat[i-1], df.long[i-1])
    curr_location = (df.lat[i], df.long[i])
    
    # Calculate the distance between the previous location and the current location using the haversine formula
    distance = haversine(prev_location, curr_location)
    
    # If the distance is greater than 5 km, add the previous location to the uniplaces list
    if(distance>5):
      uniplaces.append([df.lat[i-1],df.long[i-1]])

# Convert the uniplaces list to a numpy array
uniplaces=np.array(uniplaces)

# Get the number of locations in the uniplaces array
len(uniplaces)

uniplaces=np.array(uniplaces)

# Create a numpy array of zeros with dimensions (len(uniplaces), len(uniplaces))
prob = np.zeros((len(uniplaces), len(uniplaces)), dtype = int)
prob.shape

# Iterate through each element in the latlong list, except for the last element
for i in range(0, len(latlong)-1):
  
  # Get the index of the current location in the uniplaces array
  num1 = np.where(uniplaces == [latlong[i]])[0][0]
  
  # Get the index of the next location in the uniplaces array
  num2 = np.where(uniplaces ==  latlong[i+1])[0][0]
  
  # Increment the corresponding element in the prob array
  prob[num1][num2] += 1

# Print the prob array row by row
for i in prob:
  print(i)

#finding the sum of each row 
temp = [np.sum(prob[i]) for i in range(0, len(prob))]

ans = [np.where(prob[i] != 0)[0] for i in range(len(prob))]

for i in range(0, len(prob)):
  prob[i][ans[i]] = prob[i][ans[i]]/temp[i] 

for i in range(0, len(prob)):
  print(prob[i])

# Define a function called predict that takes an initial position as input
def predict(time):
  
  # Initialize an empty list to store the predicted places
  predictedplaces=[]
  
  # Find the index of the initial position in the latlong array
  initial_index = np.where(df.Timestamp == time)[0][0]
  
  # Get the corresponding row of the prob array for the initial position
  place = prob[initial_index]
  print(place)
  
  # Iterate through each element in the place array, starting from the second element
  for i in range(1, len(place)):
     
     # If the element is not zero, it means there is a possible predicted place
     if place[i] != 0:
      prediction_index = latlong[i+1]
      predictedplaces.append(prediction_index)
  
  # Return the list of predicted places
  return predictedplaces

li=predict(df.Timestamp[3])
presentlocation=(uniplaces[(np.where(df.Timestamp == df.Timestamp[3])[0][0])])

print(prob)

predectedlocation=li
presentlocation[0]

#find the all the cluster value of the predicted loaction
c = df.loc[df['lat'] == presentlocation[0], 'clusters'].values[0]
#find the all the lat and long value of the predected location
cluster = pd.Series([coords[cluster_labels == c]])
li=cluster[0]
li

len(li)

# Get the event associated with the present location
event = df.loc[df['lat'] == presentlocation[0], 'Event'].iloc[0] 

# Filter the DataFrame by the current cluster
filtered_df = df[df['clusters'] == c]

# Get a list of events in the filtered DataFrame, including the event at the current location
Event_list = filtered_df['Event'].values
np.append(Event_list, event)

# Count the occurrences of each event in the list using Counter
b = Counter(Event_list)

# Get the most common event and its count
mostevent = b.most_common(1)

# Print the list of events
Event_list

unique_count= len(set(Event_list))
lie=[]
n=unique_count
count=np.unique(Event_list, return_counts=True)[1]
v=np.sum(count)
for i in range(n):
  lie.append(round(count[i]/v,2))
lie

# n= len(set(Event_list))
# v=(1/n)
# lie=[v]*n
# lie

# Initialize an empty list to store the locations that are more than 10km apart
cluster_data = []

# Loop over the list of locations
for i in range(1, len(li)):
  
    # Get the previous and current locations
    prev_location = (li[i-1][0], li[i-1][1])
    curr_location = (li[i][0], li[i][1])
    
    # Calculate the distance between the previous and current locations using the haversine formula
    distance = haversine(prev_location, curr_location)
  
    # If the distance is more than 10km, add the previous location to the list
    if(distance  >0):
        cluster_data.append([li[i-1][0],li[i-1][1]])
  
    # Otherwise, continue to the next iteration of the loop
    else:
        i = i+1

print(len(cluster_data))

li=cluster_data

import folium
from haversine import haversine
x=df['lat'].median()
y=df['long'].median()
# Define the center of the map and the initial zoom level
center = [x,y]
zoom = 4
india = folium.Map(location=center, zoom_start=zoom)
prev_location = (float(presentlocation[0]), float(presentlocation[1]))
curr_location = (float(predectedlocation[0][0]), float(predectedlocation[0][1]))
line_coords = [prev_location, curr_location]
folium.Marker(location=[presentlocation[0],presentlocation[1]],popup='PRESENTLOCATION').add_to(india)

folium.plugins.AntPath(locations=line_coords, color='blue', tooltip=tooltip_text,
                         dash_array=[10, 20], weight=5, delay=800, arrow_style='end').add_to(india)
folium.Marker(location=[predectedlocation[0][0],predectedlocation[0][1]],popup='PREDECTEDLOCATION').add_to(india)

# Loop through each location in centroid_list
for i in range(0, len(li)):
    pop=df.loc[df['Event'] ==mostevent[0][0],'Event'].iloc[0] 
    folium.CircleMarker(location=[li[i][0], li[i][1]],
                  color='red', radius=5,
                  popup=pop).add_to(india)

# Display the map
india

