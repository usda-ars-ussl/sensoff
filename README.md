# sensoff

Correct field transect coordinates when an on-the-go sensor is offset from the
GPS on a mobile survey platform.

```
$ python -m sensoff --ioff -0.5 --loff -1.5 sensor_survey_GAMMA.csv
```

![transect plot](./example/gamma_survey.png)

Determining the position of an offset on-the-go sensor is relatively
straightforward if the heading of the mobile platform at each GPS reading is
known. The problem is that the heading is not known: the platform's position is
recorded by the GPS, but not its direction. To calculate the sensor location,
the unknown heading at each point is estimated to be a weighted average of the
bearings of the prior and subsequent legs of the traverse. 

See:

Scudiero, E., D. L. Corwin, P. T. Markley, A. Pourreza, T. Rounsaville, and T.
H. Skaggs. 2020. A novel platform for on-the-go sensing in micro-irrigated
orchards. Computers and Electronics in Agriculture. *In Preparation*.

### Install

```
$ pip install sensoff
```
OR
```
$ conda install -c ussl sensoff
```

### Examples

#### From the command line: 

```
$ python -m sensoff --help

usage: sensoff [-h] [--ioff IOFF] [--loff LOFF] [--xcol XCOL] [--ycol YCOL]
               [--headrows HEADROWS] [--delimiter DELIMITER]
               [--outfile OUTFILE]
               FILE

Correct transect coordinates when sensor is offset from GPS

positional arguments:
  FILE                  Delimited text file with GPS x,y coordinates

optional arguments:
  -h, --help            show this help message and exit
  --ioff IOFF           inline sensor offset, positive in direction of travel
                        (default: 0)
  --loff LOFF           lateral sensor offset, positive to left (facing
                        forward) (default: 0)
  --xcol XCOL           x-coordinate column (default: 1)
  --ycol YCOL           y-coordinate column (default: 2)
  --headrows HEADROWS   number of datafile header rows (default: None)
  --delimiter DELIMITER
                        datafile delimiter (default: ,)
  --outfile OUTFILE     write output to file

             lateral_offset

                  (+)

                   |            Direction of travel -->
             >>>>>>>>>>>>>
             >     |     >
     (-)  --->--- GPS --->---  (+) inline_offset
             >     |     >
             >>>>>>>>>>>>>
                   |
                         (mobile platform) 
                  (-)
```

On the platform, sensor is 1.1 m behind and 0.5 m to the left of the GPS

```
$ python -m sensoff --ioff -1.1 --loff 0.5 datafile1.csv
```

Specify the number of header rows in datafile1 rather than rely on inference

```
$ python -m sensoff --ioff -1.1 --loff 0.5 --headrows 1 datafile1.csv
```

Write output to a file instead of stdout

```
$ python -m sensoff --ioff -1.1 --loff 0.5 --outfile out.csv datafile1.csv
```

Use a delimiter other than "," and non-default data columns

```
$ python -m sensoff --ioff -1.1 --loff 0.5 --xcol 2 --ycol 3 --delimiter " " datafile2.txt
```

#### From python:

```
In [1]: from sensoff import sensor_coordinates

In [2]: sensor_coords = sensor_coordinates("dummy0.csv", ioff=1, loff=1)

In [3]: print(sensor_coords)
[['xgps', 'ygps', 'xsens', 'ysens'],
 [470533.3466, 3759298.5405, nan, nan],
 [470533.4242, 3759298.5348, 470534.0298120643, 3759299.8127804487],
 [470533.4641, 3759298.5622, 470534.3431564087, 3759299.670017598],
 [470533.5238, 3759298.4685, 470534.9321063309, 3759298.5976250498],
 [470533.7208, 3759298.4408, 470535.09349569224, 3759298.1006433647],
 [470533.3325, 3759298.3213, 470534.72614854627, 3759298.08100075],
 [470533.5864, 3759298.3905, 470534.3293269551, 3759297.1871465445],
 [470533.5581, 3759298.3506, 470533.71902153065, 3759296.9455717937],
 [470533.261, 3759298.181, nan, nan]]

In [4]: help(sensor_coordinates)

Help on function sensor_coordinates in module sensoff.sensoff:

sensor_coordinates(gps_file, inline_offset=0, lateral_offset=0, xcol=1, ycol=2, delimiter=',', headrows=None, ioff=None, loff=None)
    Convert GPS coordinates to offset sensor coordinates.
    
    Corrects GPS coordinates when on-the-go transect data have been
    collected using a sensor that is significantly offset from the GPS
    on a mobile platform.
    
    Parameters
    ----------
    gps_file : csv filename or object
        Delimited file containing GPS coordinates for survey transect.
    inline_offset : float, optional
        Sensor offset distance inline with the direction of travel.
        Positive in the direction of travel. Default is 0.
    lateral_offset : float, optional
        Sensor offset distance lateral to the direction of travel.
        Positive to the left (facing forward). Default is 0.
    xcol : int, optional
        Column in datafile with x-coordinates. Default is 1.
    ycol : int, optional
        Column in datafile with y-coordinates. Default is 2.
    delimiter : str, optional
        Delimiter used in coordinate datafile. Default is ",".
    headrows : int, optional
        Number of header rows in datafile. Default is 0.
    ioff, loff : floats, optional
        Aliases for inline_offset and lateral_offset.
    
    Returns
    -------
    List of original and adjusted x,y coordinates
    
    Notes
    -----
    
             lateral_offset
    
                  (+)
    
                   |            Direction of travel -->
             >>>>>>>>>>>>>
             >     |     >
     (-)  --->--- GPS --->---  (+) inline_offset
             >     |     >
             >>>>>>>>>>>>>
                   |
                         (mobile platform) 
                  (-)

```

#### Offsets demo:

![transect plot](./example/offsets_demo.png)
