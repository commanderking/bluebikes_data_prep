import pandas as pd
import utils

renamed_columns_pre_march_2023 = {
    "starttime": "start_time",
    "stoptime": "stop_time",
    "start station id": "start_station_id",
    "start station name": "start_station_name",
    "start station latitude": "start_station_latitude",
    "start station longitude": "start_station_longitude",
    "end station id": "end_station_id",
    "end station name": "end_station_name",
    "end station latitude": "end_station_latitude",
    "end station longitude": "end_station_longitude",
    "bikeid": "bike_id",
    "usertype": "usertype",
    "birth year": "birth_year",
    "gender": "gender",
    "postal code": "postal_code"
}

renamed_columns_march_2023_and_beyond = {
    "ride_id": "ride_id",
    "rideable_type": "rideable_type",	
    "started_at": "start_time",	
    "ended_at": "stop_time",	
    "start_station_name": "start_station_name",
    "start_station_id": "start_station_id",	
    "end_station_name": "end_station_name",	
    "end_station_id": "end_station_id", 
    "start_lat": "start_station_latitude",	
    "start_lng": "start_station_longitude",
    "end_lat": "end_station_latitude",	
    "end_lng": "end_station_longitude",	
    "member_casual": "member_casual"
}

def get_df_with_correct_columns(trip_file):
    df = pd.read_csv(trip_file)
    headers = list(df)
    ### ride_id is column only available starting march 2023 - denotes new headers are used
    if ("ride_id" in headers):
        df.rename(columns=renamed_columns_march_2023_and_beyond, inplace=True)
        return df
    else:
        ### trip_duration no longer provided in post march 2023 ones - removing to avoid confusion with new columns not having this
        df.drop(["tripduration"], axis=1, inplace=True)
        df.rename(columns=renamed_columns_pre_march_2023, inplace=True)
        return df
    

def create_formatted_df(trip_files, output_path):
    file_dataframes = []
    for file in trip_files:
        print(file)
        df = get_df_with_correct_columns(file)
        df[["start_time", "stop_time"]] = df[["start_time", "stop_time"]].astype("datetime64[ns]")
        df[["start_station_id", "end_station_id"]] = df[["start_station_id", "end_station_id"]].astype("str")
        
        ### Addressed the following issue: pyarrow.lib.ArrowInvalid: ("Could not convert '-71.101427' with type str: tried to convert to double", 'Conversion failed for column end_station_longitude with type object'). There may be some Na as a result in the final data
        ### TODO: Investiage this further - probably don't want to drop the row completely
        # We can check with: print(df['end_station_latitude'].isna().sum())
        df['end_station_latitude'] = pd.to_numeric(df['end_station_latitude'], errors='coerce')
        df['end_station_longitude'] = pd.to_numeric(df['end_station_longitude'], errors='coerce')
        
        if(all([item in df.columns for item in ['birth_year','gender']])):
            # Beacuse of NaN in data, birth_year and gender are floats. Converting to Int64 allows for <NA> type in integer column
            # hubway data contains \N for some birth_years
            df[["birth_year", "gender"]] = df[["birth_year", "gender"]].replace('\\N', pd.NA).astype("Int64")

        
        file_dataframes.append(df)

    print("concatenating all csv files...")
    
    print(output_path)

    all_trips_df = pd.concat(file_dataframes, join='outer', ignore_index=True)

    utils.create_file(all_trips_df, output_path)
    
    return all_trips_df

def build_all_trips(csv_source_directory, output_path):
    trip_files = utils.get_csv_files(csv_source_directory)
    create_formatted_df(trip_files, output_path)