#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  8 18:10:34 2017

@author: pesa
"""
# Zoopla api key = u3639q6jdfu5q6p3qhe6qyk8

# pd.read_html() -> scrape html tables

#from bs4 import BeautifulSoup 
import requests
import json
from datetime import datetime
from time import sleep
import logging

# cookies to be used when making requests to the server
cookies = {}

base_url = 'http://www.spareroom.co.uk'
api_location = 'http://iphoneapp.spareroom.co.uk'
api_search_endpoint = 'flatshares'
api_looking_endpoint = 'flatmates'

# Pretend we are a browser.
headers = {'User-Agent': 'Mozilla/5.0'}
headers2 = {'User-Agent': 'SpareRoomUK 3.1'}

search_pointer = '?search_id='
listing_pointer = 'flatshare/flatshare_detail.pl?flatshare_id='

# Get HTTP response containing raw page contents.
#rooms_req = requests.get(base_url + '/flatshare/', headers=headers)

#rooms_req.content

# Build a tree data structure by parsing the HTML.
#rooms_soup = BeautifulSoup(rooms_req.content, 'lxml')

#print(rooms_soup)

# =============================================================================

# preferences used to make queries to the web application
preferences = {
        'format': 'json',
        'per': 'pcm',
        'page': 1,
        'max_per_page': 1, #max is 100
        'where': 'london',
        }

buddies_preferences = {
        'format': 'json',
        'page': 1,
        'max_per_page': 1, #max is 100
        'where': 'london',
        }

max_pages = 1 # max number of pages to parse per area   

'''
call sequence:
get_rooms() --->  1) search_rooms_in(**) -->  1) req = make_get_request(<url>)
            |                             ->  2) get_room_info(req, **)
            |
             -->  2) save_rooms(**) 
    
    
'''
# hold listings data
listings = {}

# will hold all the room-seekers found
people_looking = dict()
people_looking['areas'] = dict()
people_looking['listings'] = dict()

# will hold all the rooms found
rooms = {}


# =============================================================================

#   METHODS TO REQUEST DATA FROM A URL IN A 'SAFE' WAY

def make_get_request(url=None, cookies=None, headers={'User-Agent': 'Mozilla/5.0'}, proxies=None):
    sleep(1)
    return requests.get(url, cookies=cookies, headers=headers).text


# =============================================================================
    
#   METHODS TO EXTRACT DATA ABOUT ROOMS & SORT IT INTO A DICTIONARY  

def filter_room_info(room_details, room_number=0):
    #exctract relevant details from a room and put it into a dictionary
    latitude = room_details['latitude'] 
    longitude = room_details['longitude'] 
    postcode = room_details['postcode']        
    bills = True if 'bills_inc' in room_details \
        and room_details['bills_inc'] == 'Yes' else False
    rooms_no = int(room_details['rooms_in_property']) if 'rooms_in_property' \
        in room_details else 0
    images = room_details['main_image_square_url'] \
        if 'main_image_square_url' in room_details else None
    accom_type = room_details['accom_type'] if 'accom_type' in room_details else 'Unspecified'
    available_timestamp = datetime.now()
    bold = True if room_details['bold_ad'] == 'Y' else False
    property_type = room_details['property_type']
    couples = True if room_details['couples'] == "Y" else False
    '''
    prices = []
    if 'min_rent' in room_details:
        price = int(room_details['min_rent'].split('.', 1)[0])
        price = price if 'per' in room_details and room_details['per'] == 'pcm' else price * 52 / 12
        prices.append(price)   
    if 'max_rent' in room_details:
        price = int(room_details['max_rent'].split('.', 1)[0])
        price = price if 'per' in room_details and room_details['per'] == 'pcm' else price * 52 / 12
        prices.append(price)
    '''
    price = float(room_details['rooms'][room_number]['room_price'])
    price = price if 'per' in room_details and room_details['per'] == 'pcm' else price * 52 / 12
    deposit = room_details['rooms'][room_number]['security_deposit']
    if deposit is None : deposit = 0 
    else : deposit=float(deposit)
    ensuite = True if room_details['rooms'][room_number]['ensuite'] == 'Y' else False
    available = True if room_details['rooms'][room_number]['room_status'] == 'available' \
        else False
    room_type = room_details['rooms'][room_number]['room_type']
    furnished = True if room_details['rooms'][room_number]['room_furnishings'] == 'furnished' else False
    room_info = {
            'latitude' : float(latitude),
            'longitude' : float(longitude),
            'postcode' : postcode,
            'listing_accomm_type' : accom_type,
            'property_type': property_type,
            'room_type' : room_type,
            'ensuite': ensuite,
            'images': images,
            'price': price,
            'price': price,
            'available':available,
            'timestamp': available_timestamp.isoformat(), #ISO 8601 format: YYYY-MM-DDTHH:MM:SS
            'deposit': deposit,
            'furnished': furnished,
            'bold_ad':bold,
            'bills_included': bills,
            'tot_rooms': rooms_no, 
            'couples_allowed': couples               
            }
    return room_info
    
# =============================================================================    

def search_rooms_in(area):
    global preferences
    preferences['page'] = 1
    preferences['where'] = area.lower() # str.lower() makes it lowercase
    
    rooms = {}
    
    params = '&'.join(['{key}={value}'.format(
            key=key, value=preferences[key]) for key in preferences])
    url = '{location}/{endpoint}?{parameters}'.format(
            location=api_location, endpoint=api_search_endpoint, parameters=params)
    
    try:
        sparerooms_reqs = make_get_request(url=url, cookies=cookies, headers=headers)
        #print(sparerooms_reqs) # from this we realise that the text 
                #spat out by the above func. is really a json file, so...
        results = json.loads(sparerooms_reqs)
    except Exception as e:
        print('Error Getting {area}: {message} (skipping...)'.format(area=area, message=e.message))
        return rooms 
    if results['success'] == 0 : 
        print(area, ' is not a valid search area for Room Seekers: IGNORED')
        return rooms                  
    if int(results['count']) > 10000 : #if there are more than 10k results, there must be an error: exclude this area
        print(area, ' is not returning valid search results for Room Listings: IGNORED')
        return rooms   
    pages = int(results['pages']) if 'pages' in results else 0
    
    for page in range(1, min(pages, max_pages)+1):
        preferences['page'] = page      
        params = '&'.join(
                ['{key}={value}'.format(key=key, value=preferences[key]
                ) for key in preferences])
        url = '{location}/{endpoint}?{params}'.format(
                location=api_location, endpoint=api_search_endpoint, params=params)
        sparerooms_reqs = make_get_request(url=url, cookies=cookies, headers=headers)
        results = json.loads(sparerooms_reqs) 
        '''
        # export raw spareroom page (json data)
        with open('raw_spareroom.json', 'w') as f:
            f.write(json.dumps(results, indent=2, sort_keys=True))
        ''' 
        for listing_data in results['results']: # iterate through listings
            #print(room_data,'\n') # checkpoint
            room_id = listing_data['advert_id']
            if 'days_of_wk_available' in listing_data and \
                listing_data['days_of_wk_available'] != '7 days a week':
                    continue #only consider normal lets (7 days per week)
            if 'ad_type' in listing_data and listing_data['ad_type'] != 'offered':
                continue 
            rooms_no = len(listing_data['rooms']) if 'rooms' in listing_data else 0
            for r in range(rooms_no):
                room_info = filter_room_info(listing_data, r)
                id_code = room_id + str(r).rjust(3, '0')
                if id_code in rooms: # avoid duplicates
                    continue
                rooms[id_code] = {
                                    **{'ad_id':room_id, 'room_num_within_ad':r, 'search':area},
                                    **room_info
                                 }
    return rooms

# =============================================================================
  
#   METHOD TO EXTRACT DATA ABOUT ROOM-SEEKERS & SORT IT INTO A DICTIONARY   

def get_combined_seekers(area, seekers={}):
    global buddies_preferences
    buddies_preferences['page'] = 1
    buddies_preferences['where'] = area.lower() # str.lower() makes it lowercase

    params = '&'.join(['{key}={value}'.format(
            key=key, value=buddies_preferences[key]) for key in buddies_preferences])
    flatmates_url = '{location}/{endpoint}?{params}'.format(
            location=api_location, endpoint=api_looking_endpoint, params=params)
    try:
        flatmates_results = json.loads(make_get_request(flatmates_url, cookies=cookies, headers=headers))
    except Exception as e:
        print('Error Getting {area}: {message} (skipping...)'.format(area=area, message=e.message))
        return seekers
    if flatmates_results['success'] == 0 : 
        print(area, ' is not a valid search area for Room Seekers: IGNORED')
        return seekers    
    if int(flatmates_results['count']) > 10000 : #if there are more than 10k results, there must be an error: exclude this area
        print(area, ' is not returning valid search results for Room Seekers: IGNORED')
        return seekers
    
    pages = int(flatmates_results['pages']) if 'pages' in flatmates_results else 0
 
    if not seekers:
        seekers['listings'] = {}
        seekers['areas'] = { area : int(flatmates_results['count']) }
    
    seekers['areas'] = {**seekers['areas'], **{area:int(flatmates_results['count'])} }
    
    for page in range(1, min(pages, max_pages)+1):
        preferences['page'] = page   
        params = '&'.join(['{key}={value}'.format(
            key=key, value=buddies_preferences[key]) for key in buddies_preferences])
        flatmates_url = '{location}/{endpoint}?{params}'.format(
            location=api_location, endpoint=api_looking_endpoint, params=params)
        flatmates_results = json.loads(make_get_request(flatmates_url, cookies=cookies, headers=headers))
        
        for flatmate_data in flatmates_results['results']: #iterate through listings
            #print(room_data,'\n') # checkpoint
            seeker_id = flatmate_data['advert_id']
            rooms_wanted = int(flatmate_data['number_of_rooms_required'])
            combined_b = int(flatmate_data['combined_budget'])
            couples = True if flatmate_data['couples'] == 'Y' else False
            img = flatmate_data['main_image_square_url'] if 'main_image_square_url' in flatmate_data else None
            # if the seeker is also looking in previously checked areas,
            # simply keep track of this in his data
            if seeker_id in seekers['listings']: 
                seekers['listings'][seeker_id]['searching_in'].append(area)
            else:
                seekers['listings'][seeker_id] = {
                                        'ad_id':seeker_id, 
                                        'name': flatmate_data['advertiser_name'],
                                        'rooms_wanted':rooms_wanted, 
                                        'searching_in':[area],
                                        'combined_budget':combined_b,
                                        'timestamp' : datetime.now().isoformat(), #ISO 8601 format: YYYY-MM-DDTHH:MM:SS
                                        'couple': couples,
                                        'img':img
                                    }
    return seekers
    #return flatmates_results {} #commented line returns everything

# =============================================================================

#   METHODS TO SAVE DATA EXTRACTED TO LOCAL JSON FILE
    
# file to store the rooms in
file_name = 'rooms.json'

# file to store the people looking in
file_name2 = 'flatmates.json'
        
def save_rooms(rooms):
    """Saves the found rooms in the defined file."""
    # save the rooms found in a json file
    try:
        with open(file_name, 'w') as f:
            f.write(json.dumps(rooms, indent=2, sort_keys=True))

    # catch exceptions in case it cannot create the file or something wrong
    # with json.dumps
    except (IOError, ValueError) as e:
        logging.error(e.strerror, extra={'function': 'save_rooms'})


def save_flatmates(people_looking):
    """Saves the found rooms in the defined file."""
    # save the rooms found in a json file
    try:
        #'''
        # export raw spareroom page (json data)
        with open(file_name2, 'w') as f:
            f.write(json.dumps(people_looking, indent=2, sort_keys=True))
        #''' 
    # catch exceptions in case it cannot create the file or something wrong
    # with json.dumps
    except (IOError, ValueError) as e:
        logging.error(e.strerror, extra={'function': 'save_rooms'})
    
# =============================================================================
 
# wrapper to search for:
# 1 - rooms in a given area and then save them to a json file
# 2 - people looking for a room in the same area    
def get_rooms(areas):
    global rooms
    global people_looking
    
    for area in areas: 
        rooms = {**rooms, **search_rooms_in(area)} # merge dictionaries
        #print(rooms)
        people_looking = get_combined_seekers(area, people_looking)
        '''
        temp_dict1, temp_dict2 = get_combined_seekers(area)
        people_looking['listings'] = {**temp_dict1, **people_looking['listings']}
        people_looking['areas'] = {**temp_dict2, **people_looking['areas']}
        '''       
    save_flatmates(people_looking)
    save_rooms(rooms) 
    
# =============================================================================
        
str_areas = 'SE1 SE1P SE2 SE3 SE4 SE5 SE6 SE7 SE8 SE9 SE10 SE11 SE12 SE13 SE14 SE15 SE16 SE17 SE18 SE19 SE20 SE21 SE22 SE23 SE24 SE25 SE26 SE27 SE28 SE99' 
areas = str_areas.split()

    # South East London -> SE1 SE2 SE3 SE4 SE5 SE6 SE7 SE8 SE9 SE10 SE11 SE12 SE13 SE14 SE15 SE16 SE17 SE18 SE19 SE20 SE21 SE22 SE23 SE24 SE25 SE26 SE27 SE28 -> [SPARE ROOM DOES NOT INCLUDE SE99 AND SE1P] The area contains approximately 412,444 households with a population of about 988,126 (2011 census)
    # Croydon postcodes -> CR0 CR2 CR3 CR4 CR5 CR6 CR7 CR8 CR9 [ SPARE ROOM DOES NOT HAVE CR44] CR90 -> The area contains approximately 158,695 households with a population of about 405,236 (2011 census)

get_rooms(areas)
