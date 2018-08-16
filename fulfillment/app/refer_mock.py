import sqlite3
from random import randint
from datetime import datetime, timedelta

class ReferMock:

	def __init__(self, db_file):
		self._database = sqlite3.connect(db_file);
		self._database.row_factory = sqlite3.Row

	def get_all_appointments(self):
		sql = "SELECT User.firstName, User.lastName, Pantry.name, Appointment.dateAndTime FROM Appointment INNER JOIN User ON Appointment.userId=User.Id INNER JOIN Pantry ON Appointment.pantryId=Pantry.Id"
		return self._query_db(sql)

	def get_all_users(self):
		sql = "SELECT firstName, lastName, ssn, birthdate, address FROM User"
		return self._query_db(sql)

	def search_for_user(self, ssn, birthdate):
		sql = "SELECT firstName, lastName, address, id FROM User WHERE ssn=? AND birthdate=?"
		return self._query_db(sql, [ssn, birthdate], one=True)

	def search_for_appointment(self, user_id):
		sql = "SELECT MAX(dateAndTime), Pantry.name, Pantry.notes FROM Appointment INNER JOIN Pantry ON Appointment.pantryId=Pantry.Id WHERE userId=? and dateAndTime > datetime('now')"
		result = self._query_db(sql, [user_id], one=True)

		if result == None or result['MAX(dateAndTime)'] == None:
			return None
		else:
			return {'date_and_time': result['MAX(dateAndTime)'],
					'pantry': result['name'],
					'notes': result['notes']}

	def cancel_appointment(self, user_id):
		sql = "SELECT Appointment.id, MAX(dateAndTime), Pantry.name FROM Appointment INNER JOIN Pantry ON Appointment.pantryId=Pantry.Id WHERE userId=? and dateAndTime > datetime('now')"
		result = self._query_db(sql, [user_id], one=True)

		if result == None or result['MAX(dateAndTime)'] == None:
			return None
		else:
			sql = "DELETE FROM Appointment WHERE id=?"
			self._insert_update_delete_db(sql, [result['id']])

			return {'date_and_time': result['MAX(dateAndTime)'],
					'pantry': result['name']}

	def update_name(self, first_name, last_name, user_id):
		print(first_name)
		print(last_name)
		sql = "UPDATE User SET firstName=?, lastName=? WHERE id=?"
		self._insert_update_delete_db(sql, [first_name, last_name, user_id])

	def update_address(self, address, user_id):
		sql = "UPDATE User SET address=? WHERE id=?"
		self._insert_update_delete_db(sql, [address, user_id])

	def suggest_pantries_available_asap(self):
		sql = "SELECT id FROM Pantry"
		result = self._query_db(sql)
		pantry_ids = []
		for row in result:
			pantry_ids.append(row['id'])

		while len(pantry_ids) > 3:
			del pantry_ids[randint(0, len(pantry_ids) - 1)]

		sql = "SELECT name FROM Pantry WHERE id IN (%s)" % ','.join('?'*len(pantry_ids))
		result = self._query_db(sql, pantry_ids)

		appointments = []
		tomorrow = datetime.now() + timedelta(days=1)
		for row in result:
			availableTimeHour = randint(10, 17)
			appointmentTime = tomorrow.replace(hour=availableTimeHour, minute=0, second=0, microsecond=0)
			appointments.append({'pantry': row['name'], 'date_and_time': appointmentTime})

		return appointments

	def suggest_pantries_available_wait(self):
		return self.suggest_pantries_available_asap()

	def get_available_appointment_for_pantry(self, pantry):
		availableTimeHour = randint(10, 17)
		tomorrow = datetime.now() + timedelta(days=1)
		appointmentTime = tomorrow.replace(hour=availableTimeHour, minute=0, second=0, microsecond=0)
		return {'pantry': pantry, 'date_and_time': appointmentTime}

	def book_appointment(self, user_id, pantry, appointment_date_time):
		sql = "INSERT INTO Appointment (userId, pantryId, dateAndTime) VALUES (?, (SELECT id FROM Pantry WHERE Name=?), ?)"
		try:
			self._insert_update_delete_db(sql, [user_id, pantry, appointment_date_time]);
		except sqlite3.Error:
			return None
		
		sql = "SELECT notes, address FROM Pantry WHERE name=?"
		return self._query_db(sql, [pantry], one=True)

	def _query_db(self, query, args=(), one=False):
		cursor = self._database.execute(query, args)
		results = cursor.fetchall()
		cursor.close()
		return (results[0] if results else None) if one else results

	def _insert_update_delete_db(self, query, args=()):
		cursor = self._database.cursor()
		cursor.execute(query, args)
		self._database.commit()
		cursor.close()