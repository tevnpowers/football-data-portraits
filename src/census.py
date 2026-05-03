from utils import load_state_census_data, write_census_csv

# Path to folder for output data files
CENSUS_DIRECTORY = 'census/'
CENSUS_OUTPUT_FILE = f'{CENSUS_DIRECTORY}census.csv'
INPUT_FILE_2010_2019 = f'{CENSUS_DIRECTORY}nst-est2019-01.csv'
INPUT_FILE_2020_2025 = f'{CENSUS_DIRECTORY}NST-EST2025-ALLDATA.csv'

if __name__ == '__main__':
	print('Script beginning...')
	populations = load_state_census_data((INPUT_FILE_2010_2019,INPUT_FILE_2020_2025))
	write_census_csv(CENSUS_OUTPUT_FILE, populations)