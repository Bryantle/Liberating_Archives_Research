import flask
from flask import Response, request, send_file
import json
import sqlite3
import csv

# Create the application.
app = flask.Flask(__name__)

@app.route('/')
def index():
	return flask.render_template('index.html')

	format_ = request.args.get("format", None)
	president = request.args.get("name", "")
	year = request.args.get("year", "")
    month = request.args.get("month", "")
    doc_type = request.args.get("month", "")

	connection = sqlite3.connect("mydatabase.sqlite")
	connection.row_factory = dictionary_factory
	cursor = connection.cursor()

	#Query that gets the records that match the query
	all_records_query = "SELECT hearing.hearing_title as title, hearing.date as date, speech.text as text, \
				speaker.surname as name FROM hearing inner join speech on \
				speech.hearing_id = hearing.hearing_id inner join speaker \
				on speaker.speech_id = speech.speech_id %s %s;"

	where_clause = ""
	if president or year or month or doc_type:
		where_clause = "where "
		if speaker:
			where_clause += " speaker.surname = ? " if speaker else ""
		if year and speaker:
			where_clause += " and "
		if year:
			where_clause += " hearing.date like ? " if len(year)>2 else ""
	limit_statement = "limit 20" if format_ != "csv" else ""

	all_records_query = all_records_query % (where_clause, limit_statement)
	print(all_records_query)

	if speaker and year:
		cursor.execute(all_records_query ,(speaker.lower(), "%"+ year))
	elif speaker:
		cursor.execute(all_records_query ,(speaker.lower(),))
	elif year:
		cursor.execute(all_records_query ,("%"+ year,))
	else:
		cursor.execute(all_records_query)
	records = cursor.fetchall()

	#Query to count the number of records
	count_query =  "SELECT count(*) as count FROM hearing inner join speech on \
				speech.hearing_id = hearing.hearing_id inner join speaker \
				on speaker.speech_id = speech.speech_id %s;"
	count_query = count_query % (where_clause)
	if speaker and year:
		cursor.execute(count_query, (speaker.lower(), "%"+ year))
	elif year:
		cursor.execute(count_query, ("%"+ year,))
	elif speaker:
		cursor.execute(count_query, (speaker.lower()))
	else:
		cursor.execute(count_query)
	#There's a lot of if else going on here but I will send a better solution for you guys to work with
	no_of_records = cursor.fetchall()
	connection.close()

	#Send the information back to the view
	#if the user specified csv send the data as a file for download else visualize the data on the web page
	if format_ == "csv":
		return download_csv(records, "speeches_%s.csv" % (speaker.lower()))
	else:
		years = [x for x in range(2018, 1995, -1)]
		selected_year = int(year) if year else None
		return flask.render_template('speaker.html', records=records, no_of_records=no_of_records[0]['count'], speaker=speaker, years=years, selected_year=selected_year)

########################################################################
# The following are helper functions. They do not have a @app.route decorator
########################################################################
def dictionary_factory(cursor, row):
	"""
	This function converts what we get back from the database to a dictionary
	"""
	d = {}
	for index, col in enumerate(cursor.description):
		d[col[0]] = row[index]
	return d

def download_csv(data, filename):
	"""
	Pass into this function, the data dictionary and the name of the file and it will create the csv file and send it to the view
	"""
	header = data[0].keys() #Data must have at least one record.
	with open('downloads/' + filename, "w+") as f:
		writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		writer.writerow(header)
		for row in data:
			writer.writerow(list(row.values()))

	#Push the file to the view
	return send_file('downloads/' + filename,
				 mimetype='text/csv',
				 attachment_filename=filename,
				 as_attachment=True)


if __name__ == '__main__':
	app.debug=True
	app.run()
