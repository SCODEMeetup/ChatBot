from app import app, dialogflow, refer_mock
from flask import request, jsonify

import dateutil.parser
import json

@app.route('/')
def index():
	return "It Works"

@app.route('/appointments')
def appointments():
	appointments = refer_mock.get_all_appointments()
	appointments_json = []
	for row in appointments:
		appointments_json.append({
				'firstName': row['firstName'],
				'lastName': row['lastName'],
				'pantry': row['name'],
				'dateAndTime': row['dateAndTime']})
	return jsonify(appointments_json)

@app.route('/users')
def users():
	users = refer_mock.get_all_users()
	users_json = []
	for row in users:
		users_json.append({
			'firstName': row['firstName'],
			'lastName': row['lastName'],
			'ssn': row['ssn'],
			'birthDate': row['birthdate'],
			'address': row['address']
			})
	return jsonify(users_json)

@dialogflow.intent('get-ssn-dob-service apt')
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
			Is that you? (We mean do we have the right profile?  The name may be wrong or \
			the address may be wrong.  These may be old.  You would still answer yes.  \
			We’ll give you a chance to change them next.)'.format(res['firstName'], res['lastName'], res['address']))
		df_response.add_output_context('wh-client', 10, {'userId': res['id']})

@dialogflow.intent('name-question change')
def change_client_name(df_request, df_response):
	first_name = df_request.query_result.parameters.get('client').get('firstname')
	last_name = df_request.query_result.parameters.get('client').get('lastname')
	print(first_name)
	print(last_name)
	user_id = df_request.query_result.output_contexts.get('wh-client').parameters.get('userId')

	refer_mock.update_name(first_name, last_name, user_id)

@dialogflow.intent('address-question change')
def change_client_address(df_request, df_response):
	address = df_request.query_result.parameters.get('address')
	user_id = df_request.query_result.output_contexts.get('wh-client').parameters.get('userId')

	refer_mock.update_address(address, user_id)

@dialogflow.intent('order-question asap')
def suggest_pantries_available_asap(df_request, df_response):
	appointments = refer_mock.suggest_pantries_available_asap()

	response = build_pantry_option_response(appointments)
	df_response.set_fulfillment_text(response)

	context_parameters = build_pantry_option_context(appointments)
	df_response.add_output_context('wh-appointment-options', 5, context_parameters)

@dialogflow.intent('order-question wait')
def suggest_pantries_available_wait(df_request, df_response):
	appointments = refer_mock.suggest_pantries_available_wait()
	
	response = build_pantry_option_response(appointments)
	df_response.set_fulfillment_text(response)

	context_parameters = build_pantry_option_context(appointments)
	df_response.add_output_context('wh-appointment-options', 5, context_parameters)

@dialogflow.intent('know/suggest-question know')
def get_available_appointment_for_pantry(df_request, df_response):
	pantry = df_request.query_result.parameters.get('pantry');

	res = refer_mock.get_available_appointment_for_pantry(pantry)

	if res == None:
		df_response.set_fulfillment_text('Sorry, there are no upcoming appointments available for {0}'.format(pantry))
	else:
		df_response.set_fulfillment_text('The soonest appointment I have is {0}. Is this okay? (yes, no)'.format(res['date_and_time'].strftime('%B %-d at %-I:%M %p')))
		context_parameters = {'pantry': res['pantry'], 'dateAndTime': res['date_and_time'].isoformat()}
		df_response.add_output_context('wh-appointment', 5, context_parameters)

@dialogflow.intent('single-question accept')
def confirm_appointment(df_request, df_response):
	user_id = df_request.query_result.output_contexts.get('wh-client').parameters.get('userId')
	pantry = df_request.query_result.output_contexts.get('wh-appointment').parameters.get('pantry')
	appointment_iso_date_time  = df_request.query_result.output_contexts.get('wh-appointment').parameters.get('dateAndTime')

	appointment_date_time = dateutil.parser.parse(appointment_iso_date_time)

	result = refer_mock.book_appointment(user_id, pantry, appointment_date_time)

	if result == None:
		df_response.set_fulfillment_text('Sorry, I wasnt able to confirm your appointment')
	else:
		df_response.set_fulfillment_text('Your appointment at {0} on {1} is confirmed. The address is {2}. {3}'.format(pantry, appointment_date_time.strftime('%B %-d at %-I:%M %p'), result['address'], result['notes']))

@dialogflow.intent('single-question reject')
def suggest_pantries_after_reject(df_request, df_response):
	appointments = refer_mock.suggest_pantries_available_asap()
	
	response = build_pantry_option_response(appointments)
	response = 'Here are some other options: ' + response
	df_response.set_fulfillment_text(response)

	context_parameters = build_pantry_option_context(appointments)
	df_response.add_output_context('wh-appointment-options', 5, context_parameters)


@dialogflow.intent('suggest-pantry accept')
def confirm_appointment_from_options(df_request, df_response):
	user_id = df_request.query_result.output_contexts.get('wh-client').parameters.get('userId')
	appointment_list = df_request.query_result.output_contexts.get('wh-appointment-options').parameters.get('appointments')
	selected_appointment = int(df_request.query_result.parameters.get('selectedAppointment'))

	if selected_appointment < 1 or selected_appointment > 3:
		df_response.set_fulfillment_text('You must select a number from 1 to 3')
		return

	pantry = appointment_list[selected_appointment - 1]['pantry']
	appointment_date_time = dateutil.parser.parse(appointment_list[selected_appointment - 1]['dateAndTime'])

	result = refer_mock.book_appointment(user_id, pantry, appointment_date_time)

	if result == None:
		df_response.set_fulfillment_text('Sorry, I wasnt able to confirm your appointment')
	else:
		df_response.set_fulfillment_text('Your appointment at {0} on {1} is confirmed. The address is {2}. {3}'.format(pantry, appointment_date_time.strftime('%B %-d at %-I:%M %p'), result['address'], result['notes']))


def build_pantry_option_response(appointments):
	appointment_strings = []
	for appointment in appointments:
		appointment_strings.append('{0} on {1}'.format(appointment['pantry'], appointment['date_and_time'].strftime('%B %-d at %-I:%M %p')))

	return '1) {0}, 2) {1}, 3) {2}. Respond with number to confirm one.'.format(appointment_strings[0], appointment_strings[1], appointment_strings[2])

def build_pantry_option_context(appointments):
	context_parameters = {'appointments': []}
	for appointment in appointments:
		context_parameters['appointments'].append({'pantry': appointment['pantry'], 'dateAndTime': appointment['date_and_time'].isoformat()})
