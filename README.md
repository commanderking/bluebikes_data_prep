### Purpose

While city bikeshare data is often accessible, it requires significant processing before analysis can be done. The repo cleans and merges publicly available bikeshare trip data into a single csv or parquet file to allow anaylsis on the entire history of bike trips.

Currently, data is available for:

| City          | Source |
| -----------   | ----------- |
| Boston        | <https://bluebikes.com/system-data>  |
| Chicago       | <https://divvybikes.com/system-data> |
| NYC           | <https://citibikenyc.com/system-data> |
| Philadelphia  | https://www.rideindego.com/about/data/ |
| Pittsburgh    | https://data.wprdc.org/dataset/pogoh-trip-data |
| San Francisco | <https://www.lyft.com/bikes/bay-wheels/system-data> |
| Taipei        | <https://data.gov.tw/dataset/150635> | 
| Toronto       | <https://open.toronto.ca/dataset/bike-share-toronto-ridership-data/> |
| Washington DC | <https://capitalbikeshare.com/system-data> | 

Pittsburgh old data can be found at: https://data.wprdc.org/dataset/healthyride-trip-data

### Configuration

1. Copy the contents of .env.config to .env. 
2. For PROJECT_ROOT, paste the path to this project. 

### Steps to building a parquet or csv file

1. Install pipenv (https://pipenv.pypa.io/en/latest/install/) if needed
2. pipenv install
3. pipenv shell
4. pipenv run build [city] (ex pipenv run build boston)

By default, a parquet file for your selected city wil lbe generated in the `data` folder. If you'd like a csv file instead, you can run 

```
pipenv run build [city] --csv
```

#### Steps in the script

The general procedure to clean the data in any city is:

1. Unzip all bikeshare trip data into their csv files, storing them in `./src/data/[city]`
2. Commonize the column headers and merge all trips into one polars dataframe.
3. Export a csv or parquet file for further analysis

If the data has already been unzipped by running `pipenv run build`, you can skip the unzipping step by adding `--skip_unzip` to

#### Potential Upcoming Cities in the Pipeline


### Philadelphia
Data can be found here: https://www.rideindego.com/about/data/

### Austin
TODO: Austin updates monthly, but doesn't provide an easy way to download file (need to export) - https://data.austintexas.gov/Transportation-and-Mobility/Austin-MetroBike-Trips/tyfh-5r8s/about_data

### Columbus

https://cogobikeshare.com/system-data


### London 
https://cycling.data.tfl.gov.uk/

### Los Angeles
https://bikeshare.metro.net/about/data/

### Montreal

https://bixi.com/en/open-data/

### Oslo

https://oslobysykkel.no/en/open-data/historical

### Portland

https://s3.amazonaws.com/biketown-tripdata-public/index.html

### Vancouver

https://www.mobibikes.ca/en/system-data

### Mexico City

https://ecobici.cdmx.gob.mx/en/open-data/

### Dublin

https://data.gov.ie/dataset/dublinbikes-api


### Bicimad

https://opendata.emtmadrid.es/Datos-estaticos/Datos-generales-(1)

#### Null start and end stations - tested on 6/12/24. Includes 2024/04 bluebike data
- Chicago - 4_102_485
- Boston - 19_626
- NYC - 308_238
- Philadelphia - 0
- DC - 1_563_414
- SF - 3_205_547
- Toronto - 16 
- Taipei - 692


### Personal Notes

- Pittsburgh has one file that isn't accessible through the API