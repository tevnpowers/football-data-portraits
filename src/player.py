import ast
import datetime
import uuid
from typing import Dict

# Property strings
ID = 'id'
NAME = 'name'
BIRTHDAY = 'birthday'
BIRTH_CITY = 'birth city'
BIRTH_STATE = 'birth state'
POSITION = 'position'
DRAFT_YEAR = 'draft year'
DRAFT_ROUND = 'draft round'
DRAFT_PICK = 'draft pick'
DRAFT_TEAM = 'draft team'
TEAMS = 'teams'
COLLEGES = 'colleges'
HIGH_SCHOOLS = 'high schools'
URL = 'url'
LEAGUE = 'league'

class Player:
	'''Information about an NFL player'''
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
	teams: list[uuid.UUID]
	colleges: list[uuid.UUID]
	high_schools: list[uuid.UUID]
	url: str
	league: str

	def __init__(self, id: uuid.UUID, name: str, position: str, year: int, round: int, pick: int, team: str, url: str = ''):
		self.id = id
		self.name = name
		self.position = position
		self.draft_year = year
		self.draft_round = round
		self.draft_pick = pick
		self.draft_team = team
		self.url = url
		self.birthday = ''
		self.birth_city = ''
		self.birth_state = ''
		self.league = ''
		self.teams = []
		self.colleges = []
		self.high_schools = []


	def add_team(self, team):
		self.teams.append(team)

	def add_college(self, school: uuid.UUID):
		self.colleges.append(school)

	def add_high_school(self, school: uuid.UUID):
		self.high_schools.append(school)

	def set_birth_location(self, city: str, state: str):
		self.birth_city = city
		self.birth_state = state

	def get_readable_birthday(self) -> str:
		return  self.birthday.strftime('%m-%d-%Y') if self.birthday else ''
	
	def to_dict(self) -> Dict[str, str]:
		return {
			ID: str(self.id),
			NAME: self.name,
			BIRTHDAY: self.get_readable_birthday(),
			BIRTH_CITY: self.birth_city,
			BIRTH_STATE: self.birth_state,
			POSITION: self.position,
			DRAFT_YEAR: self.draft_year,
			DRAFT_ROUND: self.draft_round,
			DRAFT_PICK: self.draft_pick,
			DRAFT_TEAM: self.draft_team,
			TEAMS: [str(id) for id in self.teams],
			COLLEGES: [str(id) for id in self.colleges],
			HIGH_SCHOOLS: [str(id) for id in self.high_schools],
			URL: self.url,
			LEAGUE: self.league
		}

	@staticmethod
	def from_dict(properties: Dict[str, str]) -> 'Player':
		player = Player(
			uuid.UUID(properties[ID]),
			properties[NAME],
			properties[POSITION],
			properties[DRAFT_YEAR],
			properties[DRAFT_ROUND],
			properties[DRAFT_PICK],
			properties[DRAFT_TEAM],
			properties[URL]
		)

		player.birthday = datetime.strptime(properties[BIRTHDAY], '%m-%d-%Y') if properties[BIRTHDAY] else ''
		player.birth_city = properties[BIRTH_CITY]
		player.birth_state = properties[BIRTH_STATE]
		player.teams = [uuid.UUID(id) for id in ast.literal_eval(properties[TEAMS])]
		player.colleges = [uuid.UUID(id) for id in ast.literal_eval(properties[COLLEGES])]
		player.high_schools = [uuid.UUID(id) for id in ast.literal_eval(properties[HIGH_SCHOOLS])]
		player.league = properties[LEAGUE]
		return player

	@staticmethod
	def get_csv_columns() -> list[str]:
		return [
			ID,
			NAME,
			BIRTHDAY,
			BIRTH_CITY,
			BIRTH_STATE,
			POSITION,
			DRAFT_YEAR,
			DRAFT_ROUND,
			DRAFT_PICK,
			DRAFT_TEAM,
			TEAMS,
			COLLEGES,
			HIGH_SCHOOLS,
			URL,
			LEAGUE
		]

	def __hash__(self):
		return hash(self.id)

	def __repr__(self):
		return f'Player(name="{self.name}", team={self.draft_team}, position={self.position}, pick="{self.draft_year} {self.draft_round}.{self.draft_pick}")'