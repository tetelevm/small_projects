# based_quotes_bot

A small project for a bot that sends a quote to the channel once a day at a certain time.
The quote is a random string from data files, it can contain any text (I send random quotes from songs).

To launch:
- locally: execute `python main.py`
- on server: copy `bot_of_based_quotes.service` to `/lib/systemd/system/` and execute `systemctl enable bot_of_based_quotes.service && systemctl start bot_of_based_quotes.service`
