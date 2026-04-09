#!/Users/tevnpowers/miniconda3/envs/sports-analysis/bin/python3
# Selenium base tutorial: https://www.zenrows.com/blog/selenium-cloudflare-bypass#seleniumbase
import time
from datetime import datetime
from typing import Dict
from seleniumbase import Driver
from seleniumbase.core import sb_driver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from player import Player

# seconds to sleep between API calls
API_RATE_LIMIT = 10
UC_RECONNECT_TIME = 10

# HTML element ID tags
META_INFO_BUTTON_ID = 'meta_more_button'
BIRTH_INFO_ID = 'necro-birth'

FIRST_PLAYER_ROW = 2

# Column indices for player table properties
NAME_IDX = 2
POSITION_IDX = 3
DRAFT_PICK_IDX = 0
DRAFT_TEAM_IDX = 1
COLLEGE_INDEX = 26

draft_year = 2025

nfl_players: Dict[Player, Player] = {}
colleges = {}
high_schools = {}

def api_sleep(seconds: int) -> None:
	# print(f'Sleeping for {seconds} seconds for API rate limit...')
	time.sleep(seconds)

def add_players_from_draft(year: int, driver: sb_driver.DriverMethods) -> None:
	print(f'Opening {year} draft url...')

	# set the target URL based on the year
	url = f'https://www.pro-football-reference.com/years/{year}/draft.htm'

	# open URL using UC mode with 6 second reconnect time to bypass initial detection
	driver.uc_open_with_reconnect(url, reconnect_time=UC_RECONNECT_TIME)

	print(f'Loaded page: {driver.title}')
	assert 'NFL Draft Listing' in driver.title

	# attempt to click the CAPTCHA checkbox if present
	driver.uc_gui_click_captcha()

	table = driver.find_element('id', 'drafts')

	rows = table.find_elements('tag name', 'tr') # get all of the rows in the table
	player_count = 0
	for i in range(FIRST_PLAYER_ROW, len(rows)):
		row = rows[i]
		# print(row.text)

		th_cols = row.find_elements('tag name', 'th')
		td_cols = row.find_elements('tag name', 'td')

		# rows with all <th> elements, and no <td> elements are
		# header rows that we don't need to process for player info
		if not td_cols:
			continue

		draft_round = 0
		if th_cols:
			draft_round = int(th_cols[0].text)

		url = ''
		href = td_cols[NAME_IDX].find_element('tag name', 'a')
		if href:
			url = href.get_attribute('href')

		player = Player(
			td_cols[NAME_IDX].text,
			td_cols[POSITION_IDX].text,
			draft_year,
			draft_round,
			int(td_cols[DRAFT_PICK_IDX].text),
			td_cols[DRAFT_TEAM_IDX].text,
			[td_cols[DRAFT_TEAM_IDX].text],
			url
		)

		nfl_players[player] = player
		player_count += 1

	print(f'Found {player_count} players from {year} draft.')

def update_player_info(player: Player, driver: sb_driver.DriverMethods) -> Player:
	if player in nfl_players:
		if nfl_players[player].url:
			print(f'Opening player profile for {nfl_players[player].name} ({nfl_players[player].position})...')
			driver.uc_open_with_reconnect(nfl_players[player].url, reconnect_time=UC_RECONNECT_TIME)

			# Check if the "More bio info" button is present on the player profile page
			meta_buttons = driver.find_elements('id', META_INFO_BUTTON_ID)
			
			# If the button is present, we need to click it to reveal the player bio info
			if meta_buttons:
				# The ID should be unique, so we assert the length should be 1
				assert len(meta_buttons) == 1

				print('Expanding player bio information...')
				# Click the button to reveal the info we want
				meta_buttons[0].click()

			# Check for the span that contains birthday and birth place info
			birth_info = driver.find_elements('id', BIRTH_INFO_ID)
			if birth_info:
				# The ID should be unique, so we assert the length should be 1
				assert len(birth_info) == 1

				print(f'Birth info: {birth_info[0].text}')

				# Birthday is stored on the data-birth property in YYYY-MM-DD format
				data_birth = birth_info[0].get_attribute('data-birth')
				if data_birth:
					player.birthday = datetime.strptime(data_birth, '%Y-%m-%d')
					# print(f'{player.name}\'s birthday: {player.birthday.strftime('%m-%d-%Y')}')

				# Location info, if present, will be stored in an inner <span> element
				birth_place = birth_info[0].find_element('tag name', 'span')
				# print(f'Birth place: {birth_place.text}')
				if birth_place.text:
					# state
					state_link = birth_place.find_elements('tag name', 'a')
					if state_link:
						player.birth_state = state_link[0].text

						# city
						player.birth_city = birth_place.text[3:(-2 - len(player.birth_state))]
						# print(f'Player birth info: {player.birth_city} ({player.birth_state})')
					else:
						# state or country if we get here
						player.birth_state = birth_place.text[3:]
						# print(f'Player birth info: ({player.birth_state})')
		else:
			print(f'No profile url found for: {nfl_players[player].name} ({nfl_players[player].position})')
	else:
		print(f'Player not found in dictionary: {player}')
	return player

if __name__ == '__main__':
	print('Script beginning...')

	# initialize the driver in GUI mode with UC enabled
	driver = Driver(uc=True, headless=False)

	# Setup wait for later
	# wait = WebDriverWait(driver, 10)

	# Check we don't have other windows open already
	assert len(driver.window_handles) == 1

	# Add players from 2025 draft
	add_players_from_draft(2025, driver)

	# sleep for 10 seconds before making any other API calls
	api_sleep(API_RATE_LIMIT)


	for key in nfl_players.keys():
		nfl_players[key] = update_player_info(key, driver)
		print(f'Updated player: {nfl_players[key]}')
		api_sleep(API_RATE_LIMIT)

	# close the browser and end the session
	driver.quit()
