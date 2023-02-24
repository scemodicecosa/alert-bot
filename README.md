# alert-bot
bot telegram per inviare alert relativi a signal

testato su python 3.10  
## Installazione
* Installare python requirements `pip install -r requirements.txt`
* Configurare account google per gspread ([link](https://docs.gspread.org/en/latest/oauth2.html))
* Clonare SpreadSheet da [qui](https://docs.google.com/spreadsheets/d/1oMzEpjTMJfAi5kzUkwK99R4tM0pW50gaHZSso0JHXzE/edit?usp=sharing)
* Inserire in `credentials.py`:
  * `token_key` api key del bot telegram
  * `gcred_path` path completo al file delle credenziali google
  * `chat_id` id della chat con il bot ([link](https://docs.influxdata.com/kapacitor/v1.6/event_handlers/telegram/#get-your-telegram-chat-id))
* Inserire in `spread_alert.py`:
  * `spread_name` nome dello spreadsheet da cui prendere i signal
* `python signal_alert_bot.py` esegui il bot
* `python spread_alert.py` main di test, vengono controllati tutti i signal sullo spreadsheet e viene inviato l'alert indipendetemente dal prezzo 

## Comandi Bot
* `/list` controlla prezzo di tutti i signal e invia alert forzatamente
* `/search text` cerca tutti i ticker disponibili con tradingview_ta (per l'elenco completo consultare [qui](https://tvdb.brianthe.dev/) che è più semplice) 