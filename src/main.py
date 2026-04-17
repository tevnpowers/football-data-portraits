# Selenium base tutorial: https://www.zenrows.com/blog/selenium-cloudflare-bypass#seleniumbase

# built-in libraries
import csv
import time
import uuid
from datetime import datetime
from typing import Dict

# installed libraries
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn, TimeElapsedColumn, MofNCompleteColumn, TimeRemainingColumn
from seleniumbase import Driver
from seleniumbase.core import sb_driver

# project modules
from player import Player
from school import School, SchoolLevel

# seconds to sleep between API calls
API_RATE_LIMIT = 10

# Seconds to disconnect chrome driver
# to prevent bot detection
UC_RECONNECT_TIME = 10

# HTML element ID tags
META_INFO_BUTTON_ID = 'meta_more_button'
BIRTH_INFO_ID = 'necro-birth'
METADATA_ID = 'meta'

# HTML element class names
NO_THUMB_CLASS = 'nothumb'

# Prefixes on relative links to college and high school profiles
SITE_URL = 'https://www.pro-football-reference.com'
COLLEGE_URL_PREFIX = '/schools'
HS_URL_PREFIX = '/schools/high_schools.cgi?id'

# NFL Draft year range
FIRST_DRAFT_YEAR = 1937
LAST_DRAFT_YEAR = 2025

# First row in draft table with player info
FIRST_PLAYER_ROW = 2

# Column indices for player properties in draft table
NAME_IDX = 2
POSITION_IDX = 3
DRAFT_PICK_IDX = 0
DRAFT_TEAM_IDX = 1
COLLEGE_INDEX = 26

# Path to folder for output data files
OUTPUT_DIRECTORY = 'output/'

def rate_limit_api_calls(seconds: int) -> None:
	time.sleep(seconds)

def get_draft_links(driver: sb_driver.DriverMethods, progress: Progress = None) -> list[tuple]:
	if progress:
		progress.console.print(f'Getting all NFL/AFL draft history...')

	url = 'https://www.pro-football-reference.com/draft/'
	driver.uc_open_with_reconnect(url, reconnect_time=UC_RECONNECT_TIME)

	if progress:
		progress.console.print(f'Loaded page: {driver.title}')

	# attempt to click the CAPTCHA checkbox if present
	driver.uc_gui_click_captcha()

	# Get the table of drafted players by element ID
	table = driver.find_element('id', 'draft_years')

	# Get all rows in the table by the <tr> html tag
	rows = table.find_elements('tag name', 'tr')

	draft_info = []

	# Skip the first row, which is a header for the table
	for i in range(1, len(rows)):
		row = rows[i]
		
		# The <td> HTML element defines cells in the row that contain player data
		td_cols = row.find_elements('tag name', 'td')

		# Skip rows that don't contain draft info
		if not td_cols:
			continue

		# The <th> (table header) HTML element in a row contains the draft year and url
		th_cols = row.find_elements('tag name', 'th')
		assert len(th_cols) == 1

		# Save draft info in a tuple, add it to the list
		draft_year = int(th_cols[0].text)
		draft_url = th_cols[0].find_element('tag name', 'a').get_attribute('href')
		league = td_cols[0].text

		draft_info.append((draft_year, league, draft_url))

	return draft_info

def get_drafted_players(url: str, year: int, driver: sb_driver.DriverMethods, progress: Progress = None) -> Dict[int, list[Player]]:
	'''Get basic info of players drafted to the NFL in the given year.

	Arguments:
	year -- the draft year
	driver -- driver for web browser
	progress -- context manager for progress bar

	Return value: dictionary where keys are draft rounds and values
	are the list of drafted players in the corresponding round.
	'''
	# Dictionary of players by round. Keys are draft rounds.
	# Values are lists of players drafted in that round.
	players: Dict[int, list[Player]] = {}

	if progress:
		progress.console.print(f'Opening {year} draft url: {url}')

	# open URL using UC mode with 6 second reconnect time to bypass initial detection
	driver.uc_open_with_reconnect(url, reconnect_time=UC_RECONNECT_TIME)

	if progress:
		progress.console.print(f'Loaded page: {driver.title}')

	assert 'NFL Draft Listing' in driver.title

	# attempt to click the CAPTCHA checkbox if present
	driver.uc_gui_click_captcha()

	# Get the table of drafted players by element ID
	table = driver.find_element('id', 'drafts')

	# Get all rows in the table by the <tr> html tag
	rows = table.find_elements('tag name', 'tr')

	# Loop through each row in the table that represents an NFL player.
	# Extract and store the basic info about each player row.
	player_count = 0
	for i in range(FIRST_PLAYER_ROW, len(rows)):
		row = rows[i]

		# The <td> HTML element defines cells in the row that contain player data
		td_cols = row.find_elements('tag name', 'td')

		# Skip rows that don't contain player info
		if not td_cols:
			continue

		# The <th> (table header) HTML elements in a row contains the player's draft round
		th_cols = row.find_elements('tag name', 'th')
		
		# TODO: Check if this always evaluates to true. What to do when it doesn't?
		draft_round = 0
		if th_cols:
			draft_round = int(th_cols[0].text)

		# On the website, a player's profile can be reached by clicking
		# their name in the table. Here we extract the url from this <a>
		# anchor element in the column with a player's name.
		url = ''
		href = td_cols[NAME_IDX].find_element('tag name', 'a')
		if href:
			url = href.get_attribute('href')

		# Initialize a Player object with the info available from the table
		player = Player(
			uuid.uuid4(),
			td_cols[NAME_IDX].text,
			td_cols[POSITION_IDX].text,
			year,
			draft_round,
			int(td_cols[DRAFT_PICK_IDX].text),
			td_cols[DRAFT_TEAM_IDX].text,
			url
		)

		# If this is the first player drafted in the current round
		# we need to initialize an empty list for players to be appended to.
		if player.draft_round not in players:
			players[player.draft_round] = []

		# Add the current player to the list associated with their round
		players[player.draft_round].append(player)
		player_count += 1

	if progress:
		progress.console.print(f'Found {player_count} players from {year} draft.')

	return players

def get_player_birth_info(player: Player, driver: sb_driver.DriverMethods) -> Player:
	# Check for the span that contains birthday and birth place info
	birth_info = driver.find_elements('id', BIRTH_INFO_ID)
	if birth_info:
		# The ID should be unique, so we assert the length should be 1
		assert len(birth_info) == 1

		# Birthday is stored on the data-birth property in YYYY-MM-DD format
		data_birth = birth_info[0].get_attribute('data-birth')
		if data_birth:
			player.birthday = datetime.strptime(data_birth, '%Y-%m-%d')

		# Location info, if present, will be stored in an inner <span> element
		birth_place = birth_info[0].find_element('tag name', 'span')
		if birth_place.text:
			# If the birth place span has an anchor element, then the
			# pattern appears to be that the text in that anchor is
			# a state abbreviation.
			state_link = birth_place.find_elements('tag name', 'a')
			if state_link:
				state = state_link[0].text
				
				# There is likely a city preceding the state.
				# The format is often: "in [CITY], [STATE]"
				# Slice the string to omit the word "in" and any characters
				# belonging to the text corresponding to the state.
				city = birth_place.text[3:(-2 - len(state))]
				player.set_birth_location(city, state)
			else:
				# If there is no anchor link present, then the text likely
				# references a country and does not include city info.
				player.set_birth_location('', birth_place.text[3:])
	return player

def get_player_school_data(player: Player, driver: sb_driver.DriverMethods) -> Player:
	# Identify metadata div, containing school information
	metadata = driver.find_elements('id', METADATA_ID)
	if metadata:
		# The ID should be unique, so we assert the length should be 1
		assert len(metadata) == 1
		metadata_divs = metadata[0].find_elements('tag name', 'div')

		for div in metadata_divs:
			# media-item divs contain a profile picture
			# The div with the text we want to extract
			# should be "nothumb" class or no class at all.
			class_name = div.get_attribute('class')
			if class_name != 'media-item':
				paragraphs = div.find_elements('tag name', 'p')

				for paragraph in paragraphs:
					if paragraph.text.startswith("College:"):
						college_links = paragraph.find_elements('tag name', 'a')

						for link in college_links:

							url = link.get_attribute('href')
							if url.startswith(SITE_URL + COLLEGE_URL_PREFIX):
								# If we haven't come across a school with this url,
								# add a new school to the dictionary.
								if url not in schools:
									schools[url] = School(
											uuid.uuid4(),
											link.text,
											SchoolLevel.College,
											url
										)

								# Add player to the school's list of players
								schools[url].add_player(player.id)

								# Add school to the player's list of colleges
								player.add_college(schools[url].id)
					elif paragraph.text.startswith("High School:"):
						# if url.startswith(SITE_URL + HS_URL_PREFIX)
						hs_links = paragraph.find_elements('tag name', 'a')
						for link in hs_links:
							url = link.get_attribute('href')

							if url.startswith(SITE_URL + HS_URL_PREFIX):
								# If we haven't come across a school with this url,
								# add a new school to the dictionary.
								if url not in schools:
									schools[url] = School(
											uuid.uuid4(),
											link.text,
											SchoolLevel.HighSchool,
											url
										)

								# Add player to the school's list of players
								schools[url].add_player(player.id)

								# Add school to the player's list of high schools
								player.add_high_school(schools[url].id)

	return player

def get_player_details(player: Player, driver: sb_driver.DriverMethods, progress: Progress = None) -> Player:
	'''Get bio info for and NFL player from their profile.

	Arguments:
	player -- a player object with basic info about a player
	driver -- driver for web browser
	progress -- context manager for progress bar

	Return value: An updated player object.
	'''
	# If the player has a url for a profile, we can scrape their
	# information from that web page.
	if player.url:
		if progress:
			progress.console.print(f'Opening player profile for {player.name} ({player.position})...')

		driver.uc_open_with_reconnect(player.url, reconnect_time=UC_RECONNECT_TIME)

		# Check if the "More bio info" button is present on the player profile page.
		meta_buttons = driver.find_elements('id', META_INFO_BUTTON_ID)
		
		# If the button is present, we need to click it to expand the player bio info.
		# Only visible content on the screen can be extracted.
		if meta_buttons:
			# The ID should be unique, so we assert the length should be 1
			assert len(meta_buttons) == 1

			if progress:
				progress.console.print('Expanding player bio information...')

			# Click the button to reveal the player info we want
			meta_buttons[0].click()

		# Update player with birth info
		player = get_player_birth_info(player, driver)

		# Update player with college and high school info
		player = get_player_school_data(player, driver)
	else:
		# If there is no URL associated with the player then there's no
		# additional info we can add.
		if progress:
			progress.console.print(f'No profile url found for: {player.name} ({player.position})')

	# Return the (potentially) updated Player
	return player

if __name__ == '__main__':
	print('Script beginning...')

	# initialize the driver in GUI mode with
	# UC (Undetected-Chromedriver Mode) mode on.
	# UC mode allows bots to appear humans.
	driver = Driver(uc=True, headless=False)

	# Check that we don't have other windows open already
	assert len(driver.window_handles) == 1

	# Configure columns for the progress bars in the terminal
	with Progress(SpinnerColumn(),
			TextColumn("[progress.description]{task.description}"),
			BarColumn(),
			TaskProgressColumn(),
			TimeRemainingColumn(),
			TimeElapsedColumn(),
			MofNCompleteColumn()) as progress:

		# Dictionary of schools attended by drafted players
		schools: Dict[str, School] = {}

		# CSV file that acts as a database of NFL players
		with open(f'{OUTPUT_DIRECTORY}players.csv', 'w', newline='') as players_csv:
			# Initialize csv dict writer and specify keys (column headers)
			writer = csv.DictWriter(players_csv, fieldnames=Player.get_csv_columns())
			writer.writeheader()

			# Dictionary of drafted NFL players
			nfl_players: Dict[Player, Player] = {}

			# Get links to all NFL/AFL drafts
			nfl_drafts = get_draft_links(driver, progress)

			# sleep before making any other API calls to respect the rate limit
			rate_limit_api_calls(API_RATE_LIMIT)

			# Progress bar associated with processing all NFL drafts
			task_nfl_drafts = progress.add_task(f'[green]Processing all NFL Drafts...', total=len(nfl_drafts))

			# For each draft year, get info associated with each player drafted
			for draft_info in nfl_drafts:
				draft_year, league, draft_url = draft_info

				# Get players from the current year's draft.
				# Key: draft round, Value: List of players drafted in the round
				drafted_players: Dict[int, list[Player]] = get_drafted_players(draft_url, draft_year, driver, progress)

				# Progress bar associated with each player in the current draft.
				total_players = [draftee for draftees in drafted_players.values() for draftee in draftees]
				task_total_players = progress.add_task(f'[red]Players in the {draft_year} draft...', total=len(total_players))

				# sleep before making any other API calls to respect the rate limit
				rate_limit_api_calls(API_RATE_LIMIT)

				# Iterate round by round through all players in the current year's draft
				# to check for more detailed info on their profile page.
				for round in sorted(drafted_players.keys()):
					# Progress bar associated with each player in the current draft and round.
					players_in_round_task = progress.add_task(f'[cyan]Players in Round {round} of {draft_year} draft...', total=len(drafted_players[round]))

					# Visit each player's pro-football reference profile for more details
					for player in drafted_players[round]:
						nfl_players[player] = get_player_details(player, driver, progress)
						nfl_players[player].league = league

						# Update progress bars, advancing them one player update
						progress.update(players_in_round_task, advance=1)
						progress.update(task_total_players, advance=1)

						# Create a row in our csv file for this player
						writer.writerow(nfl_players[player].to_dict())

						# sleep before making any other API calls to respect the rate limit
						rate_limit_api_calls(API_RATE_LIMIT)

				# Update progress bar, advancing one completed NFL draft
				progress.update(task_nfl_drafts, advance=1)

		# CSV file that acts as a database of schools
		with open(f'{OUTPUT_DIRECTORY}schools.csv', 'w', newline='') as schools_csv:
			# Initialize csv dict writer and specify keys (column headers)
			writer = csv.DictWriter(schools_csv, fieldnames=School.get_csv_columns())
			writer.writeheader()

			for key in schools:
				# Create a row in our csv file for this player
				writer.writerow(schools[key].to_dict())

	# close the browser and end the session
	driver.quit()
