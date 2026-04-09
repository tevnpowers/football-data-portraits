import datetime
import uuid

class Player:
	'''An NFL player'''
	id: uuid.UUID
	name: str
	birthday: datetime.date
	birth_city: str
	birth_state: str
	position: str
	draft_year: int
	draft_round: int
	draft_pick: int
	draft_team: str
	teams: list[int]
	colleges: list[int]
	high_schools: list[int]
	url: str

	def __init__(self, name: str, position: str, year: int, round: int, pick: int, team: str, teams: list[int], url: str = ''):
		self._id = uuid.uuid4()
		self.name = name
		self.position = position
		self.draft_year = year
		self.draft_round = round
		self.draft_pick = pick
		self.draft_team = team
		self.teams = teams
		self.url = url
		self.colleges = []
		self.high_schools = []

	def add_team(self, team):
		self.teams.append(team)

	def add_college(self, school: int):
		self.colleges.append(school)

	def add_high_school(self, school: int):
		self.high_schools.append(school)

	def set_birthday(self, date: datetime.date):
		self.birthday = date

	def set_birth_location(self, city: str, state: str):
		self.birth_city = city
		self.birth_state = state

	def __hash__(self):
		return hash(self._id)
	
	def __repr__(self):
		return f'Player(name="{self.name}", team={self.draft_team}, position={self.position}, pick="{self.draft_year} {self.draft_round}.{self.draft_pick}")'