import ast
import uuid
from enum import Enum
from typing import Dict

# Property strings
ID = 'id'
NAME = 'name'
CITY = 'city'
STATE = 'state'
LEVEL = 'level'
PLAYERS = 'players'
URL = 'url'

class SchoolLevel(Enum):
	HighSchool = 1
	College = 2

class School:
	id: uuid.UUID
	name: str
	city: str
	state: str
	level: SchoolLevel
	players: list[uuid.UUID]
	url: str

	def __init__(self, id: uuid.UUID, name: str, level: SchoolLevel, url: str, city: str = '', state: str = ''):
		self.id = id
		self.name = name
		self.level = level
		self.url = url

		self.city = city
		self.state = state

		self.players = []

	def add_player(self, id: uuid.UUID):
		self.players.append(id)

	def add_players(self, ids: list[uuid.UUID]):
		self.players += ids

	def to_dict(self) -> Dict[str, str]:
		return {
			ID: str(self.id),
			NAME: self.name,
			CITY: self.city,
			STATE: self.state,
			LEVEL: self.level.name,
			URL: self.url,
			PLAYERS: [str(id) for id in self.players]
		}

	@staticmethod
	def from_dict(properties: Dict[str, str]) -> 'School':
		school = School(uuid.UUID(properties[ID]), properties[NAME])
		school.city = properties[CITY]
		school.state = properties[STATE]
		school.level = SchoolLevel[properties[LEVEL]]
		school.url = properties[URL]
		school.players = [uuid.UUID(player_id) for player_id in ast.literal_eval(properties[PLAYERS])]
		return school
	
	@staticmethod
	def get_csv_columns() -> list[str]:
		return [
			ID,
			NAME,
			CITY,
			STATE,
			LEVEL,
			PLAYERS,
			URL
		]

	def __hash__(self):
		return hash(self.id)

	def __repr__(self):
		return f'School(name="{self.name}", level="{'college' if self.level == SchoolLevel.College else 'high school'}", players="{self.players}")'
