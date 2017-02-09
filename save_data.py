from activesg import ActiveSG
from credentials import credentials
from datetime import datetime, timedelta
import csv
import json

active_sg = ActiveSG(credentials['username'], credentials['password'])
active_sg.save_list_of_activities()
active_sg.save_list_of_venues()

def save_data():
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    venues = active_sg.get_venues_by_activity('18')
    date_range = create_date_range()
    jsonArray = []

    with open("/home/chip/active-sg-badminton/data/"+timestamp, 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',')
        for d in date_range:
            for venue in venues['results']:
                print (d + " : " + venue['venue_id'])
                url =active_sg.create_url_for_activesg_booking('18', venue['venue_id'], d)
                data = [timestamp, d]
                result = active_sg.activesg_full_summary_badminton(d, venue['venue_id'])
                venue = result.keys()[0]
                value = result.values()[0]
                data.append(venue)
                data = data + value
                spamwriter.writerow(data)
                jsonData = {"update_timestamp":timestamp,
                            "booking_date":d,
                            "venue":venue,
                            "avail":value,
                            "url":url}
                jsonArray.append(jsonData)
            data = [timestamp, d]
            result = active_sg.arena_full_summary_badminton(d)
            venue = result.keys()[0]
            value = result.values()[0]
            data.append(venue)
            data = data + value
            spamwriter.writerow(data)
            url =active_sg.create_url_for_arena_booking()
            jsonData = {"update_timestamp":timestamp,
                            "booking_date":d,
                            "venue":venue,
                            "avail":value,
                            "url":url}
            jsonArray.append(jsonData)
        with open("/home/chip/active-sg-badminton/data/latest.json","w") as f:
            json.dump(jsonArray,f)

def create_date_range():
    for n in range(0, 14):
        yield (datetime.now() + timedelta(n, 0)).strftime("%Y-%m-%d")


save_data()
