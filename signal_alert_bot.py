from apscheduler.triggers.cron import CronTrigger

import credentials
from spread_alert import check_alerts_job, check_all_alerts

import logging
from tradingview_ta import TradingView
from telegram import  Update

from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
)

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


def search_to_text(query):
    data = TradingView.search(query)

    s = ""
    for d in data:
        s += f"<b>{d['exchange'].upper()}:{d['symbol'].upper()}</b> {d['type']}\n{d['description']}\n\n"

    return s


def search(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(search_to_text(" ".join(context.args)), parse_mode="html")


def list(update: Update, context: CallbackContext) -> None:
    if update.message.chat_id == credentials.chat_id:
        check_all_alerts()
    else:
        update.message.reply_text("sciò")


def main() -> None:
    """Run the bot."""

    # Create the Application and pass it your bot's token.
    application = Updater(credentials.token_key)  # Application.builder().concurrent_updates(False).token(token_key).build()
    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO

    application.dispatcher.add_handler(CommandHandler("list", list))
    application.dispatcher.add_handler(CommandHandler("search", search, pass_args=True))

    # daily statistics
    application.job_queue.run_custom(callback=check_alerts_job,
                                     job_kwargs={"trigger": CronTrigger.from_crontab("* * * * *")},context=None)

    # Run the bot until the user presses Ctrl-C
    application.start_polling()
    application.idle()


if __name__ == "__main__":
    main()
    # application = Application.builder().token().build()
    # time.sleep(1000)
