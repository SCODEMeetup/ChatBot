class DialogFlowResponse:

	def __init__(self, session):
		self._session = session;
		self._response_dict = {'fulfillmentText': '', 'outputContexts': []}

	def set_fulfillment_text(self, text):
		self._response_dict['fulfillmentText'] = text

	def add_output_context(self, name, lifespan, parameters):
		context = {'name': self._session + '/contexts/' + name,
				'lifespanCount': lifespan,
				'parameters': parameters}
		self._response_dict['outputContexts'].append(context)

	def getRawResponse(self):
		return self._response_dict

	class Context:

		def __init__(self, name, lifespan, parameters):
			self._name = name
			self._lifespan_count = lifespan 
			self._parameters = parameters

