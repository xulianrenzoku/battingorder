# A Study of Batting Order

This project is motivated by a baseball question at Zhihu.com - "Why teams let their best hitters bat fourth? ([为什么棒球第四棒是强棒？](https://www.zhihu.com/question/269068185))"


This project consists of three parts.
- Data Acquisition
- Data Quality Validation
- Data Analysis (Unfinished)

### Data Acquisition
For data scraping, the objective is to obtain three types of records for each batting order:
- Number of plate appearances
- Number of plate appearances with runners on base
- Number of plate appearances with runners in scoring positions

Since we are pursuing the plate appearnce numbers for each batting order instead of individual players, so we have no choice but painstakingly going through the **play-by-play** record of each game.

**Baseball-Reference.com** is chosen due to its perfect accounting of the play-by-play data. Not only it has the records of every single play, but also has an 'RoB' column that keeps information regarding baserunners. Below is an example.

<img src='static/play_by_play_example.png'>

The major challenge during the data scraping process, is to write a robust set of rules to identify whether the play description of an event makes a plate appearnce. 

In order to perfect the rules, I scraped all the records from 2011 to 2018 (38876 games in total), and obtained all the possible edge cases, from [a walk-off balk](https://www.baseball-reference.com/boxes/LAN/LAN201506180.shtml) to a stupid 'Neil Walker caught stealing (*Hint: a walk makes a plate appearance*)'. I mean, how can you not be romantic about baseball? 

In terms of time, it takes around 70 minutes to scrape a season (30 teams, 162 games each).

[See Scraping Script](https://github.com/xulianrenzoku/battingorder/blob/master/batting_order.py)

### Data Quality Validation
[Team statistics pages](https://www.baseball-reference.com/leagues/MLB/2018.shtml) of Baseball-Reference.com are used to validate the quality of the scraped data. If the number does not match, then scrape the batting statistics of 162 games of the anomaly team (Happened to be the [2012 Milwaukee Brewers](https://github.com/xulianrenzoku/battingorder/blob/master/batting_order_data_scraping_quality_validation.ipynb)) for further investigation.

[See data quality validation for the 2018 season](https://github.com/xulianrenzoku/battingorder/blob/master/batting_order_data_scraping_example_2018.ipynb)

[See data quality validation for 2011-17 seasons](https://github.com/xulianrenzoku/battingorder/blob/master/batting_order_data_scraping_quality_validation.ipynb)

### Data Analysis (Unfinished)
