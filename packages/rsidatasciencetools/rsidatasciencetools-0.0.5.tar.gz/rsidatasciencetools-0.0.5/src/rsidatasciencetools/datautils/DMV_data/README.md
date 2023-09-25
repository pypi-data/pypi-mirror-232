# DMV Data Generator

This code generates records of compliant and non-compliant Data for DMV to be used in RSI Machine Learning Models. Vehicle records corresponds to vehicles in current usage. Does not include historical ownership nor sale transactions.

# Output
It generates two pandas dataframes: a owner details dataframe (`owner_dataset_df`), and a vehicle details dataframe (`vehicle_dataset_df`), which can be join with the `dmv_userid` field.

```
optional arguments:
  -h, --help            show this help message and exit
  --n_samples N_SAMPLES
                        Number of owner records to generate
  --seed SEED           Seed to start random state
  --p_nc P_NC           Probability for a record to be non-compliant
  --export_csv          Export generated dataset to CSV
  --debug               Enable debugging
```

The export is made to two files `dmv_owner_dataset.csv` and `dmv_vehicle_dataset.csv`, in the `./tests` folder relative to where the `DMC_data_generator.py` is located.

# Usage
Out of the box, you can run:

```
$python DMV_data_generator.py --n_samples=40 --seed=1 --p_nc=0.05 --export_csv --debug 
```

# Columns included in version 1

## Owner dataset
```
dmv_userid                   int64
taxpayertype                object
compositename               object
firstname                   object
lastname                    object
middlename                  object
maidenname                  object
driver_license              object
ssn                         object
birthday            datetime64[ns]
phoneno                      int64
email                       object
ethnicity                   object
compositeaddress            object
streetno                    object
aptno                       object
streetname                  object
city                        object
zipcode                      int64
routing_number              object
bank_account                object
h_income                   float64
n_vehicles                   int64
is_nc                        int64
```

## Vehicle dataset
```
dmv_userid           int64
vehicle_id          object
vehicle_type        object
plate               object
vin                 object
manufacturer        object
model               object
prod_year           object
color               object
category            object
leather interior    object
fuel_type           object
engine_volume       object
mileage             object
cylinders           object
gear_box_type       object
drive_wheels        object
doors               object
wheel               object
airbags             object
levy                object
purchase_price      object
```
