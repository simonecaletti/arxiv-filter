# Overview

Arxiv filter is similar to the standard arxiv email digests, but allows you to filter using keywords so that the email digests are significantly shorter. This is useful if you want to target a subset of a category (e.g., not all of cs.AI), and filter by areas of research (e.g, "reinforcement learning"), authors (e.g., "Yann LeCun"), or some other filter keyword.

# Installation

You should install this on a machine that is always on and has internet access. The installation has been tested on Ubuntu 16.04, but should be easy to replicate on other Unix systems. The installation process should take less than 10 minutes.

#### Choose categories and keywords

Arxiv filter works by finding all articles that
1. Were submitted in the past day
2. Are in one of the categories listed in categories.txt
3. Have in the title at least one of the keywords listed in titles.txt
4. Have as an author at least one of the names listed in authors.txt

You should change categories.txt, titles.txt and authors.txt based on your interests. (Note: capitalization does not matter for titles and authors. Also second name only should work, although it doesn't distinguish between people with different first names.)

### Setup yagmail


#### Setup the script locally

Run the following to install the necessary python libraries:
```
$ pip install datetime pytz requests arxiv python-dotenv
```
make a `.env` file in the same directory as `run.py` and add the following
```
MAILGUN-SANDBOX-NAME=<your sandbox name>
MAILGUN-EMAIL-RECIPIENT=<you email address>
MAILGUN-API-KEY=<you api key>
```
Run using 
```
$ python run.py
```
You can install a local cronjob in linux by running
```
$ crontab -e
```
and adding 
```
0 7 * * * /path/to/python /path/to/arxiv-filter/run.py
```
which will run everyday at 7am as long as your machine is running.
This has the downside of only running if your machine is up and running so I recommend setting this up for free on Heroku.

#### Setting up Heroku for scheduling (recommended)
1. Make an account with [Heroku](https://www.heroku.com).
2. Create a new app and follow steps to deploy the code using the Heroku CLI.
3. Click the "Settings" tab and add the environment variables in `.env` to Config Vars. This is where the app running on Heroku will find the environment variables.
3. Click the "Resources" tab then the "find more add-ons" button and search for "Advanced Scheduler".
4. Go to the "Overview" tab and click on "Advanced Scheduler" then add a new trigger.
5. Add `python run.py` as the command
6. Click Type - Recurring
7. Click Schedule - Cron Expression
8. Add `0 7 * * *` which will trigger at 7am everyday.

(Note: arxiv filter searches over submissions from the past week and---after filtering---only emails you submissions that it has not sent you before. If you want to start from scratch, delete the file previous_arxivs.txt)
