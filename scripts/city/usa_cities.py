import zipfile
import os
import polars as pl
import utils
import constants
import city.philadelphia as philadelphia
default_final_columns = constants.final_columns

city_file_matcher = {
    "boston": ["-tripdata"],
    "nyc": ["citibike-tripdata"],
    "dc": ["capitalbikeshare-tripdata"],
    "chicago": ["trip", "Trips"],
    "philadelphia": ["trips", "Trips"],
    "pittsburgh": [".csv"],
    "sf": ["tripdata"]
}

def get_applicable_columns_mapping(df, rename_dict):
    # Filter the rename dictionary to include only columns that exist in the DataFrame
    existing_columns = df.columns
    filtered_rename_dict = {old: new for old, new in rename_dict.items() if old in existing_columns}

    return filtered_rename_dict

def rename_columns(df, args):
    city = args.city
    mappings = constants.column_mapping[city]
    headers = df.columns
    applicable_renamed_columns = []
    
    # TODO: This should be more robust - theoretically, multiple column mappings could match and the 
    # last match would be the mapping used
    for mapping in mappings:
        if (mapping["header_matcher"] in headers):
            applicable_renamed_columns = get_applicable_columns_mapping(df, mapping["column_mapping"])
            final_columns = mapping.get("final_columns", default_final_columns)
            renamed_df = df.rename(applicable_renamed_columns).select(final_columns)
            return renamed_df
    raise ValueError(f'We could not rename the columns because no valid column mappings for {city} match the data! The headers we found are: {df.columns}')


def format_and_concat_files(trip_files, args):
    """Get correct column data structures"""
    
    print("adding files to polars df")
    file_dataframes = []
    for file in trip_files:
        print(file)

        date_formats = [
            "%Y-%m-%d %H:%M:%S",
            "%m/%d/%Y %H:%M:%S",
            "%m/%d/%Y %H:%M",
            "%Y-%m-%d %H:%M", # Chicago - Divvy_Trips_2013
            '%Y-%m-%dT%H:%M:%S', # Pittsburgh
            '%a, %b %d, %Y, %I:%M %p' #Pittsburgh one file - 8e8a5cd9-943e-4d21-a7ed-05f865dd0038 (data-id), April 2023
        ]
        # TODO: Some columns like birth year have value \\N. Map \\N to correct values
        df = pl.read_csv(file, infer_schema_length=0)
        
        # For debugging columns that have missing data
        # utils.assess_null_data(df)
            
        df = rename_columns(df ,args)
        df = df.with_columns([
            # Replace . and everything that follows with empty string. Some Boston dates have milliseconds
            pl.coalesce([pl.col("start_time").str.replace(r"\.\d+", "").str.strptime(pl.Datetime, format, strict=False) for format in date_formats]),
            pl.coalesce([pl.col("end_time").str.replace(r"\.\d+", "").str.strptime(pl.Datetime, format, strict=False) for format in date_formats]),
        ])
        
        # For debugging and printing tables with null data for a particular column after formatting
        # df_start_time = df.filter(pl.col("start_time").is_null())
        # print(df_start_time)

        # TODO: This station name mapping should apply to all stations
        # May want to make this configuration based rather than explicit city checks here
        if (args.city == "philadelphia"):
            stations_df = philadelphia.get_stations_df()
            df = philadelphia.append_station_names(df, stations_df).drop("start_station_id", "end_station_id")                      
        file_dataframes.append(df)

    print("concatenating all csv files...")
    
    all_trips_df = pl.concat(file_dataframes)
    return all_trips_df

def extract_zip_files(city):
    print(f'unzipping {city} trip files')
    city_zip_directory = utils.get_zip_directory(city)
    
    def city_match(file_path, city):
        if city == "nyc":
            # JC files are duplicates of other files, but contain a more limited set of columns
            return "JC" not in file_path
        else: 
            return any(word in file_path for word in city_file_matcher[city])        

    for file in os.listdir(city_zip_directory):
        file_path = os.path.join(city_zip_directory, file)
        if (zipfile.is_zipfile(file_path) and city_match(file_path, city)):
            with zipfile.ZipFile(file_path, mode="r") as archive:
                archive.extractall(utils.get_raw_files_directory(city))

def filter_filenames(filenames, matching_words):
    # os.path.basename - Chicago files have a stations_and_trips folder, which creates a csv for stations. I don't want to include this stations csv in our checks, so filtering on just the filename not folder
    return [filename for filename in filenames if any(word in os.path.basename(filename) for word in matching_words)]


def build_all_trips(args):
    source_directory = utils.get_raw_files_directory(args.city)

    if args.skip_unzip is False:
        extract_zip_files(args.city)
    else:
        print("skipping unzipping files")
    trip_files = utils.get_csv_files(source_directory)
    filtered_files = filter_filenames(trip_files, city_file_matcher[args.city])
    all_trips_df = format_and_concat_files(filtered_files, args)
    
    utils.create_all_trips_file(all_trips_df, args)
    utils.create_recent_year_file(all_trips_df, args)
    
    utils.print_null_rows(all_trips_df)
