# searchCraigsList

Goal: to search craigslist for matching hits, and post the results to a slack channel for use.

Use: run in background on computer. Every <10> minutes script will look at new postings, post them to slack, filter out some, and flag for specific features it finds.


To set up:

0a. Clone this repository.
0b. Install https://github.com/slackapi/python-slackclient with `pip install slackclient`
0c. Install https://pypi.org/project/python-craigslist/ with `pip install python-craigslist`


1a. Create a slack channel.

1b. Create slack channels "housing", "logging", and "repeats". Mute logging and repeats channels (unless you want notifications for these!)

1c. Create a slack token (https://api.slack.com/custom-integrations/legacy-tokens, scroll down and click "create token") and save this to a new file, "token.txt".


2. Edit the checkCraigslist.py. Ignore all files "...\_yuriy..."; these were made for a friend.

2a. Edit lines 77-78 for price and size, line 76 for general location (boston, cambridge)

2b. Edit line 86-90 and 99-100 to define your ideal region, and line 165 to use geotags.

2c. Edit line 238 to match your move in dates

2d. Add additional filters if necessary, around line 180. The stripped html lives in "soup" eg. line 180. "result", line 118, has some pre-pulled values also, if that's useful.

2e. checkCraigslist_yuriy.py has a couple useful functions, including manhattan distance.


Open a command line window. Move to the repository, and run runCheckCraigslist.py.
