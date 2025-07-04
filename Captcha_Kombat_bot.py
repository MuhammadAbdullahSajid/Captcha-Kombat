import logging
import random
import string
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

user_captcha = {}  # Store user_id:captcha_string
user_scores = {}   # Store user_id:score

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "👋 Welcome to Captcha Kombat!\n"
        "Type /solve to get a captcha and start earning points.\n"
        "Type /score to check your points.\n"
        "Type /leader to see the leaderboard."
    )

def generate_captcha(length=5):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def solve(update: Update, context: CallbackContext):
    captcha = generate_captcha()
    user_captcha[update.message.from_user.id] = captcha
    update.message.reply_text(f"🧠 Solve this captcha: {captcha}\nReply with the exact code!")

def check_answer(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in user_captcha:
        update.message.reply_text("Please type /solve first to get a captcha.")
        return

    answer = update.message.text.strip().upper()
    if answer == user_captcha[user_id]:
        user_scores[user_id] = user_scores.get(user_id, 0) + 1
        update.message.reply_text(
            f"✅ Correct! Your score is now {user_scores[user_id]}.\nType /solve for next captcha."
        )
        del user_captcha[user_id]
    else:
        update.message.reply_text("❌ Wrong answer! Try again or type /solve for a new captcha.")

def score(update: Update, context: CallbackContext):
    score = user_scores.get(update.message.from_user.id, 0)
    update.message.reply_text(f"📊 Your score: {score}")

def leader(update: Update, context: CallbackContext):
    if not user_scores:
        update.message.reply_text("No scores yet. Be the first to solve a captcha!")
        return
    # Sort users by score desc
    sorted_scores = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)
    msg = "🏆 Leaderboard:\n"
    for i, (user_id, score) in enumerate(sorted_scores[:5], start=1):
        msg += f"{i}. User ID: {user_id} - {score} points\n"
    update.message.reply_text(msg)

def main():
    import os
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN environment variable not set")
        return

    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("solve", solve))
    dp.add_handler(CommandHandler("score", score))
    dp.add_handler(CommandHandler("leader", leader))

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, check_answer))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
