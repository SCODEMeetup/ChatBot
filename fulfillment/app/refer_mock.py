import sqlite3

class ReferMock:

	def __init__(self, db_file):
		self._database = sqlite3.connect(db_file);
		self._database.row_factory = sqlite3.Row

	def search_for_user(self, ssn, birthdate):
		print("in search")
		print(ssn)
		print(birthdate)
		sql = "SELECT firstName, lastName, address, clientId FROM User WHERE ssn=? AND birthdate=?"
		result = self._query_db(sql, [ssn, birthdate], one=True)
		return result

	def _query_db(self, query, args=(), one=False):
		cursor = self._database.execute(query, args)
		results = cursor.fetchall()
		return (results[0] if results else None) if one else results