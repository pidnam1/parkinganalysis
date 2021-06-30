import requests
import json
import os
import config
import csv


def main():
    ###File path names
    directory = "parkingtry"
    csv_name = "parkingdata"

    ##Request
    API_KEY = config.places_api_key
    response = requests.get("https://maps.googleapis.com/maps/api/place/textsearch/json?query=Los+Angeles&type=parking&key=" + API_KEY)
    results = response.json()
    results = results["results"]

    ##Create directory
    path = os.getcwd()
    path = path + "\\" + directory
    os.makedirs(path)
    print(path)

    ##Write csv
    data_file = open(os.path.join(path,csv_name + ".csv"), 'w', newline='')
    csv_writer = csv.writer(data_file)
    count = 0
    photos = []
    tracker = []
    for i in results:
        if count == 0:
            # Writing headers of CSV file
            header = ["Formatted Address", "Latitude", "Longitude", "Name", "Types" ]
            csv_writer.writerow(header)
            count += 1
        csv_writer.writerow([i["formatted_address"], i["geometry"]["location"]["lat"],i["geometry"]["location"]["lng"]
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
        photo = requests.get("https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference=" + photos[i] + "&key=" + API_KEY)

        filename =  str(tracker[i])+ ".jpg"
        file = open(os.path.join(path, filename), "wb")
        file.write(photo.content)
        file.close()

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
                print(row[1], row[0],  row[4], row[7])
                processed_result.append(row[1])
                processed_result.append(row[0])
                processed_result.append(row[4])
                processed_result.append(row[7])

                ## fetch photo data for search in format **address**, Los Angeles
                address = row[7]
                photores = requests.get("https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=" + str(row[4]) + "LosAngeles&inputtype=textquery&fields=photos&key=" + PLACES_API_KEY)
                photores = photores.json()

                ##if entry has photo data, request for photo and write to directory, add "Yes" in
                ## photo column for processed result
                try:
                    ref = photores["candidates"][0]['photos'][0]['photo_reference']
                    print("photores", photores["candidates"][0]['photos'][0]['photo_reference'])
                    photo = requests.get("https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference=" + ref + "&key=" + PLACES_API_KEY)
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
                    "https://maps.googleapis.com/maps/api/elevation/json?locations=" + str(row[1]) + "," + row[0] + "&key="
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
                header = [ "Latitude", "Longitude", "Name", "Formatted Address", "Elevation", "Photo"]
                csv_writer.writerow(header)
                count += 1
            csv_writer.writerow(
                    [i[0], i[1], i[2]
                        , i[3], i[5], i[4]])


def tallestBuilding():
    API_KEY = config.elevation_api_key
    response = requests.get(
        "https://maps.googleapis.com/maps/api/elevation/json?locations=" + "34.05109750994255, -118.25467000161362" + "&key="
        + API_KEY)
    results = response.json()
    results = results["results"]
    print(results)
if __name__ == '__main__':
    elevationData()


