from functools import wraps
from flask import request, Response
from .DialogFlowRequest import DialogFlowRequest
from .DialogFlowResponse import DialogFlowResponse

import json

class DialogFlow:

	def __init__(self, app, route, basic_auth_username, basic_auth_password):

		self.app = app
		self._route = route;
		self._intent_to_function_map = {}
		self._basic_auth_username = basic_auth_username
		self._basic_auth_password = basic_auth_password

		app.add_url_rule(self._route, view_func=self._flask_view_func, methods=['POST'])

	def _flask_view_func(self, *args, **kwargs):

		if (request.authorization.username != self._basic_auth_username or
				request.authorization.password != self._basic_auth_password):
			return "", 401

		json_data = request.get_json(silent=True, force=True)
		#remove
		print(json_data)
		intent = json_data['queryResult']['intent']['displayName']

		try:
			view_func = self._intent_to_function_map[intent]
		except KeyError:
			raise NotImplementedError('No registered intent handler for intent: "{}"'.format(intent))

		df_request = DialogFlowRequest(json_data)
		df_response = DialogFlowResponse(df_request.session)

		view_func(df_request, df_response)

		response = Response(
				response = json.dumps(df_response.getRawResponse()),
				status = 200,
				mimetype = 'application/json')
		return response

	def intent(self, intent_name):

		def decorator(f):
			self._intent_to_function_map[intent_name] = f

			@wraps(f)
			def wrapper(*args, **kw):
				self._flask_view_func(*args, **kw)
			return f
		return decorator

