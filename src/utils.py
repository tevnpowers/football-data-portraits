import csv
from pathlib import Path

from player import Player
from school import School


def load_downloaded_players(filename: str) -> list[Player]:
	'''Load NFL players from csv file'''
	# Check if the file exists
	if Path(filename).is_file():
		# List of drafted NFL players in the csv file
		players: list[Player] = []

		# Read the file row by row, deserializing
		# each player's information into a Player object
		# Append each Player to the list above.
		with open(filename, 'r') as player_file:
			reader = csv.DictReader(player_file)
			for row in reader:
				players.append(Player.from_dict(row))

		return players
	
	# If no file exists, we have no players to load
	return []

def load_downloaded_schools(filename: str) -> list[School]:
	'''Load schools from a csv file'''
	# Check if the file exists
	if Path(filename).is_file():
		# List of schools attended by drafted NFL players
		schools: list[School] = []

		# Read the file row by row, deserializing
		# each school's information into a School object
		# Append each School to the list above.
		with open(filename, 'r') as school_file:
			reader = csv.DictReader(school_file)
			for row in reader:
				schools.append(School.from_dict(row))

		return schools

	# If no file exists, we have no schools to load
	return []
