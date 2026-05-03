import csv
from pathlib import Path
from typing import Dict, Tuple

from player import Player
from school import School

# Census 2010-2019 csv column indices
CENSUS_STATE_IDX = 0
CENSUS_2010_POP_IDX = 3
CENSUS_2011_POP_IDX = 4
CENSUS_2012_POP_IDX = 5
CENSUS_2013_POP_IDX = 6
CENSUS_2014_POP_IDX = 7
CENSUS_2015_POP_IDX = 8
CENSUS_2016_POP_IDX = 9
CENSUS_2017_POP_IDX = 10
CENSUS_2018_POP_IDX = 11
CENSUS_2019_POP_IDX = 12

# Census 2020-2025 csv headers
CENSUS_STATE_NAME = 'NAME'
CENSUS_2020_POP = 'POPESTIMATE2020'
CENSUS_2021_POP = 'POPESTIMATE2021'
CENSUS_2022_POP = 'POPESTIMATE2022'
CENSUS_2023_POP = 'POPESTIMATE2023'
CENSUS_2024_POP = 'POPESTIMATE2024'
CENSUS_2025_POP = 'POPESTIMATE2025'

years_to_csv_columns = {
	2025: CENSUS_2025_POP,
	2024: CENSUS_2024_POP,
	2023: CENSUS_2023_POP,
	2022: CENSUS_2022_POP,
	2021: CENSUS_2021_POP,
	2020: CENSUS_2020_POP,
}

years_to_csv_index = {
	2019: CENSUS_2019_POP_IDX,
	2018: CENSUS_2018_POP_IDX,
	2017: CENSUS_2017_POP_IDX,
	2016: CENSUS_2016_POP_IDX,
	2015: CENSUS_2015_POP_IDX,
	2014: CENSUS_2014_POP_IDX,
	2013: CENSUS_2013_POP_IDX,
	2012: CENSUS_2012_POP_IDX,
	2011: CENSUS_2011_POP_IDX,
	2010: CENSUS_2010_POP_IDX
}

states_to_abbrev = { 
	'Alabama': 'AL',
	'Alaska': 'AK',
	'Arizona': 'AZ',
	'Arkansas': 'AR',
	'California': 'CA',
	'Colorado': 'CO',
	'Connecticut': 'CT',
	'Delaware': 'DE',
	'District of Columbia': 'DC',
	'Florida': 'FL',
	'Georgia': 'GA',
	'Hawaii': 'HI',
	'Idaho': 'ID',
	'Illinois': 'IL',
	'Indiana': 'IN',
	'Iowa': 'IA',
	'Kansas': 'KS',
	'Kentucky': 'KY',
	'Louisiana': 'LA',
	'Maine': 'ME',
	'Maryland': 'MD',
	'Massachusetts': 'MA',
	'Michigan': 'MI',
	'Minnesota': 'MN',
	'Mississippi': 'MS',
	'Missouri': 'MO',
	'Montana': 'MT',
	'Nebraska': 'NE',
	'Nevada': 'NV',
	'New Hampshire': 'NH',
	'New Jersey': 'NJ',
	'New Mexico': 'NM',
	'New York': 'NY',
	'North Carolina': 'NC',
	'North Dakota': 'ND',
	'Ohio': 'OH',
	'Oklahoma': 'OK',
	'Oregon': 'OR',
	'Pennsylvania': 'PA',
	'Rhode Island': 'RI',
	'South Carolina': 'SC',
	'South Dakota': 'SD',
	'Tennessee': 'TN',
	'Texas': 'TX',
	'Utah': 'UT',
	'Vermont': 'VT',
	'Virginia': 'VA',
	'Washington': 'WA',
	'West Virginia': 'WV',
	'Wisconsin': 'WI',
	'Wyoming': 'WY'
}

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


def load_state_census_data(filenames: Tuple[str, str]) -> Dict[int, Dict[str, int]]:
	'''Load state census data from 2010-2025'''
	# Initialize population dictionary
	populations = {}
	for year in range(2010,2026):
		populations[year] = {}

	# Census data 2010-2019
	census_range_a = range(2010,2020)
	with open(filenames[0], newline='') as csvfile:
		reader = csv.reader(csvfile)

		for row in reader:
			if row[CENSUS_STATE_IDX][1:] in states_to_abbrev:
				abbrev = states_to_abbrev[row[CENSUS_STATE_IDX][1:]]
				for year in census_range_a:
					populations[year][abbrev] = int(row[years_to_csv_index[year]].replace(',',''))

	# Census data 2020-2025
	census_range_b = range(2020,2026)
	with open(filenames[1], newline='') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			state = row[CENSUS_STATE_NAME]

			if state in states_to_abbrev:
				for year in census_range_b:
					populations[year][states_to_abbrev[state]] = int(row[years_to_csv_columns[year]])

	return populations

def write_census_csv(filename: str, populations: Dict[int, Dict[str, int]]):
	years = range(2010,2026)
	with open(filename, 'w', newline='') as csvfile:
		fieldnames = ['state'] + list(years)
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		writer.writeheader()

		for state in states_to_abbrev.values():
			row = {
				'state': state,
			}
			for year in years:
				row[year] = populations[year][state]
			
			writer.writerow(row)