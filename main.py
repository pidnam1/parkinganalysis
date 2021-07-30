import requests
import json
import os
from csv import writer
import self as self
import config
import csv
import time
from urllib3 import PoolManager
import urllib.request
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import sys
import time
import logging
import io
import pandas as pd

'''
Finds parking garages in Los Angeles and places that info in Excel file
Also fetches relevant pictures of the found garages
'''
def main():
    ###File path names
    directory = "parkingtry"
    csv_name = "parkingdata"

    ##Request
    API_KEY = config.places_api_key
    response = requests.get(
        "https://maps.googleapis.com/maps/api/place/textsearch/json?query=Los+Angeles&type=parking&key=" + API_KEY)
    results = response.json()
    results = results["results"]

    ##Create directory
    path = os.getcwd()
    path = path + "\\" + directory
    os.makedirs(path)
    print(path)

    ##Write csv
    data_file = open(os.path.join(path, csv_name + ".csv"), 'w', newline='')
    csv_writer = csv.writer(data_file)
    count = 0
    photos = []
    tracker = []
    for i in results:
        if count == 0:
            # Writing headers of CSV file
            header = ["Formatted Address", "Latitude", "Longitude", "Name", "Types"]
            csv_writer.writerow(header)
            count += 1
        csv_writer.writerow([i["formatted_address"], i["geometry"]["location"]["lat"], i["geometry"]["location"]["lng"]
                                , i["name"], i["types"]])

        print(i)

        ##Store photo info
        try:
            photos.append(i["photos"][0]["photo_reference"])
            tracker.append(i["formatted_address"])
        except:
            pass
    data_file.close()

    ## Get photos
    for i in range(0, len(photos)):
        photo = requests.get("https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference=" + photos[
            i] + "&key=" + API_KEY)

        filename = str(tracker[i]) + ".jpg"
        file = open(os.path.join(path, filename), "wb")
        file.write(photo.content)
        file.close()

'''
Gets elevation and relevant photos from existing list of addresses
Creates new excel file with elevation info and downloads photos
'''
def elevationData():
    ##name files
    directory = "elevation"
    csv_name = "elevationdata"

    ##create directory
    path = os.getcwd()
    path = path + "\\" + directory
    os.makedirs(path)
    print(path)

    ##fetch api keys
    API_KEY = config.elevation_api_key
    PLACES_API_KEY = config.places_api_key

    ##open and read file
    with open('citydata.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        processed_result = []
        processed_results = []

        ##define headers and append data to proccessed_result
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                print(row[1], row[0], row[4], row[7])
                processed_result.append(row[1])
                processed_result.append(row[0])
                processed_result.append(row[4])
                processed_result.append(row[7])

                ## fetch photo data for search in format **address**, Los Angeles
                address = row[7]
                photores = requests.get(
                    "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=" + str(
                        row[4]) + "LosAngeles&inputtype=textquery&fields=photos&key=" + PLACES_API_KEY)
                photores = photores.json()

                ##if entry has photo data, request for photo and write to directory, add "Yes" in
                ## photo column for processed result
                try:
                    ref = photores["candidates"][0]['photos'][0]['photo_reference']
                    print("photores", photores["candidates"][0]['photos'][0]['photo_reference'])
                    photo = requests.get(
                        "https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference=" + ref + "&key=" + PLACES_API_KEY)
                    filename = address + ".jpg"
                    file = open(os.path.join(path, filename), "wb")
                    file.write(photo.content)
                    file.close()
                    processed_result.append("Yes")

                    ##No photo data add "No" to photo column
                except:
                    processed_result.append("No")

                ##Get elevation data for entry by lat-long
                response = requests.get(
                    "https://maps.googleapis.com/maps/api/elevation/json?locations=" + str(row[1]) + "," + row[
                        0] + "&key="
                    + API_KEY)
                results = response.json()
                results = results["results"]
                processed_result.append((results[0]['elevation']))
                print("Processed", processed_result)
                line_count += 1

                ## add processed_result to processed_results array
                processed_results.append(processed_result)
                processed_result = []
        print(f'Processed {line_count} lines.')

        ##Create csv with **csv_name** defined earlier
        data_file = open(os.path.join(path, csv_name + ".csv"), 'w', newline='')
        csv_writer = csv.writer(data_file)
        count = 0

        ##loop through processed results array, add each entry
        for i in processed_results:
            if count == 0:
                # Writing headers of CSV file
                header = ["Latitude", "Longitude", "Name", "Formatted Address", "Elevation", "Photo"]
                csv_writer.writerow(header)
                count += 1
            csv_writer.writerow(
                [i[0], i[1], i[2]
                    , i[3], i[5], i[4]])

'''
Definition of Address class used in webscraper
Makes code easier to read and debug
'''
class Address:
    def __init__(self, code, address, lat, long, name):
        self.code = code
        self.address = address
        self.lat = lat
        self.long = long
        self.name = name

'''Finds addresses, name, and lat long of relevant cities parking and prepares them for next function'''
def multipleParking():
    ##Request
    API_KEY = config.places_api_key
    formatted_addresses = []
    cities = []
    addy_arr = []
    # Using readlines()
    file1 = open('cities_list.txt', 'r')
    lines = file1.readlines()

    count = 0
    # Strips the newline character
    for line in lines:
        print(line.strip())
        cities.append(line.strip())
    for i in cities:
        response = requests.get(
        "https://maps.googleapis.com/maps/api/place/textsearch/json?query=" + i + ",CA&type=parking&key=" + API_KEY)
        results = response.json()
        results = results["results"]
        for i in results:
            print(i["formatted_address"], i["geometry"]["location"]["lat"], i["geometry"]["location"]["lng"]
        , i["name"], i["types"])
            if i["formatted_address"] in formatted_addresses:
                pass
            else:
                formatted_addresses.append(i["formatted_address"])
                addy = Address(address= i["formatted_address"], lat = i["geometry"]["location"]["lat"], long = i["geometry"]["location"]["lng"], name = i["name"] )
                addy_arr.append(addy)
    print("----------------------------------")
    print(len(addy_arr))
    try:
        with io.open('mapsgot.txt', 'w', encoding="utf-8") as f:
            for i in addy_arr:
                f.write(i.address)
                f.write("\n")
                f.write(str(i.lat))
                f.write("\n")
                f.write(str(i.long))
                f.write("\n")
                f.write(i.name)
                f.write("\n")
            f.close()
        web_expand(addy_arr)
    except:
        web_expand(addy_arr)
'''
Creates excel file with related images from addresses searched on google maps
Also downloads the images
 '''

def nearby_try():
    file1 = io.open('mapsgot.txt', 'r', encoding="utf-8")
    lines = file1.readlines()
    addresses=[]
    lats = []
    longs = []
    codes = []
    count = 0
    # Strips the newline character
    addy_arr = []
    for line in lines[0:]:
        if count % 4 == 0:
            print ("ADDRESS: ", line.strip())
            addresses.append(line.strip())
            if count >= 0 and count < 4025:
                codes.append("L")
            if count >= 4025 and count < 4437:
                codes.append("V")
            if count >= 4437:
                codes.append("O")

        if count % 4 == 1:
            print("LAT: ", line.strip())
            lats.append(line.strip())
        if count % 4 == 2:
            print("LONG: ", line.strip())
            longs.append(line.strip())

        ##if count == 4432:
        count += 1
    ##check that all arrays have same count, important
    print("CHECKING CODES IS OK: ", codes)
    print("SHOULD ALL BE THE SAME: ", len(codes), len(addresses), len(lats), len(longs))
    for h, i, j, k in zip(codes, addresses, lats, longs):
        addy = Address(code = h, address = i, lat = j, long = k, name = "")
        addy_arr.append(addy)
    sorted_by_distance(addy_arr)

def sorted_by_distance(addy_arr):
    city_counter = {"L": 0, "V": 0, "O": 0}
    print("By Distance: -------------")
    PLACES_API_KEY = config.places_api_key
    cords = []
    file = io.open('pictry.csv', 'r', encoding="utf-8")
    df = pd.read_csv(file)

    ### adds previous cordinates to array so we can check for duplicates
    for i in addy_arr:
        addy = Address(code = i.code, address=i.address, lat= i.lat, long= i.long, name="")
        cords.append(addy)


    ##define array for results of searches, can check in here to make sure we don't double count while we do the search
    lat_check = []

    ##define array we will add found addresses to
    addresses = []

    with io.open('distgot.txt', 'w', encoding="utf-8") as f:
        for i in addy_arr:
            response = requests.get(
                "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=" + str(i.lat) + "," + str(
                    i.long) + "&rankby=distance&type=parking&key=" + PLACES_API_KEY)
            full_results = response.json()
            print(full_results)
            try:
                caught = full_results["next_page_token"]
                print("Caught", caught)
                time.sleep(1.75)
                response_two = requests.get("https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken=" + caught + "&key=" + PLACES_API_KEY)
                results_two = response_two.json()
                results_two = results_two['results']
                print("Second, ", results_two)
                for j in results_two:
                    if j['geometry']['location']['lat'] not in lat_check:
                        lat_check.append(j['geometry']['location']['lat'])
                        addresses.append(Address(code = i.code + str(city_counter[i.code]) , address = "", lat = j['geometry']['location']['lat'], long = j['geometry']['location']['lng'], name = ""))
                        city_counter[i.code] += 1
                try:
                    time.sleep(1.75)
                    caught = results_two["next_page_token"]
                    response_three = requests.get(
                        "https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken=" + caught + "&key=" + PLACES_API_KEY)
                    results_three = response_three.json()
                    results_three = results_three['results']
                    print("Third, " ,results_three)
                    for j in results_three:
                        if j['geometry']['location']['lat'] not in lat_check:
                            lat_check.append(j['geometry']['location']['lat'])
                            addresses.append(Address(code=i.code + str(city_counter[i.code]), address="", lat=j['geometry']['location']['lat'],
                                                     long=j['geometry']['location']['lng'], name=""))
                            city_counter[i.code] += 1
                except:
                    pass

            except:
                pass
            results = full_results["results"]

            print("------------------")
            print("Querying: -> ", i.lat, i.long)
            print(results)

            ##generate proper IDs


            for j in results:
                f.write(j['name'])
                f.write("\n")
                print( j['geometry']['location']['lat'], j['geometry']['location']['lng'])
                if j['geometry']['location']['lat'] not in lat_check:
                    lat_check.append(j['geometry']['location']['lat'])
                    addresses.append(Address(code = i.code + str(city_counter[i.code]), address = "", lat = j['geometry']['location']['lat'], long = j['geometry']['location']['lng'], name = ""))
                    city_counter[i.code] += 1
    print("-------------------------------------")
    print("# OF FOUND ADDRESSES", len(addresses))

    web_expand(addresses)

def web_expand(addresses):
    with io.open('codealltry.csv', 'w', encoding="utf-8") as f_object:
        csv_writer = writer(f_object)
        csv_writer.writerow(["ID", "Lat", "Long", "Name"])
    ##open google maps and write first address, search
        chrome_options = Options()
        maps = webdriver.Chrome(options=chrome_options)
        maps.maximize_window()
        maps.get('https://www.google.com/maps/')
        search_bar = maps.find_element_by_xpath("//*[@id='searchboxinput']")
        search_bar.send_keys(str(addresses[0].lat) + "," + str(addresses[0].long))
        button = maps.find_element_by_id("searchbox-searchbutton")
        button.click()
        time.sleep(6)

        ##grab pic webelement and download from link
        pic = maps.find_element_by_xpath("//*[@id='pane']/div/div[1]/div/div/div[1]/div[1]/button/img")
        src = pic.get_attribute('src')
        urllib.request.urlretrieve(src, addresses[0].code + ".png")
        csv_writer.writerow([addresses[0].code, addresses[0].lat, addresses[0].long, addresses[0].name,
                                 '=HYPERLINK("' + src + '" , "link")'])
        ##loop through rest of address objects
        for i in range(1, len(addresses)):
            search_bar.send_keys(Keys.CONTROL, 'a')
            search_bar.send_keys(Keys.BACKSPACE)
            time.sleep(.1)
            search_bar.send_keys(str(addresses[i].lat) + "," + str(addresses[i].long))
            button.click()
            time.sleep(3)

            ## if no pic, still add other info in except block
            try:
                pic = maps.find_element_by_xpath("//*[@id='pane']/div/div[1]/div/div/div[1]/div[1]/button/img")
                src = pic.get_attribute('src')

                if src != "https://maps.gstatic.com/tactile/pane/default_geocode-2x.png":
                    urllib.request.urlretrieve(src, addresses[i].code + ".png")
                    csv_writer.writerow([addresses[i].code, addresses[i].lat, addresses[i].long, addresses[i].name,
                                         '=HYPERLINK("' + src + '" , "link")'])
                else:
                    csv_writer.writerow([addresses[i].code, addresses[i].lat, addresses[i].long, addresses[i].name,
                                         "default"])


            except:
                try:
                    csv_writer.writerow([addresses[i].code, addresses[i].lat, addresses[i].long, addresses[i].name])
                except:
                    pass

        ##Close everything
        f_object.close()
        maps.close()
def webtry():
    csv_name = "pictry"

    ##create directory
    path = os.getcwd()

    ##put all Address objects in array
    addresses = []
    with open('citydata.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                address = row[7] + ", CA"
                addy = Address(address=address, lat=row[1], long=row[0], name=row[4])
                addresses.append(addy)
    data_file = open(os.path.join(path, csv_name + ".csv"), 'w', newline='')
    csv_writer = csv.writer(data_file)

    ##write header
    csv_writer.writerow(["Address", "Lat", "Long", "Name", "Pic"])

    ##open google maps and write first address, search
    chrome_options = Options()
    maps = webdriver.Chrome(options=chrome_options)
    maps.maximize_window()
    maps.get('https://www.google.com/maps/')
    search_bar = maps.find_element_by_xpath("//*[@id='searchboxinput']")
    search_bar.send_keys(addresses[0].address)
    button = maps.find_element_by_id("searchbox-searchbutton")
    button.click()
    time.sleep(5)

    ##grab pic webelement and download from link
    pic = maps.find_element_by_xpath("//*[@id='pane']/div/div[1]/div/div/div[1]/div[1]/button/img")
    src = pic.get_attribute('src')
    urllib.request.urlretrieve(src, addresses[0].address + ".png")

    ##loop through rest of address objects
    for i in range(1, len(addresses)):
        search_bar.send_keys(Keys.CONTROL, 'a')
        search_bar.send_keys(Keys.BACKSPACE)
        time.sleep(.5)
        search_bar.send_keys(addresses[i].address)
        button.click()
        time.sleep(2.5)

        ## if no pic, still add other info in except block
        try:
            pic = maps.find_element_by_xpath("//*[@id='pane']/div/div[1]/div/div/div[1]/div[1]/button/img")
            src = pic.get_attribute('src')
            urllib.request.urlretrieve(src, addresses[i].address + ".png")
            csv_writer.writerow([addresses[i].address, addresses[i].lat, addresses[i].long, addresses[i].name,
                                 '=HYPERLINK("' + src + '" , "link")'])

        except:
            csv_writer.writerow([addresses[i].address, addresses[i].lat, addresses[i].long, addresses[i].name])
            pass

    ##Close everything
    data_file.close()
    maps.close()

'''
Test to see how elevation works in Google Maps
'''
def tallestBuilding():
    API_KEY = config.elevation_api_key
    response = requests.get(
        "https://maps.googleapis.com/maps/api/elevation/json?locations=" + "34.05109750994255, -118.25467000161362" + "&key="
        + API_KEY)
    results = response.json()
    results = results["results"]
    print(results)


if __name__ == '__main__':
    nearby_try()
