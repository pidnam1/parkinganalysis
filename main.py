# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import requests
import json
import os
import config
import csv


def main():
    ###File path names
    directory = "parking"
    csv_name = "parkingdata"

    ##Request
    API_KEY = config.api_key
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


if __name__ == '__main__':
    main()


