##env_grapher
import matplotlib.pyplot as plt
import urllib3 as url
import numpy as np
import datetime as dt
url.disable_warnings() ## Removes warnings about Unverified HTTPS requests
import sys

def get_data(stat_num,attr):
    stat_num=str(stat_num)
    target = 'https://www.ndbc.noaa.gov/data/realtime2/'+stat_num+'.txt'
    path = stat_num + '.txt'
    c = url.PoolManager()
    resp = c.request('GET',target,preload_content=False)
    with open(path, 'wb') as out:
        while True:
            data = resp.read()
            if not data:
                break
            out.write(data)
    resp.release_conn()
    data = open(path,'r')

    made_keys=False
    times,result=[],[]
    for line in data:
        if line[0] is '#' and not made_keys:
            keys=line[1:].split()[5:]
            found = False
            ind = 0
            for i in range(len(keys)):
                if keys[i] == attr:
                    ind = i+5
                    found = True
            if not found:
                print("Error getting data: invalid attribute given")
                return -1
            made_keys = True
        elif line[0] is '#' and made_keys:
            units = line.split()[ind]
        elif line[0] is not '#':
            times.append(dt.datetime(*[int(x) for x in line.split()[:5]]))
            datapt = line.split()[ind]
            if datapt == 'MM':
                datapt = None
            else:
                datapt=float(datapt)
            result.append(datapt)
        
    
    return times,result,units

#def plot_station(statnum,):

attribute_list = ['WDIR','WSPD','GST','WVHT','DPD','APD','MWD','PRES','ATMP','WTMP','DEWP','VIS','PTDY','TIDE']

def centered_moving_average(dlist):
    rlist=[(1/2)*(dlist[0]+dlist[1])]
    for i in range(1,len(dlist)-1):
        rlist.append((1/3)*(dlist[i-1]+dlist[i]+dlist[i+1]))
    rlist.append((1/2)*(dlist[-1]+dlist[-2]))
    return rlist
    

def compare_plot_station(stat1,stat2,attr,cma):
    if not attr in attribute_list:
        return "Could not create compare plot, attribute not defined. See https://www.ndbc.noaa.gov/measdes.shtml for attributes and their descriptions. \nThey are:" + str(attribute_list)
    t1,r1,u1=get_data(stat1,attr)
    t2,r2,u2=get_data(stat2,attr)
    plt.figure(figsize=(8,6),edgecolor='b')
    if attr=='WDIR':
        flag=''
        for i in range(1,len(r1)):
            ang=r1[i]*np.pi/180
            plt.quiver(t1[i],0.3,np.sin(ang),np.cos(ang),scale=20,color='r')
        ang=r1[0]*np.pi/180
        plt.quiver(t1[0],0.3,np.sin(ang),np.cos(ang),scale=20,color='r',label=('Station '+str(stat1)))
        for j in range(1,len(r2)):
            ang=r2[j]*np.pi/180
            plt.quiver(t2[j],0.7,np.sin(ang),np.cos(ang),scale=20,color='b')
        ang=r2[0]*np.pi/180
        plt.quiver(t1[0],0.7,np.sin(ang),np.cos(ang),scale=20,color='b',label=('Station '+str(stat2)))
        x1,x2,y1,y2=plt.axis()
        plt.axis((x1,x2,0,1))
        plt.ylabel('Direction (North as Up)')
        plt.yticks([])
    else:
        flag = 'Raw '
        if cma:
            flag = 'Smooth '
            r1=centered_moving_average(r1)
            r2=centered_moving_average(r2)
        plt.plot(t1,r1,'r',label=('Station '+str(stat1)))
        plt.plot(t2,r2,'b',label=('Station '+str(stat2)))
        plt.ylabel(attr+' ('+u1+')')
    plt.title(flag+attr+' comparison of stations ' + str(stat1) + ' and ' + str(stat2))
    plt.xlabel('Times (GMT)')
    plt.legend()
    plt.show()
    return "Created and terminated graph successfully."

while True:
    stat1 = input("Number of first station. \nSee https://www.ndbc.noaa.gov/ for map (use ECCC probes)\nOR use sample value of 46208\n")
    stat2 = input("Number of second station. \nSee https://www.ndbc.noaa.gov/ for map (use ECCC probes)\nOR use sample value of 46204\n")
    attr = input("Attribute to Graph. See https://www.ndbc.noaa.gov/measdes.shtml for attributes and their descriptions. \nThey are:" + str(attribute_list)+'\n')
    smooth = input("Smooth data?(True/False)")
    print(compare_plot_station(stat1,stat2,attr,smooth))
    if input("Create another graph? (True/False)"):
        break
