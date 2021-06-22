# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import requests
import json
import config
import csv
def maps_call():
    API_KEY = config.api_key
    response = requests.get("https://maps.googleapis.com/maps/api/place/textsearch/json?query=Los+Angeles+garage&key=" + API_KEY)
    ##response = requests.get("https://maps.lacity.org/lahub/rest/services/LADOT/MapServer/2/query?where=1%3D1&outFields=*&outSR=4326&f=json")
    results = response.json()
    results = results["results"]

    data_file = open('datagarage.csv', 'w', newline='')
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
        try:
            photos.append(i["photos"][0]["photo_reference"])
            tracker.append(i["formatted_address"])
        except:
            pass
    data_file.close()


    for i in range(0, len(photos)):
        photo = requests.get("https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference=" + photos[i] + "&key=" + API_KEY)

        file = open( str(tracker[i])+ ".jpg", "wb")
        file.write(photo.content)
        file.close()

    # Press the green button in the gutter to run the script.
if __name__ == '__main__':
    maps_call()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
