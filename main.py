import pandas as pd
import requests
import xml.etree.ElementTree as ET
import logging

USER_ID = 'USER_ID'# TODO replace with your USPS API userid
CITY = 'CHICAGO'# TODO replace with your target city or pass it in from the csv file
STATE = 'IL'# TODO replace with your target state or pass it in from the csv file
TARGET_ZIPCODES = ['TargetZipCode1', 'TargetZipCode2']# TODO replace with your target zipcodes
DATA_SOURCE_PATH = 'data.csv' # TODO replace with your csv file path
SAVE_FILE_PATH = 'results.txt' # TODO replace with your save file path

logging.basicConfig(filename='chicagoIL.log', level=logging.DEBUG)
# Exclude the request lines of debug code from the log
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logger = logging.getLogger()

def get_zipcode(id, address1, address2, city, state):
    """
    Given an address, city, and state, this function uses the USPS API to validate the address and retrieve the corresponding zipcode.
    If the zipcode is found, it is returned. Otherwise, None is returned.
    
    Args:
    - id (int): The ID of the address.
    - address1 (str): The first line of the address (optional).
    - address2 (str): The second line of the address.
    - city (str): The city of the address.
    - state (str): The state of the address.
    
    Returns:
    - str or None: The zipcode of the address if found, otherwise None.
    """
    
    url = 'http://production.shippingapis.com/ShippingAPI.dll'
    xml = f'<AddressValidateRequest USERID="{USER_ID}"><Address ID="0"><Address1>{address1}</Address1><Address2>{address2}</Address2><City>{city}</City><State>{state}</State><Zip5></Zip5><Zip4></Zip4></Address></AddressValidateRequest>'
    params = {'API': 'Verify', 'XML': xml}
    response = requests.get(url, params=params)
    root = ET.fromstring(response.content)
    try:
        zipcode = root.find('Address').find('Zip5').text
        logger.debug(f"ZIPCODE FOUND- id:{id}, zipcode: {zipcode}, address:{address2}")
        return zipcode
    except Exception as e:
        print(f"Error: {e}, id: {id}, response:{response}")
        logger.error(f"ERROR- {e}, id: {id}, address: {address2}, response:{response}")
        return None

def main():
    """
    Reads a CSV file containing building permit data and searches for matching zipcodes using the `get_zipcode` function.
    If a match is found, the corresponding data is saved to a text file and printed to the console.
    """
           
    df = pd.read_csv(DATA_SOURCE_PATH)  
    matching_ids = []

    for index, row in df.iterrows():
        zipcode = get_zipcode(row['ID'], "", row['Address2'], CITY, STATE)
        if zipcode in TARGET_ZIPCODES:
            matching_ids.append({
                "zipcode": zipcode,
                "id": row['ID'],
                "address": f"{row['Address2']}",
                "ISSUE_DATE": row['ISSUE_DATE'],
                "YEAR": row['YEAR']
            })
            logger.info(f"MATCH FOUND- id:{row['ID']}, zipcode: {zipcode}, address:{row['Address2']}")


    # Save matching_ids to a text file
    with open(SAVE_FILE_PATH, 'w') as file:
        for item in matching_ids:
            line = f"id: {item['id']}, zipcode: {item['zipcode']}, address: {item['address']}, ISSUE_DATE: {item['ISSUE_DATE']}, YEAR: {item['YEAR']}\n"
            file.write(line)
            print(line)

def test():
    address1=""
    address2="150 N RIVERSIDE PLZ"
    print(get_zipcode(0, address1, address2, CITY, STATE))

if __name__ == '__main__':
    test()
    main()
