class DialogFlowRequest:

	def __init__(self, json):
		self._request_json = json
		self._response_id = json['responseId']
		self._session = json['session']
		self._query_result = QueryResult(json['queryResult'])

	@property
	def response_id(self):
		return self._response_id

	@property
	def session(self):
		return self._session

	@property
	def query_result(self):
		return self._query_result


class QueryResult:

	def __init__ (self, json):
		self._query_text = json['queryText']
		self._parameters = json.get('parameters', {})
		self._all_required_params_present = json['allRequiredParamsPresent']
		self._fulfillment_text = json.get('fulfillmentText', '')
		self._output_contexts = self._parse_contexts(json.get('outputContexts', []))
		self._intent = Intent(json['intent'])

	def _parse_contexts(self, json):
		contexts = {}
		for context_json in json:
			context = Context(context_json)
			contexts[context.display_name] = context
		return contexts

	@property
	def query_text(self):
		return self._query_text

	@property
	def parameters(self):
		return self._parameters
	
	@property
	def all_required_params_present(self):
		return self._all_required_params_present

	@property
	def fulfillment_text(self):
		return self._fulfillment_text
	
	@property
	def output_contexts(self):
		return self._output_contexts

	@property
	def intent(self):
		return self._intent


class Intent:

	def __init__(self, json):
		self._name = json['name']
		self._display_name = json['displayName']

	@property
	def name(self):
		return self._name

	@property
	def displayName(self):
		return self._display_name


class Context:

	def __init__(self, json):
		self._name = json['name']
		self._display_name = self._name.split('contexts/')[1]
		self._lifespan_count = json['lifespanCount']
		self._parameters = json.get('parameters', {})

	@property
	def name(self):
		return self._name
	
	@property
	def display_name(self):
		return self._display_name

	@property
	def lifespan_count(self):
		return self._lifespan_count
	
	@property
	def parameters(self):
		return self._parameters
	
		
		

	