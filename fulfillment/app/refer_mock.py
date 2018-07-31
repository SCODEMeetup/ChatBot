import sqlite3
from random import randint
from datetime import datetime, timedelta

class ReferMock:

	def __init__(self, db_file):
		self._database = sqlite3.connect(db_file);
		self._database.row_factory = sqlite3.Row

	def search_for_user(self, ssn, birthdate):
		sql = "SELECT firstName, lastName, address, id FROM User WHERE ssn=? AND birthdate=?"
		result = self._query_db(sql, [ssn, birthdate], one=True)
		return result

	def get_available_appointment_for_pantry(self, pantry):
		availableTimeHour = randint(10, 17)
		tomorrow = datetime.now() + timedelta(days=1)
		appointmentTime = tomorrow.replace(hour=availableTimeHour, minute=0, second=0)
		return {'pantry': pantry, 'date_and_time': appointmentTime}


	def _query_db(self, query, args=(), one=False):
		cursor = self._database.execute(query, args)
		results = cursor.fetchall()
		return (results[0] if results else None) if one else results