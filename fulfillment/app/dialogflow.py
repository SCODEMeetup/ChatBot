import json
from functools import wraps
from flask import request, Response

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
		intent = json_data['queryResult']['intent']['displayName']

		try:
			view_func = self._intent_to_function_map[intent]
		except KeyError:
			raise NotImplementedError('No registered intent handler for intent: "{}"'.format(intent))

		result_json = view_func(json_data)

		if result_json is not None:
			response = Response(
					response = json.dumps(result_json),
					status = 200,
					mimetype = 'application/json')
			return response
		return "", 400

	def intent(self, intent_name):

		def decorator(f):
			self._intent_to_function_map[intent_name] = f

			@wraps(f)
			def wrapper(*args, **kw):
				self._flask_view_func(*args, **kw)
			return f
		return decorator

