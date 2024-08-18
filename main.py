import requests
import xml.etree.ElementTree as ET
from statistics import mean

VALID_CURRENCIES = ['EUR', 'USD', 'GBP', 'JPY', 'HUF', 'SEK', 'NOK', 'RON', 'BGN','CHF','CZK','PLN','DKK','HRK','CNY','INR','KRW', 'TRY','RUB','MXN','CAD','BRL','AUD',]

def fetch_exchange_rates(currency, date):
    if currency == 'EUR':
        return 1
    if currency not in VALID_CURRENCIES:
        raise ValueError(f"Invalid currency: {currency}")
    entrypoint = 'https://data-api.ecb.europa.eu/service/'
    resource = 'data'
    flowRef = 'EXR'
    key = f'D.{currency}.EUR.SP00.A'
    parameters = {
        'startPeriod': date,
        'endPeriod': date
    }
    request_url = entrypoint + resource + '/' + flowRef + '/' + key

    response = requests.get(request_url, params=parameters)

    if response.status_code == 200:
        root = ET.fromstring(response.text)
        for obs in root.findall('.//{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}Obs'):
            obs_dimension = obs.find('{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}ObsDimension')
            obs_value = obs.find('{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}ObsValue')
            
            if obs_dimension is not None and obs_value is not None:
                return float(obs_value.attrib['value'])

    else:
        return "Exception"

def fetch_exchange_rates_period(currency, date_start, date_end):
    if currency == 'EUR':
        return 1
    if currency not in VALID_CURRENCIES:
        raise ValueError(f"Invalid currency: {currency}")
    entrypoint = 'https://data-api.ecb.europa.eu/service/'
    resource = 'data'
    flowRef = 'EXR'
    key = f'D.{currency}.EUR.SP00.A'
    parameters = {
        'startPeriod': date_start,
        'endPeriod': date_end
    }
    request_url = entrypoint + resource + '/' + flowRef + '/' + key

    response = requests.get(request_url, params=parameters)
    if response.status_code == 200:
        root = ET.fromstring(response.text)
        exchange_rates = []
        for obs in root.findall('.//{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}Obs'):
            obs_dimension = obs.find('{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}ObsDimension')
            obs_value = obs.find('{http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic}ObsValue')
            
            if obs_dimension is not None and obs_value is not None:
                date = obs_dimension.attrib['value']
                rate = float(obs_value.attrib['value'])
                exchange_rates.append((date, rate))
        
        return exchange_rates
    else:
        return "Exception"

def fetch_average_exchange_rate_for_year(currency, year):
    start_date = f'{year}-01-01'
    end_date = f'{year}-12-31'
    rates = fetch_exchange_rates_period(currency, start_date, end_date)
    if rates != "Exception" and rates:
        return mean([rate for _, rate in rates])
    else:
        return None

#Beispielabrufe
if __name__ == "__main__":
    try:
        year = 2023
        currency = 'USD'
        
        # Abrufen des Durchschnittskurses für ein Jahr
        average_rate = fetch_average_exchange_rate_for_year(currency, year)
        if average_rate is not None:
            print(f"The average exchange rate for {currency} in {year} is {average_rate:.4f} {currency}/1.0000 EUR")
        else:
            print(f"No exchange rate data available for {currency} in {year}")
        
        # Abrufen des Stichtagskurses
        specific_date = '2023-03-01'
        spot_rate = fetch_exchange_rates(currency, specific_date)
        if spot_rate is not None:
            print(f"The spot exchange rate for {currency} on {specific_date} is {spot_rate:.4f} {currency}/1.0000 EUR")
        else:
            print(f"No exchange rate data available for {currency} on {specific_date}")
        
        # Abrufen der Kursspanne für einen bestimmten Zeitraum
        date_start = '2023-03-01'
        date_end = '2023-03-10'
        range_average_rate = fetch_exchange_rates_period(currency, date_start, date_end)
        if range_average_rate is not None:
            print(f"The average exchange rate for {currency} from {date_start} to {date_end} is {mean([rate for _, rate in range_average_rate]):.4f} {currency}/1.0000 EUR")
        else:
            print(f"No exchange rate data available for {currency} between {date_start} and {date_end}")
        
        # Abrufen der Tageskurse für den Zeitraum 01-01-2024 bis 15-01-2024
        date_start_2024 = '2024-01-01'
        date_end_2024 = '2024-01-15'
        print(f"Daily exchange rates for {currency} from {date_start_2024} to {date_end_2024}:")
        daily_rates_2024 = fetch_exchange_rates_period(currency, date_start_2024, date_end_2024)
        if daily_rates_2024 != "Exception":
            for date, rate in daily_rates_2024:
                print(f"Date: {date} | Rate: {rate:.4f} {currency}/1.0000 EUR")
        else:
            print(f"No exchange rate data available for {currency} between {date_start_2024} and {date_end_2024}")
        
    except ValueError as e:
        print(e)
