import requests
import pandas as pd
import re
from bs4 import BeautifulSoup
from time import sleep


def fetch(url):
    """
    Use BeautifulSoup to get the text of a web page.
    """
    r = requests.get(url)
    comm = re.compile("<!--|-->")
    soup = BeautifulSoup(comm.sub("", r.text), "html.parser")
    return soup


def get_team_page(season_page_url):
    """
    This function is to get the url's of all 30 MLB teams in a given year.
    """
    soup = fetch(season_page_url)
    url_list = []
    for item in soup.find_all('th',
                              {'scope':"row",
                               'class':"left ",
                               'data-stat':"team_name"}
                              ):
        if item.a:
            url = "https://www.baseball-reference.com" + item.a['href']
            title = item.text
            url_list.append((url, title))
    return list(set(url_list))


def get_game_page(team_page_url):
    """
    This function is to get all the url's of a single team's record
    in a given year.
    The input is a single team's season page.
    """
    soup = fetch(team_page_url)  # Call fetch()
    url_list = []
    for item in soup.find_all('span', {'class':"poptip"}):
        winTag = item.find(class_= "count win")
        lossTag = item.find(class_= "count notwin")
        tieTag = item.find(class_= "count unplayed")
        if winTag:
            url = "https://www.baseball-reference.com" + item.a['href']
            url_list.append(url)
        elif lossTag:
            url = "https://www.baseball-reference.com" + item.a['href']
            url_list.append(url)
        elif tieTag:
            url = "https://www.baseball-reference.com" + item.a['href']
            url_list.append(url)
    return url_list


def get_info(game_page_url, team_page_title):
    """
    This function is to get the raw html table regarding play-by-play
    given a box score page and the raw html table regarding targeted team's
    batting statsg.
    The input is a single game's page.
    """
    soup = fetch(game_page_url)
    target_table = soup.findAll('table', id="play_by_play")
    team_title_adj = team_page_title.replace(" ", "")\
                                    .replace(".", '') + 'batting'
    target_table_val = soup.findAll('table', id=team_title_adj)
    if target_table_val == [] and "Angels" in team_page_title:
        team_title_adj = team_page_title.replace(" ", "")\
                                        .replace(".", '') + 'ofAnaheimbatting'
        target_table_val = soup.findAll('table', id=team_title_adj)
    return target_table[0], target_table_val[0]


def html2pd(pbp_table):
    """
    This function is to convert a html play-by-play table to a pandas dataframe.
    The input is a single game's html play-by-play table.
    """
    column_flag = 1
    column_list = []
    pbp_list = []
    for row in pbp_table.find_all('tr'):
        # Get column names
        if column_flag == 1:
            for item in row.find_all('th'):
                column_list.append(item.text)
            column_flag = 0
        # Get row records
        else:
            row_list = []
            for item in row.find_all('th'):
                row_list.append(item.text)
            for item in row.find_all('td'):
                row_list.append(item.text)
            pbp_list.append(row_list)
    # Create pandas dataframe
    pbp_df = pd.DataFrame(columns=column_list)
    pbp_list_adj = [row for row in pbp_list if len(row) == len(column_list)]
    for i in range(len(pbp_list_adj)):
        pbp_df.loc[i] = pbp_list_adj[i]
    return pbp_df


def get_val_pa(pa_table):
    """
    This function is to get the actual plate appearances for a team in a game.
    The input is a single game's html batting table.
    """
    team_row_list = []
    for row in pa_table.find_all('tr'):
        for item in row.find_all('th'):
            # Find row that contains team total stats
            if item.text == 'Team Totals':
                for item in row.find_all('td'):
                    team_row_list.append(item.text)
    # index 6 is the total plate appearance for a team in a game
    return int(team_row_list[6])


def get_pa(game_page_url, team, team_page_title):
    """
    This function is to get the desired info from the play-by-play table.
    The input is a single game's page and a team's name.
    """
    pbp_table, pa_table = get_info(game_page_url, team_page_title)  # Get HTML
    pbp_df = html2pd(pbp_table)  # Convert HTML to pandas df
    team_actual_pa = get_val_pa(pa_table)  # Get a team's actual PA
    team_df = pbp_df[pbp_df["@Bat"] == team]  # Only focus on the desired team
    # Following chunk tries to eliminate non-plate-appearance actions
    batter_list = list(team_df.Batter)
    pa_list = []
    for i in range(len(batter_list)):
        if i == 0:
            pa_list.append(1)
        else:
            if batter_list[i] != batter_list[i - 1]:
                pa_list.append(1)
            else:
                pa_list[i - 1] = 0
                pa_list.append(1)
    team_df["PA"] = pa_list  # Add column PA to df
    # Filter out non-PA-related actions
    team_df_PA = team_df[team_df["PA"] == 1].reset_index()\
                                            .drop("index", axis=1)
    # Filter out extreme cases
    # Check if the last play of each inning is incurred by the runner on bases
    for i in range(len(team_df_PA)):
        p_des = team_df_PA.loc[i]['Play Description'].lower()
        if team_df_PA.loc[i].Out == '2':
            # steal and then out: (DET)
            # baseball-reference.com/boxes/OAK/OAK201808030.shtml
            if 'picked off' in p_des or 'caught stealing' in p_des \
                    or 'baserunner out advancing' in p_des \
                    or 'passed ball' in p_des \
                    or ('steals' in p_des and 'out' in p_des):
                # Extreme case in one of the Mets game
                # baseball-reference.com/boxes/MIA/MIA201807010.shtml
                # Ultimate extreme case: (Neil Walker)
                # baseball-reference.com/boxes/PIT/PIT201207210.shtml
                if 'walk' not in p_des.replace('walker', '') \
                        and 'strikeout' not in p_des:
                    team_df_PA.loc[i] = 0
        # wild pitch: (OAK)
        # baseball-reference.com/boxes/NYA/NYA201805120.shtml
        # caught stealing double play: (PHI)
        # baseball-reference.com/boxes/PHI/PHI201804200.shtml
        # balk: (SEA)
        # baseball-reference.com/boxes/SEA/SEA201808180.shtml
        if ('wild pitch' in p_des and 'walk' not in p_des
                and 'strikeout' not in p_des) \
                or ('picked off' in p_des and 'walk' not in p_des
                     and 'strikeout' not in p_des) \
                or ('passed ball' in p_des and 'walk' not in p_des
                     and 'strikeout' not in p_des) \
                or ('baserunner advance' in p_des and 'walk' not in p_des
                    and 'strikeout' not in p_des) \
                or ('caught stealing' in p_des and 'out at' in p_des
                    and 'walk' not in p_des and 'strikeout' not in p_des) \
                or ('baserunner out advancing' in p_des and 'out at' in p_des
                    and 'walk' not in p_des and 'strikeout' not in p_des) \
                or ('steals' in p_des and 'walk' not in p_des
                    and 'strikeout' not in p_des) \
                or 'balk' in p_des:
            team_df_PA.loc[i] = 0
    team_df_PA = team_df_PA[team_df_PA["PA"] == 1].reset_index()\
                                                  .drop("index", axis=1)
    # Add a new column showing whether there is a runner on base
    team_df_PA["is_OB"] = team_df_PA.RoB.apply(
        lambda x: 0 if x == '---' else 1)
    # Add a new column showing whether there is a runner on socring position
    team_df_PA["is_ISP"] = team_df_PA.RoB.apply(
        lambda x: 1 if '2' in x or '3' in x else 0)
    # Add batting order (1-9)
    team_df_PA["Batting_Order"] = [i % 9 + 1 for i in range(len(team_df_PA))]
    # Get the sum of PA and other stats for each batting position
    team_df_gb = team_df_PA.groupby(by='Batting_Order')[
        ["PA", "is_OB", "is_ISP"]].sum().reset_index()
    team_df_gb["Team"] = team  # Add team name
    team_df_gb["URL"] = game_page_url
    # Validation
    # Outliers include some false accounting in PA
    # For example, in this game, Chris Young's PA got counted twice.
    # baseball-reference.com/boxes/BOS/BOS201708250.shtml
    otls = ["https://www.baseball-reference.com/boxes/BOS/BOS201708250.shtml"]
    if team_df_gb["PA"].sum() != team_actual_pa:
        if game_page_url not in otls:
            print(game_page_url)
            print(team_df_gb["PA"].sum() - team_actual_pa)
    return team_df_gb


def get_team_pa(team_page):
    """
    This function is to get the desired info for all 162 games of one team.
    The input is a set.
    Index 0 is the team page url and index 1 is the team page title.
    """
    team_page_url = team_page[0]
    team_page_title = team_page[1]
    team = team_page_url.split("/")[-2]  # Get team name
    print(f"Team: {team}")  # Print team name
    game_pages = get_game_page(team_page_url)  # Get game url
    team_df_list = []
    count = 0
    for game_page in game_pages:
        # sleep(1)  # 1 second delay b/w scraping request
        # Print progress
        count += 1
        if count % 30 == 0:
            print(f"{count} Games Done")
        # Get df for a single game
        team_df = get_pa(game_page, team, team_page_title)
        team_df["GM"] = count  # Add game number
        team_df_list.append(team_df)
    print(f"{len(team_df_list)} Games in Total\n")  # Print total games played
    return pd.concat(team_df_list)


def get_season_pa(season_page_url):
    """
    This function is to get the desired info of all the teams for one season.
    The input is a single season' page.
    """
    year = season_page_url.split('/')[-1].split('.')[0]  # Get year
    print(f"Season: {year}\n")
    team_pages = get_team_page(season_page_url)
    season_df = pd.concat([get_team_pa(team_page) for team_page in team_pages])
    season_df['Season'] = year
    return season_df
