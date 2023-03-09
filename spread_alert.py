from tradingview_ta import TA_Handler, Interval
import gspread
import pandas as pd
from datetime import *
from telegram.ext import (CallbackContext,)
from telegram import Bot
import credentials

# cambiare nome qui dello spreadsheet
spread_name = "alert-bot"

bot_alert = Bot(credentials.token_key)



def df_from_ws(ws):
    # lo spreadsheet su google deve contenere queste chia
    fkeys = ["SL", "TP1", "TP2", "EP"]
    df = pd.DataFrame(ws.get_all_records())

    for fk in fkeys:
        df[fk] = pd.to_numeric(df[fk])
    # df["SL"] = pd.to_numeric(df["SL"])
    return df


gc = gspread.service_account(filename=credentials.gcred_path)
sh = gc.open(spread_name)


# come funziona, ogni tot viene letto lo spreadsheet
# per ogni entry:
#   viene preso il prezzo e controllato l'alert in base ai parametri
#   aggiornare spreadsheet in base a sopra

# emoji per gli alert su telegram, il pollice indica che l'entrata o l'uscita è considerata "validata"
circle_green = "\U0001F7E2"
circle_red = "\U0001F534"
thumbs_up = "\U0001F44D"
thumbs_down = "\U0001F44E"


def to_alert_text(ta_h, a, price, strong, send):
    #  dato un alert genera il messaggio html che verrà inviato su telegram
    stop = ""
    price_emoji = ""
    if send:
        if a.Status == "in":
            price_emoji = circle_red
            if strong:
                price_emoji += thumbs_down
        else:
            price_emoji = circle_green
            if strong:
                price_emoji += thumbs_up

    if not pd.isna(a.SL) != 0:
        stop = f"<b><u>Stop</u></b> at <b>{a.SL}$</b>\n"

    return f"<b>{ta_h.exchange.upper()}:{ta_h.symbol.upper()}</b> {ta_h.screener}\n" \
           f"<b><u>{a.Trend.capitalize()}</u></b> at <b>{a.EP}$</b> chiusura <i>{a.Close}</i>\n" \
           f"{stop}" \
           f"Prezzo: <b><u>{price}$</u></b> {price_emoji}\n" \
           f"<i>{a.Note}</i>"


def process_alert(a, send=False):
    # processa un alert e invia una notifica se necessario
    # il parametro send=True permette di inviare ugualmente l'alert anche se il prezzo non ha superato il livello
    ta_handler = TA_Handler(
        symbol=a.Ticker,
        screener=a.Type,
        exchange=a.Exchange,
        interval=Interval.INTERVAL_1_MINUTE
    )
    price = ta_handler.get_analysis().indicators['close']

    should_send = False
    strong_send = False

    # se il segnale è _in_ viene controllato SL, altrimenti EP
    if a.Trend == "buy":
        #  il segnale viene considerato strong se il prezzo supera con
        #  uno scarto di 1.5% il livello di ingresso (a seconda di buy o sell).
        #  TODO Teoricamente lo scarto dovrebbe essere 1/10 della differenza tra EP e TP (o SL)
        if a.Status == "in":
            # se il segnale è in, vuol dire che siamo a mercato quindi controllo solo SL
            should_send = price < a.SL
            strong_send = price < a.SL * 0.985
        else:
            # il segnale non è a mercato, controllo solo l'ingresso
            should_send = price > a.EP
            strong_send = price > a.EP * 1.015

    elif a.Trend == "sell":
        if a.Status == "in":
            should_send = price > a.SL
            strong_send = price > a.SL * 1.015
        else:
            should_send = price < a.EP
            strong_send = price < a.EP * 0.985

    if send or should_send:
        # print("price", price, strong_send)
        print(F"sent alert {a.Ticker}")
        bot_alert.send_message(credentials.chat_id, to_alert_text(ta_handler, a, price, strong_send, should_send),
                               parse_mode="html")


def check_alerts_job(context: CallbackContext):
    # questa funzione viene eseguita ogni ora
    print("parte alerts job")
    for ws in sh.worksheets():
        if "done" in ws.title:
            continue
        # prendo dati da spredsheet e inserisco in pandas df
        df = df_from_ws(ws)

        now = datetime.now()
        # dt contiene i time frame da controllare, di default h1
        dt = ['h1']
        if now.hour == 0:
            # se è mezzanotte controllo anche segnali d1 e h4
            dt.append("d1")
            dt.append("h4")
        elif now.hour % 4 == 0:
            # se l'ora è multiplo di 4 controllo anche segnali h4
            dt.append("h4")

        # esegue process alert su tutti signal con timeframe in dt
        df[df["Close"].isin(dt)].apply(lambda x: process_alert(x), axis=1)


def check_all_alerts():
    # controlla tutti gli alert a prescindere dal timeframe
    for ws in sh.worksheets():
        if "done" in ws.title:
            continue
        df = df_from_ws(ws)
        df.apply(lambda x: process_alert(x, True), axis=1)


if __name__ == '__main__':
    # main di test per controllare tutti gli alert nello spreadsheet
    check_all_alerts()
