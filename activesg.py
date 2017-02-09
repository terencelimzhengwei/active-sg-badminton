import datetime
import json
import os.path
import time

import requests

class ActiveSG(object):
    def __init__(self, username=None, password=None):
        self.login_status = False
        self.login_details = None
        self.access_token = None

        self.login(username, password)

        #if not os.path.isfile('/home/chip/active-sg-badminton/venues.json'):
        self.save_list_of_venues()
        print('saving venues')
        #if not os.path.isfile('/home/chip/active-sg-badminton/activities.json'):
        self.save_list_of_activities()
        print('saving activities')

        with open('/home/chip/active-sg-badminton/venues.json') as data_file:
            self.venues = json.load(data_file)

        with open('/home/chip/active-sg-badminton/activities.json') as data_file2:
            self.activities = json.load(data_file2)

    @staticmethod
    def save_json_to_file(response, filename):
        with open(filename, 'w') as outfile:
            json.dump(response, outfile)
            print('Success')

    @staticmethod
    def format_activesg_timestamps(timefrom, timeto):
        return timefrom[:5] + ' - ' + timeto[:5]

    def save_list_of_activities(self):
        results = self.get_all_activities_available()['results']
        json_data = {}
        for result in results:
            json_data[result['activity_id']] = result['name']
        self.save_json_to_file(json_data, '/home/chip/active-sg-badminton/activities.json')

    def save_list_of_venues(self):
        results = self.get_all_venues_available()['results']
        json_data = {}
        for result in results:
            json_data[result['venue_id']] = result['name']
        self.save_json_to_file(json_data, '/home/chip/active-sg-badminton/venues.json')

    def login(self, username, password):
        url = "https://members.myactivesg.com:8889/api/index.php/v2/account/account_login"

        headers = {
            'Cache-Control': 'no-cache',
            'Connection': 'Keep-Alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Length': '432',
            'Host': 'members.myactivesg.com:8889',
            'Accept-Encoding': 'gzip'
        }

        payload = {
            'login_type': 'normal',
            'user_name': username,
            'password': password,
            'platform': 'android'
        }

        r = requests.post(url, headers=headers, data=payload)

        self.login_details = r.json()

        if self.login_details['status_code'] == 1010:
            self.access_token = self.login_details['results']['access_token']
            self.login_status = True
            return 'Login Success'
        else:
            self.login_status = False
            self.access_token = None
            return 'Login Failed'

    ########### CODE TO RETRIEVE FROM URL ########

    def request_url(self, url):
        headers = {
            'Cache-Control': 'no-cache',
            'Host': 'members.myactivesg.com:8889',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip'}

        if self.login_status:
            headers['X-authorization'] = self.access_token
        else:
            self.login_status = False
            return "Not logged in"

        r = requests.get(url, headers=headers)

        return r.json()

    ########### GYM RELATED CODE ###########

    @staticmethod
    def get_max_capacity_of_gyms():
        url = "https://members.myactivesg.com:8889/api/index.php/facility/gym/?platform=android"
        return requests.get(url).json()

    @staticmethod
    def get_current_capacity_of_gym(venue_id):
        url = "https://members.myactivesg.com:8889/api/index.php/facility/gym/" + venue_id + "?platform=android"
        return requests.get(url).json()

    ########################################

    def get_raw_slots_activesg(self, activity_id, venue_id, date):
        url = "https://members.myactivesg.com:8889/api/index.php/facility/slots?platform=android&activity_id=" + activity_id + "&venue_id=" + venue_id + "&date=" + date
        return self.request_url(url)

    def get_raw_badminton_slots_activesg(self, venue_id, date):
        return self.get_raw_slots_activesg('18', venue_id, date)

    ########## Static Stuff ################
    def get_virtual_card(self):
        url = "https://members.myactivesg.com:8889/api/index.php/account/my_virtual_card"
        return self.request_url(url)

    def get_profile_details(self):
        url = "https://members.myactivesg.com:8889/api/index.php/account/profile"
        return self.request_url(url)

    def get_venue_activity_details(self, venue_id, activity_id):
        url = "https://members.myactivesg.com:8889/api/index.php/facility/more?platform=android&activity_id=" + activity_id + "&venue_id=" + venue_id
        return self.request_url(url)

    def get_venues_by_activity(self, venue_id):
        url = "https://members.myactivesg.com:8889/api/index.php/facility/venue/" + venue_id + "?platform=android"
        return self.request_url(url)

    def get_all_activities_available(self):
        url = "https://members.myactivesg.com:8889/api/index.php/facility/activity/all?platform=android"
        return self.request_url(url)

    def get_all_venues_available(self):
        url = "https://members.myactivesg.com:8889/api/index.php/facility/venue/all?platform=android"
        return self.request_url(url)

    def get_max_date_for_activity(self, activity_id):
        url = "https://members.myactivesg.com:8889/api/index.php/facility/activity/max_date/" + activity_id + "?platform=android"
        return self.request_url(url)
    ##########################################

    @staticmethod
    def get_all_slots_arena():
        url = "https://bookings.sportshub.com.sg/json/sportsBookings.php"
        r = requests.get(url)
        return r.json()

    def get_badminton_slots_arena(self):
        slots = self.get_all_slots_arena()
        return [x for x in slots if x['sportId'] == '5']

    def get_badminton_slots_by_date(self, date):
        r = self.get_badminton_slots_arena()
        return [x for x in r if x['start'].split(' ')[0] == date]

    @staticmethod
    def format_results_activesg(obj):
        result_new = {'short_name': obj['short_name'],
                      'available_slot': list(filter(lambda x: x['is_available'] == 'Y', obj['timeslots']))}
        return result_new

    @staticmethod
    def format_timestamp_arena(hour_time):
        start = hour_time
        end = (datetime.datetime.strptime("07:00", "%H:%M") + datetime.timedelta(0, 3600)).strftime("%H:%M")
        return start + " - " + end

    def get_available_slots_activesg(self, date, activity, venue):
        courts = self.get_raw_slots_activesg(activity, venue, date)
        result = {'venue': self.venues[venue], 'activity': self.activities[activity], 'date': date}

        if 'results' in courts and courts['results'] != False:
            courts = courts['results']
            result['results'] = list(map(self.format_results_activesg, courts))
        else:
            result['results'] = []
        return result

    @staticmethod
    def convert_date_to_timestamp(dateString):
        return int(time.mktime(datetime.datetime.strptime(dateString, "%Y-%m-%d").timetuple()))

    def get_activesg_available_slots(self, date, activity, venue):
        slots = self.get_available_slots_activesg(date, activity, venue)['results']
        result = {'venue': self.venues[venue], 'activity': self.activities[activity], 'date': date,
                  'available_slots': {}}
        for res in slots:
            for ts in res['available_slot']:
                time_short = self.format_activesg_timestamps(ts['time_from'], ts['time_to'])
                if time_short in result['available_slots']:
                    result['available_slots'][time_short] += 1
                else:
                    result['available_slots'][time_short] = 1
        return result

    def activesg_full_summary(self, date, activity, venue):
        slots = self.get_available_slots_activesg(date, activity, venue)['results']
        result = {'venue': self.venues[venue], 'activity': self.activities[activity], 'date': date,
                  'available_slots': {"7": 0, "8": 0, "9": 0, "10": 0,
                                      "11": 0, "12": 0, "13": 0, "14": 0,
                                      "15": 0, "16": 0, "17": 0, "18": 0,
                                      "19": 0, "20": 0, "21": 0}}
        for res in slots:
            for ts in res['available_slot']:
                time_short = str(int(ts['time_from'][:2]))
                if time_short in result['available_slots']:
                    result['available_slots'][time_short] += 1
                else:
                    result['available_slots'][time_short] = 1
        return result

    def activesg_full_summary_badminton(self, date, venue):
        slots = self.get_available_slots_activesg(date, "18", venue)['results']
        result = {self.venues[venue] : [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]}
        for res in slots:
            for ts in res['available_slot']:
                time_short = int(ts['time_from'][:2]) - 7
                result[self.venues[venue]][time_short]+=1
        return result

    def get_arena_available_slots(self, date):
        slots = self.get_badminton_slots_by_date(date)
        result = {'venue': "OCBC Arena", 'activity': "Badminton", 'date': date, 'available_slots': {}}
        for res in slots:
            time_short = self.format_timestamp_arena(res['start'][11:16])
            result['available_slots'][time_short] = res['courts_avail']
        return result

    def arena_full_summary_badminton(self, date):
        slots = self.get_badminton_slots_by_date(date)
        result = {"OCBC Arena": [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]}
        for res in slots:
            time_short = int(res['start'][11:13]) - 7
            result["OCBC Arena"][time_short] = res['courts_avail']
        return result

    def create_url_for_activesg_booking(self, activity, venue, date):
        timeStamp = self.convert_date_to_timestamp(date)
        url = ("https://members.myactivesg.com/facilities/view/activity/" +
               activity + "/venue/" + venue + "?time_from=" + str(timeStamp))
        return url

    @staticmethod
    def create_url_for_arena_booking():
        url = "https://bookings.sportshub.com.sg/default.php?action=venues"
        return url

    @staticmethod
    def format_summary_to_string(result):
        resultString = 'Activity : ' + result['activity'] + '\n'
        resultString += 'Venue : ' + result['venue'] + '\n'
        resultString += 'Date : ' + result['date'] + '\n'
        resultString += 'Available Courts : '

        if len(result['available_slots']) == 0:
            resultString += 'No available courts'
        else:
            resultString += '\n'

            def getKey(item):
                return item[0]

            for key, val in sorted(result['available_slots'].items(), key=getKey):
                resultString += key + ' : ' + str(val) + '\n'
            resultString = resultString[:-1]
        return resultString

    def available_activesg_badminton_to_string(self, date, venue):
        activesg = self.format_summary_to_string(self.get_activesg_available_slots(date,"18", venue))
        return activesg

    def available_arena_badminton_to_string(self,date):
        arena = self.format_summary_to_string(self.get_arena_available_slots(date))
        return arena

    def all_activesg_badminton_to_string(self, date):
        venues = self.get_venues_by_activity("18")

        result_string = ''

        for venue in venues['results']:
            courts = self.get_activesg_available_slots(date, "18", venue['venue_id'])
            if len(courts['available_slots']) != 0:
                result_string += self.format_summary_to_string(courts) + '\n\n'
        result_string = result_string[:-2]
        return result_string

    def all_badminton_to_string(self,date):
        activesg = self.all_activesg_badminton_to_string(date)
        arena = self.available_arena_badminton_to_string(date)
        return activesg + "\n\n" + arena
