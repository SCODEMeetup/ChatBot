from app import app, dialogflow, refer_mock
from flask import request, jsonify

import dateutil.parser

@app.route('/')
def index():
	return "It Works"

@dialogflow.intent('get-ssn-dob-service')
def lookup_user(df_request, df_response):
	ssn = df_request.query_result.parameters.get('ssn')
	dob = df_request.query_result.parameters.get('dob')

	parsed_dob = dateutil.parser.parse(dob)
	dob_string = parsed_dob.strftime('%Y-%m-%d')
	
	# zfill for ssn's starting with a 0
	parsed_ssn = str(int(ssn)).zfill(4)

	res = refer_mock.search_for_user(parsed_ssn, dob_string)

	if res == None:
		df_response.set_fulfillment_text('I did not find {0} and {1} in the system. \
				Are those entries correct?'.format(parsed_ssn, parsed_dob.strftime('%B %e, %Y')))
	else:
		df_response.set_fulfillment_text('I found {0} {1} at {2} in our system. \
			Is that you?'.format(res['firstName'], res['lastName'], res['address']))
		df_response.add_output_context('wh-client', 10, {'userId': res['id']})

@dialogflow.intent('know/suggest-question know')
def get_available_appointment_for_pantry(df_request, df_response):
	pantry = df_request.query_result.parameters.get('pantry');

	res = refer_mock.get_available_appointment_for_pantry(pantry)

	if res == None:
		df_response.set_fulfillment_text('Sorry, there are no upcoming appointments available for {0}'.format(pantry))
	else:
		df_response.set_fulfillment_text('The soonest appointment I have is {0}. Is this okay? (yes, no)'.format(res['date_and_time'].strftime('%B %d at %I:%M %p')))
		context_parameters = {'pantry': res['pantry'], 'dateAndTime': res['date_and_time'].isoformat()}
		df_response.add_output_context('wh-appointment', 1, context_parameters)

@dialogflow.intent('single-question accept')
def confirm_appointment(df_request, df_response):
	user_id = df_request.query_result.output_contexts.get('wh-client').parameters.get('userId')
	pantry = df_request.query_result.output_contexts.get('wh-appointment').parameters.get('pantry')
	appointment_iso_date_time  = df_request.query_result.output_contexts.get('wh-appointment').parameters.get('date_and_time')

	appointment_date_time = dateutil.parser.parse(appointment_iso_date_time)

	success = refer_mock.bookAppointment(user_id, appointment_date_time)

	if success == True:
		df_response.set_fulfillment_text('')
	else:
		df_response.set_fulfillment_text('Sorry, I wasnt able to confirm your appointment')
