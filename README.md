# A Study of Batting Order

This project is motivated by a baseball question at Zhihu.com ([为什么棒球第四棒是强棒？](https://www.zhihu.com/question/269068185))


This project consists of three parts.
- Data Scraping
- Data Quality Validation
- Data Analysis (Unfinished)

### Data Scraping
For data scraping, the objective is to obtain three types of records for each batting order:
- Number of plate appearances
- Number of plate appearances with runners on base
- Number of plate appearances with runners in scoring positions

Since we are pursuing the plate appearnce numbers for each batting order instead of individual players, so we have no choice but going through the **play-by-play** record of each game.

**Baseball-Reference.com** is chosen due to its perfect accounting in terms of play-by-play. Not only it has the records of every single play, but also has an 'RoB' column that keeps information regarding baserunners. Below is an example.

<img src='static/play_by_play_example.png'>

The major challenge to tackle during the data scraping process, is to write a robust set of rules to identify whether the play description of an event makes a plate appearnce. 

In order to perfect the rules, I scraped all the records from 2011 to 2018 (38876 games in total), and obtained all the possible edge cases, from [a walk-off balk](https://www.baseball-reference.com/boxes/LAN/LAN201506180.shtml) to a stupid 'Neil Walker caught stealing' (*Hint: a walk makes a plate appearance*). I mean, how can you not be romantic about baseball? 

[See Scraping Script](https://github.com/xulianrenzoku/battingorder/blob/master/batting_order.py)

### Data Quality Validation

### Data Analysis (Unfinished)
