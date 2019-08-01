import pandas as pd
import numpy as np
from batting_order import *
import warnings
warnings.filterwarnings('ignore')


seasons = sorted(list(range(2011, 2018)), reverse=True)
for season in seasons:
    season_page_url = f"https://www.baseball-reference.com/leagues/MLB/{str(season)}.shtml"
    season_df = get_season_pa(season_page_url)
    season_df.to_csv(f'season_scraped/{str(season)}.csv', index=False)
