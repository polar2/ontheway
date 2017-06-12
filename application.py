from flask import request, Flask, jsonify, render_template, url_for
from helpers import calc_midpoint,find_places,pick_closest
import os

application = Flask(__name__)

@application.route('/',methods=['GET','POST'])
def hello_world():
	if request.method == 'POST':
		o = request.form['orig']
		o = o.replace(" ","+")
		o = o.replace(",","")
		d = request.form['dest']
		d = d.replace(" ","+")
		d = d.replace(",","")
		m = calc_midpoint(o,d)
		if m['lat']==99:
			return render_template("error.html",error_str="origin not found")
		if m['lon']==99:
			return render_template("error.html",error_str="destination not found")
		if request.form['stop_type']=='cafe':
			n = find_places(m,'cafe','')
		if request.form['stop_type']=='star':
			n = find_places(m,'cafe','Starbucks')
		if request.form['stop_type']=='rest':
			n = find_places(m,'restaurant','')
		if request.form['stop_type']=='mcdo':
			n = find_places(m,'restaurant','McDonalds')
		if len(n)==0:
			return render_template("error.html",error_str="no feasible stops found")
		stps = pick_closest(o,d,n)
		if len(stps)==0:
			return render_template("error.html",error_str="no feasible directions found")
		api_key = os.environ.get('MY_API_KEY', None)
		return render_template("directions.html",orig_var=o,dest_var=d,new_places=stps,api_key=api_key)
	if request.method == 'GET':
		return render_template("index.html")

if __name__ == "__main__":
    application.run()
    