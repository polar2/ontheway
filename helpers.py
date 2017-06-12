import urllib, json, os

def calc_midpoint(orig,dest):
	api_key = os.environ.get('MY_API_KEY', None)
	orig_src = "https://maps.googleapis.com/maps/api/geocode/json?address="+orig+"&key="+api_key
	dest_src = "https://maps.googleapis.com/maps/api/geocode/json?address="+dest+"&key="+api_key
	orig_resp = urllib.urlopen(orig_src)
	dest_resp = urllib.urlopen(dest_src)
	orig_json = json.loads(orig_resp.read())
	dest_json = json.loads(dest_resp.read())
	mid = {}
	if orig_json['status']!='OK':
		mid['lat'] = 99
		mid['lon'] = 50
		return mid
	if dest_json['status']!='OK':
		mid['lat'] = 50
		mid['lon'] = 99
		return mid
	orig_location = orig_json['results'][0]['geometry']['location']
	dest_location = dest_json['results'][0]['geometry']['location']
	mid['lat'] = (orig_location['lat']+dest_location['lat'])/2
	mid['lon'] = (orig_location['lng']+dest_location['lng'])/2
	return mid

def find_places(mid,search_for,search_name):
	api_key = os.environ.get('MY_API_KEY', None)
	if search_name=='':
		mid_src = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="+str(mid['lat'])+","+str(mid['lon'])+"&rankby=distance&type="+search_for+"&key="+api_key
	if search_name!='':
		mid_src = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="+str(mid['lat'])+","+str(mid['lon'])+"&rankby=distance&type="+search_for+"&name="+search_name+"&key="+api_key
	mid_resp = urllib.urlopen(mid_src)
	mid_json = json.loads(mid_resp.read())
	mid_places = []
	if mid_json['status']!='OK':
		return mid_places
	num_results = min(10,len(mid_json['results']))
	for x in range(num_results):
		new_location = {'name':mid_json['results'][x]['name'], 'place_id':mid_json['results'][x]['place_id'], 'address':mid_json['results'][x]['vicinity']}
		mid_places.append(new_location.copy())
	return mid_places

class Midpoint(object):
    def __init__(self, name, place_id, address, tt1, tt2, tt3):
        self.name = name
        self.place_id = place_id
        self.address = address
        self.tt1 = tt1
        self.tt2 = tt2
        self.tt3 = tt3

def getSort(midp):
    return midp.tt3

def pick_closest(orig,dest,mids):
	api_key = os.environ.get('MY_API_KEY', None)
	mids_str = ""
	for x in mids:
		mids_str = mids_str+"place_id:"+x['place_id']+"|"
	step1_src = "https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins="+orig+"&destinations="+mids_str+"&key="+api_key
	step2_src = "https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins="+mids_str+"&destinations="+dest+"&key="+api_key
	step1_resp = urllib.urlopen(step1_src)
	step2_resp = urllib.urlopen(step2_src)
	step1_json = json.loads(step1_resp.read())
	step2_json = json.loads(step2_resp.read())
	if step1_json['status']!='OK':
		sorted_lst = []
		return sorted_lst
	if step2_json['status']!='OK':
		sorted_lst = []
		return sorted_lst
	num_results = len(step1_json['rows'][0]['elements'])
	mids_lst = []
	for x2 in range(num_results):
		mids_lst.append(Midpoint(mids[x2]['name'],mids[x2]['place_id'],mids[x2]['address'],step1_json['rows'][0]['elements'][x2]["duration"]["value"]/60,step2_json['rows'][x2]['elements'][0]["duration"]["value"]/60,(step1_json['rows'][0]['elements'][x2]["duration"]["value"]+step2_json['rows'][x2]['elements'][0]["duration"]["value"])/60))
	num_to_show = min(4,len(mids_lst))
	sorted_lst = sorted(mids_lst, key=getSort)[0:num_to_show]
	return(sorted_lst)
