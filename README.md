# htb-sapienza-bot
Python Telegram bot for the HackTheBox Sapienza team
@HTB_sapienza_bot

## USAGE
1. Install or clone this repo.
2. Install Docker.
3. Create the cookies file in the db directory (it's listed in the .gitignore not to commit sensitive data by mistake) and `ehco {} > db/cookies` , this will prevent getting parsing errors the first time it is read.
4. Build the image `docker build . -t htb`
5. Run the container `docker run --rm --name htb -it --env EMAIL=your@htbmail --env PASSWORD=your_pass --env TOKEN=bot_token  htb`. At the first run it will automatically import the db, then you'll need to schedule a job like in `db/crontab`.

## FEATURES
* `/users` lists all the Sapienza group users with their stats.
* `/users name` lists the 'name' stats.
* `/machines` lists all the machines the group has owned (active or not).
* `/machines name` lists the 'name' machine stats (how many users and how many roots the group has owned on that machine).
* `/uni name` lists the 'name' university ranking stats.
