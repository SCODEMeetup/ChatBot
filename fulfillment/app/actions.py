from app import app, dialogflow, refer_mock
from flask import request, jsonify

import dateutil.parser

@app.route('/')
def index():
	return "It Works"

@dialogflow.intent('1.all.lookup-user')
def lookupUser(df_request, df_response):
	ssn = df_request.query_result.parameters.get('ssn')
	dob = df_request.query_result.parameters.get('dob')

	parsed_dob = dateutil.parser.parse(dob).strftime('%Y-%m-%d')
	parsed_ssn = str(int(ssn))
	# need to deal with ssn's starting with a 0
	res = refer_mock.search_for_user(parsed_ssn, parsed_dob)

	if res == None:
		df_response.set_fulfillment_text('I did not find {0} and {1} in the system. \
				Are those entries correct?'.format(parsed_ssn, parsed_dob))
	else:
		df_response.set_fulfillment_text('I found {0} {1} at {2} in our system. \
			Is that you?'.format(res['firstName'], res['lastName'], res['address']))


