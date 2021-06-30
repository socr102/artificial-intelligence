import csv
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime
from pykalman import KalmanFilter

header = [ 'latitude', 'longitude', 'altitude']
filter_data = []    
    
csv_filename = "antakalnis - namai.csv"
df = pd.read_csv(csv_filename)
data = df.values.tolist()
time = []
latitude = []
longitude = []
altitude = []
speed = []
bearing = []
num = []
hdop = []



def convert_latitude(s):
    t = int(s)/100+(s-100*int(s)/100)/60
    return s

def convert_time(tmp):
    h = int(tmp/3600) 
    m = int((tmp-3600*h)/60)
    s = int(tmp-h*3600-m*60)
    dt_obj = datetime.strptime(str(h)+":"+str(m)+":"+str(s),'%H:%M:%S')
    return (dt_obj)
filter = []
filter.append(data[0])

for i in range(1,len(data)):
    if int(data[i][0]-data[i-1][0])!=0:
        filter.append(data[i])

coords = pd.DataFrame([
    {
        'idx':i,
        'lat':convert_latitude(p[1]),
        'lon':convert_latitude(p[2]),
        'ele':convert_latitude(p[3]),
        'speed':p[4],
        'time':convert_time(p[0])
    }
    for i,p in enumerate(filter)
])


    
for i in range(1,len(coords)):
    tmp = []
    tmp.append(coords['lat'][i])
    tmp.append(coords['lon'][i])
    tmp.append(coords['ele'][i])
    filter_data.append(tmp)
    
with open( 'before.csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)

    # write the header
    writer.writerow(header)

    # write multiple rows
    writer.writerows(filter_data)

coords.set_index('time', inplace = True)
coords.head(2)
coords.tail(2)
coords.index = np.round(coords.index.astype(np.int64),-9).astype('datetime64[ns]')

#coords = coords.resample('1S').asfreq()
#coords.loc[coords.ele.isnull()].head()
measurements = np.ma.masked_invalid(coords[['lon', 'lat', 'ele']].values)

F = np.array([[1, 0, 0, 1, 0, 0],
              [0, 1, 0, 0, 1, 0],
              [0, 0, 1, 0, 0, 1],
              [0, 0, 0, 1, 0, 0],
              [0, 0, 0, 0, 1, 0],
              [0, 0, 0, 0, 0, 1]])

H = np.array([[1, 0, 0, 0, 0, 0],
              [0, 1, 0, 0, 0, 0],
              [0, 0, 1, 0, 0, 0]])

R = np.diag([1e-4, 1e-4, 100])**2

initial_state_mean = np.hstack([measurements[0, :], 3*[0.]])
initial_state_covariance = np.diag([1e-4, 1e-4, 50, 1e-6, 1e-6, 1e-6])**2

kf = KalmanFilter(transition_matrices=F, 
                  observation_matrices=H, 
                  observation_covariance=R,
                  initial_state_mean=initial_state_mean,
                  initial_state_covariance=initial_state_covariance,
                  em_vars=['transition_covariance'])

kf = kf.em(measurements, n_iter=2)
(filtered_state_means, filtered_state_covariances) = kf.filter(measurements)
state_means, state_vars = kf.smooth(measurements)

m_filter_data = []
for mdata in filtered_state_means:
    tmp = []
    tmp.append(mdata[1])
    tmp.append(mdata[0])
    tmp.append(mdata[2])
    m_filter_data.append(tmp)
    
with open( 'after.csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)

    # write the header
    writer.writerow(header)

    # write multiple rows
    writer.writerows(m_filter_data)
fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True, figsize=(12, 7))
#ax1.plot(measurements[:,1]), ax2.plot(state_means[:,1]);
#ax1.plot()
#ax1.plot(coords['lon'],coords['lat'])
ax1.plot(filtered_state_means[:,0],filtered_state_means[:,1]);
ax2.plot(state_means[:0]);
#ax2.plot(filtered_state_means[:1])
plt.show()

