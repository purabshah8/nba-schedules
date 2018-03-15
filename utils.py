import geopy, requests, csv
from bs4 import BeautifulSoup
import pandas as pd
from geopy.distance import vincenty



teams = {'Atlanta Hawks': 'Philips Arena', 'Boston Celtics': 'TD Garden', 'Brooklyn Nets': 'Barclays Center',
         'Charlotte Hornets': 'Spectrum Center', 'Chicago Bulls': 'United Center, Chicago',
         'Cleveland Cavaliers': 'Quicken Loans Arena', 'Dallas Mavericks': 'American Airlines Center',
         'Denver Nuggets': 'Pepsi Center', 'Detroit Pistons': 'Little Caesars Arena',
         'Golden State Warriors': 'Oracle Arena', 'Houston Rockets': 'Toyota Center',
         'Indiana Pacers' : 'Bankers Life Fieldhouse', 'Los Angeles Clippers': 'Staples Center',
         'Los Angeles Lakers': 'Staples Center', 'Memphis Grizzlies': 'FedExForum',
         'Miami Heat': 'AmericanAirlines Arena', 'Milwaukee Bucks': 'BMO Harris Bradley Center',
         'Minnesota Timberwolves' : 'Target Center', 'New Orleans Pelicans': 'Smoothie King Center',
         'New York Knicks' : 'Madison Square Garden', 'Oklahoma City Thunder': 'Chesapeake Energy Arena',
         'Orlando Magic': 'Amway Center', 'Philadelphia 76ers': 'Wells Fargo Center',
         'Phoenix Suns': 'Talking Stick Resort Arena', 'Portland Trail Blazers': 'Moda Center',
         'Sacramento Kings': 'Golden 1 Center', 'San Antonio Spurs': 'AT&T Center',
         'Toronto Raptors': 'Air Canada Centre', 'Utah Jazz': 'Vivint Smart Home Arena',
         'Washington Wizards': 'Capital One Arena'}

arenas = {'Philips Arena': (), 'TD Garden': (), 'Barclays Center': (), 'Spectrum Center': (),
          'United Center, Chicago': (), 'Quicken Loans Arena': (), 'American Airlines Center': (), 'Pepsi Center': (),
          'Little Caesars Arena': (), 'Oracle Arena': (), 'Toyota Center': (), 'Bankers Life Fieldhouse': (),
          'Staples Center': (), 'FedExForum': (), 'AmericanAirlines Arena': (), 'BMO Harris Bradley Center': (),
          'Target Center': (), 'Smoothie King Center': (), 'Madison Square Garden': (), 'Chesapeake Energy Arena': (),
          'Amway Center': (), 'Wells Fargo Center': (), 'Talking Stick Resort Arena' : (), 'Moda Center': (),
          'Golden 1 Center': (), 'AT&T Center': (), 'Air Canada Centre': (), 'Vivint Smart Home Arena': (),
          'Capital One Arena': ()}

def locate_arenas():
    """ Locates NBA arenas and saves them to dictionary """
    for arena in arenas:
        geolocation = geopy.geocoders.Nominatim()
        arena_loc = geolocation.geocode(arena)
        arenas[arena] = (arena_loc.latitude,arena_loc.longitude)

def get_schedule(year):
    """Creates a csv of the NBA schedule in given year
        type(year) = string
    """
    months = ['october', 'november', 'december', 'january', 'february', 'march', 'april']
    game_info = []
    print('Retrieving schedule for {0}-{1}'.format(int(year) - 1, year[-2:]))
    for month in months:
        response = requests.get('https://www.basketball-reference.com/leagues/NBA_{0}_games-{1}.html'.format(year,month))
        schedule_soup = BeautifulSoup(response.text, 'lxml')
        rows = schedule_soup.find_all('tr')
        rows = rows[1:]
        for item in rows:
            if item.text == 'Playoffs':
                break       # stop before playoff games
            date = item.find('a')
            right = item.find_all('td',{'class':'right'})
            left = item.find_all('td',{'class':'left'})
            game_info.append([date.text + ' ' + right[0].text, left[0].text, left[1].text])
        print('Added games from ' + month.capitalize())
    game_info.insert(0, ['DateTime', 'Away', 'Home'])
    with open("nba_schedules/{0}_Schedule.csv".format(year), "w") as f:
        writer = csv.writer(f)
        writer.writerows(game_info)
    print('Finshed scraping {0}-{1} NBA schedule. Saved to nba_schedules/{2}_Schedule.csv'.format(int(year) - 1, year[-2:], year))

def team_travel(list_teams, nba_schedule):
    """Returns a list of travel amounts for each game for all teams inputted.
    type(list_teams) = dict
    type(nba_schedule) = pd.DataFrame
    """
    travel_amts = {}
    for team in list_teams:
        distance = 0
        prev_gps = arenas[teams[team]]
        game_locations = nba_schedule.loc[(nba_schedule.Home == team) | (nba_schedule.Away == team), ['Arena']]
        for loc in game_locations['Arena']:
            game_gps = arenas[loc]
            distance += vincenty(prev_gps, game_gps).miles
        travel_amts[team] = distance
    return pd.Series(travel_amts)
