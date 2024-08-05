import logging
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from text_generation_api import Endpoint

# Initialize the Endpoint
tga = Endpoint("http://<host>:<port>")

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Define the start command
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hi! Send me a prompt, and I will generate text for you.')

# Define the help command
def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Send any text, and I will complete it using a text generation model.')

# Define the echo command that processes user messages
def generate_text(update: Update, context: CallbackContext) -> None:
    prompt = update.message.text
    result = tga.generate(
        model="gpt2",  # You can specify other models here
        prompt=prompt
    )
    update.message.reply_text(result['generated_text'])

def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("6247500066:AAGdftkEye7peoG0QSpu3MmKC0795Yr4bpU")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - generate text
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, generate_text))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
    updater.idle()

if __name__ == '__main__':
    main()