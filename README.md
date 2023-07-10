# USPS-Address-Zipcode-Lookup

This project will help you to complete two tasks:
1. Transfer US address to zipcode using the USPS Address Validation API, which not only validate and standardize addresses but also return corresponding zipcodes
2. Find zipcodes that matches with your target zipcodes

## Required Packages

- pandas
- requests
- logging

## Installation

1. Clone the repository to your local machine.
2. Install the required packages using pip: `pip install pandas requests logging`.
3. Set up your USPS API userid and other input by following the instructions.

## Usage

1. Replace the TODOs in the `main.py` file with your target zip codes, city, state, USPS API user_id, TARGET_ZIPCODES, path to your csv file, and matching results saved file
2. Run the `main.py` file: `python main.py`.
3. The output file will be saved to the `SAVE_FILE_PATH` directory.

## Functions

### `def get_zipcode`

```py
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
```

### `def main`, which calls get_zipcode() and search for matching zipcodes 

```py
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
```
