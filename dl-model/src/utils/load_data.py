import csv

data_lithuania_24 = []
data_lithuania_23 = []
data_netherlands_24 = []
data_netherlands_23 = []
data_germany_24 = []
data_germany_23 = []
data_finland_24 = []
data_finland_23 = []
data_austria_24 = []
data_austria_23 = []
data_poland_24 = []
data_poland_23 = []
data_sweden_24 = []
data_sweden_23 = []
data_hungary_24 = []
data_hungary_23 = []

# Each data point has 3 fields: time, prediction, actual
def load_data():
    print('(1/16) Loading data for Lithuania (24-25)...')
    load_country_data(data_lithuania_24, "../data/Total Load - Day Ahead _ Actual_Lithuania_24-25.csv", "LT")

    print('(2/16) Loading data for Lithuania (23-24)...')
    load_country_data(data_lithuania_23, "../data/Total Load - Day Ahead _ Actual_Lithuania_23-24.csv", "LT")

    print('(3/16) Loading data for the Netherlands (24-25)...')
    load_country_data(data_netherlands_24, "../data/Total Load - Day Ahead _ Actual_Netherlands_24-25.csv", "NL")

    print('(4/16) Loading data for the Netherlands (23-24)...')
    load_country_data(data_netherlands_23, "../data/Total Load - Day Ahead _ Actual_Netherlands_23-24.csv", "NL")

    print('(5/16) Loading data for Germany (24-25)...')
    load_country_data(data_germany_24, "../data/Total Load - Day Ahead _ Actual_Germany_24-25.csv", "DE-LU")

    print('(6/16) Loading data for Germany (23-24)...')
    load_country_data(data_germany_23, "../data/Total Load - Day Ahead _ Actual_Germany_23-24.csv", "DE-LU")

    print('(7/16) Loading data for Finland (24-25)...')
    load_country_data(data_finland_24, "../data/Total Load - Day Ahead _ Actual_Finland_24-25.csv", "FI")
   
    print('(8/16) Loading data for Finland (23-24)...')
    load_country_data(data_finland_23, "../data/Total Load - Day Ahead _ Actual_Finland_23-24.csv", "FI")

    print('(9/16) Loading data for Austria (24-25)...')
    load_country_data(data_austria_24, "../data/Total Load - Day Ahead _ Actual_Austria_24-25.csv", "AT")

    print('(10/16) Loading data for Austria (23-24)...')
    load_country_data(data_austria_23, "../data/Total Load - Day Ahead _ Actual_Austria_23-24.csv", "AT")

    print('(11/16) Loading data for Poland (24-25)...')
    load_country_data(data_poland_24, "../data/Total Load - Day Ahead _ Actual_Poland_24-25.csv", "PL")

    print('(12/16) Loading data for Poland (23-24)...')
    load_country_data(data_poland_23, "../data/Total Load - Day Ahead _ Actual_Poland_23-24.csv", "PL")

    print('(13/16) Loading data for Sweden (24-25)...')
    load_country_data(data_sweden_24, "../data/Total Load - Day Ahead _ Actual_Sweden_24-25.csv", "SE1")

    print('(14/16) Loading data for Sweden (23-25)...')
    load_country_data(data_sweden_23, "../data/Total Load - Day Ahead _ Actual_Sweden_23-24.csv", "SE1")

    print('(15/16) Loading data for Hungary (24-25)...')
    load_country_data(data_hungary_24, "../data/Total Load - Day Ahead _ Actual_Hungary_24-25.csv", "HU")

    print('(16/16) Loading data for Hungary (23-24)...')
    load_country_data(data_hungary_23, "../data/Total Load - Day Ahead _ Actual_Hungary_23-24.csv", "HU")


    print('Data loaded successfully.')
    return data_lithuania_24, data_lithuania_23, data_netherlands_24, data_netherlands_23, data_germany_24, data_germany_23, data_finland_24, data_finland_23, data_austria_24, data_austria_23, data_poland_24, data_poland_23, data_sweden_24, data_sweden_23, data_hungary_24, data_hungary_23

def load_country_data(data, file, country_code):
    with open(file, mode="r", encoding="utf-8") as file:
        csv_file = csv.DictReader(file)
        for row in csv_file:
            data.append({
                "time": row["Time (CET/CEST)"],
                "prediction": row[f"Day-ahead Total Load Forecast [MW] - BZN|{country_code}"],
                "actual": row[f"Actual Total Load [MW] - BZN|{country_code}"]
            })
