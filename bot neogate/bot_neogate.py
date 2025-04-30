import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

load_dotenv()
TOKEN = "7713512345:AAEF-UfSbtpPtH8wtFyhRbBKPQj8R91LIIk"

# 🔐 Features that require purchase
locked_features = ["wallets", "filters", "listings"]

user_settings = {
    "limit_sell": "None",
    "stop_loss": "None",
    "awaiting_custom": None
}

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📈 Buy Mode", callback_data='buy_mode')],
        [InlineKeyboardButton("❌ Close", callback_data='close')]
    ])

def buy_mode_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Limit Sell: 5%", callback_data="limit_5"),
         InlineKeyboardButton("10%", callback_data="limit_10"),
         InlineKeyboardButton("20%", callback_data="limit_20"),
         InlineKeyboardButton("30%", callback_data="limit_30")],
        [InlineKeyboardButton("Custom %", callback_data="limit_custom"),
         InlineKeyboardButton("None", callback_data="limit_none")],
        [InlineKeyboardButton("Stop Loss: 5%", callback_data="stop_5"),
         InlineKeyboardButton("10%", callback_data="stop_10"),
         InlineKeyboardButton("20%", callback_data="stop_20"),
         InlineKeyboardButton("30%", callback_data="stop_30")],
        [InlineKeyboardButton("Custom %", callback_data="stop_custom"),
         InlineKeyboardButton("None", callback_data="stop_none")],
        [InlineKeyboardButton("⬅️ Back", callback_data="back_to_main")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_settings["awaiting_custom"] = None
    await update.message.reply_text(
        "👋 *Welcome to NeoGate Bot!*\n\n"
        "📈 Manage your Buy Mode settings below 👇",
        parse_mode='Markdown',
        reply_markup=main_menu()
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if user_settings["awaiting_custom"] in ["limit", "stop"]:
        try:
            percent = int(update.message.text.strip().replace("%", ""))
            if not (1 <= percent <= 100):
                raise ValueError
        except ValueError:
            await update.message.reply_text("❌ Please enter a valid number between 1 and 100.")
            return
        if user_settings["awaiting_custom"] == "limit":
            user_settings["limit_sell"] = f"{percent}%"
            await update.message.reply_text(f"✅ Limit Sell set to {percent}%", reply_markup=buy_mode_menu())
        else:
            user_settings["stop_loss"] = f"{percent}%"
            await update.message.reply_text(f"✅ Stop Loss set to {percent}%", reply_markup=buy_mode_menu())
        user_settings["awaiting_custom"] = None
        return
    await update.message.reply_text("Type /start to begin.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "buy_mode":
        await query.edit_message_text("📈 *Buy Mode Settings:*", parse_mode="Markdown", reply_markup=buy_mode_menu())
        return

    if data.startswith("limit_"):
        val = data.split("_")[1]
        if val == "custom":
            user_settings["awaiting_custom"] = "limit"
            await query.edit_message_text("✍️ Enter your custom Limit Sell % in the chat:")
        else:
            user_settings["limit_sell"] = f"{val}%" if val != "none" else "None"
            await query.edit_message_text(f"✅ Limit Sell set to {user_settings['limit_sell']}", reply_markup=buy_mode_menu())
        return

    if data.startswith("stop_"):
        val = data.split("_")[1]
        if val == "custom":
            user_settings["awaiting_custom"] = "stop"
            await query.edit_message_text("✍️ Enter your custom Stop Loss % in the chat:")
        else:
            user_settings["stop_loss"] = f"{val}%" if val != "none" else "None"
            await query.edit_message_text(f"✅ Stop Loss set to {user_settings['stop_loss']}", reply_markup=buy_mode_menu())
        return

    if data == "back_to_main":
        await query.edit_message_text("🔙 Back to main menu:", reply_markup=main_menu())
        return

    if data == "close":
        await query.edit_message_text("❌ Menu closed. Type /start to reopen.")
        return

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.run_polling()
