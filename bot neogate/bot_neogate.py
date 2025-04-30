import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

load_dotenv()
TOKEN = "7713512345:AAEF-UfSbtpPtH8wtFyhRbBKPQj8R91LIIk"

# 🔐 Features that require purchase
locked_features = ["wallets", "filters", "listings"]

user_settings = {
    "lang": "🇺🇸 American",
    "buy_mode": "Node",
    "sell_mode": "Node",
    "buy_mev": "OFF",
    "sell_mev": "OFF",
    "auto_buy": "OFF",
    "awaiting_license": False,
    "awaiting_custom_input": None,
    "limit_sell": None,
    "stop_loss": None
}

def main_menu():
    auto_buy_icon = "✅" if user_settings["auto_buy"] == "ON" else "❌"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👛 Wallets", callback_data='wallets'), InlineKeyboardButton("💼 Positions", callback_data='positions')],
        [InlineKeyboardButton(f"🤖 Auto Buy {auto_buy_icon}", callback_data='auto_buy'), InlineKeyboardButton("📈 Buy Mode", callback_data='buy_mode')],
        [InlineKeyboardButton("📊 DEX / CEX Filters", callback_data='filters'), InlineKeyboardButton("📡 Listings Live", callback_data='listings')],
        [InlineKeyboardButton("🔔 Notifications", callback_data='notifications'), InlineKeyboardButton("🧾 Logs", callback_data='logs')],
        [InlineKeyboardButton("⚙️ Settings", callback_data='settings'), InlineKeyboardButton("🔄 Refresh", callback_data='refresh')],
        [InlineKeyboardButton("🔑 Activate your license", callback_data='activate')],
        [InlineKeyboardButton("❌ Close", callback_data='close')]
    ])

def buy_mode_menu():
    def make_button(label, setting_type, value):
        selected = user_settings[setting_type]
        is_selected = selected == value
        text = f"{label}{' ✅' if is_selected else ''}"
        return InlineKeyboardButton(text, callback_data=f"{setting_type}_{value}")

    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📉 Limit Sell", callback_data='noop')],
        [
            make_button("5%", "limit_sell", "5"),
            make_button("10%", "limit_sell", "10"),
            make_button("20%", "limit_sell", "20"),
            make_button("30%", "limit_sell", "30")
        ],
        [
            make_button("Custom %", "limit_sell", "custom"),
            make_button("None", "limit_sell", "none")
        ],
        [InlineKeyboardButton("🛑 Stop Loss", callback_data='noop')],
        [
            make_button("5%", "stop_loss", "5"),
            make_button("10%", "stop_loss", "10"),
            make_button("20%", "stop_loss", "20"),
            make_button("30%", "stop_loss", "30")
        ],
        [
            make_button("Custom %", "stop_loss", "custom"),
            make_button("None", "stop_loss", "none")
        ],
        [InlineKeyboardButton("⬅️ Back", callback_data='back_to_main')]
    ])


def settings_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🌐 Language: {user_settings['lang']}", callback_data='lang')],
        [InlineKeyboardButton(f"💸 Buy: {user_settings['buy_mode']}", callback_data='buy_mode_set')],
        [InlineKeyboardButton(f"💰 Sell: {user_settings['sell_mode']}", callback_data='sell_mode_set')],
        [InlineKeyboardButton(f"🛡 Buy MEV Protect: {user_settings['buy_mev']}", callback_data='buy_mev')],
        [InlineKeyboardButton(f"🛡 Sell MEV Protect: {user_settings['sell_mev']}", callback_data='sell_mev')],
        [InlineKeyboardButton("⬅️ Back", callback_data='back_to_main')]
    ])

def language_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇺🇸 American", callback_data='lang_en')],
        [InlineKeyboardButton("🇨🇳 Chinese", callback_data='lang_cn')],
        [InlineKeyboardButton("🇪🇸 Spanish", callback_data='lang_es')],
        [InlineKeyboardButton("⬅️ Back", callback_data='settings')]
    ])

def notifications_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 All listings", callback_data='notif_all')],
        [InlineKeyboardButton("🎯 Listings fitting filters", callback_data='notif_filtered')],
        [InlineKeyboardButton("🤖 Listings bought", callback_data='notif_bought')],
        [InlineKeyboardButton("🔕 None", callback_data='notif_none')],
        [InlineKeyboardButton("⬅️ Back", callback_data='back_to_main')]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_settings["awaiting_license"] = False
    text = (
        "👋 *Welcome to NeoGate Bot!*\n\n"
        "🚀 _Get real-time token listings alerts, filters, and auto-trading tools._\n\n"
        "📘 [X](https://example.com) | 🧵 [Website](https://example.com) | 📺 [Whitepaper](https://example.com)\n\n"
        "💡 *Use the menu below to configure and monitor your strategy 👇*"
    )
    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=main_menu())

def cycle_option(current, options):
    i = options.index(current)
    return options[(i + 1) % len(options)]

def toggle(value):
    return "ON" if value == "OFF" else "OFF"

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if user_settings.get("awaiting_license"):
        code = update.message.text.strip()
        if code == "NEOGATE123":
            user_settings["awaiting_license"] = False
            await update.message.reply_text("✅ License activated successfully!", reply_markup=main_menu())
        else:
            await update.message.reply_text("❌ Invalid code. Please try again or type /start to cancel.")
    elif user_settings.get("awaiting_custom_input"):
        input_value = update.message.text.strip().replace("%", "")
        if input_value.isdigit():
            setting = user_settings["awaiting_custom_input"]
            user_settings[setting] = input_value
            user_settings["awaiting_custom_input"] = None
            await update.message.reply_text(f"✅ {setting.replace('_', ' ').title()} set to {input_value}%", reply_markup=buy_mode_menu())
        else:
            await update.message.reply_text("❌ Please enter a valid number.")
    else:
        await update.message.reply_text("Type /start to begin.")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "activate":
        user_settings["awaiting_license"] = True
        await query.edit_message_text("🔑 *Enter your license code below:*", parse_mode="Markdown")
        return

    if query.data == "auto_buy":
        user_settings["auto_buy"] = toggle(user_settings["auto_buy"])
        await query.edit_message_text(
            f"🤖 Auto Buy is now *{user_settings['auto_buy']}*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back_to_main")]])
        )
        return

    if query.data == "buy_mode":
        await query.edit_message_text("📈 *Configure Buy Mode:*", parse_mode="Markdown", reply_markup=buy_mode_menu())
        return

    if query.data.startswith("limit_sell_"):
        value = query.data.split("_")[-1]
        if value == "custom":
            user_settings["awaiting_custom_input"] = "limit_sell"
            await query.edit_message_text("✍️ Please enter your custom *Limit Sell* %:", parse_mode="Markdown")
        else:
            user_settings["limit_sell"] = None if value == "none" else value
            msg = f"✅ Limit Sell set to: *{value}%*" if value != "none" else "🚫 Limit Sell disabled."
            await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=buy_mode_menu())
        return

    if query.data.startswith("stop_loss_"):
        value = query.data.split("_")[-1]
        if value == "custom":
            user_settings["awaiting_custom_input"] = "stop_loss"
            await query.edit_message_text("✍️ Please enter your custom *Stop Loss* %:", parse_mode="Markdown")
        else:
            user_settings["stop_loss"] = None if value == "none" else value
            msg = f"✅ Stop Loss set to: *{value}%*" if value != "none" else "🚫 Stop Loss disabled."
            await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=buy_mode_menu())
        return

    if query.data in locked_features:
        msg = f"🔒 *This feature is available for NeoGate members only.*\n\n👉 Buy the tool at [neogate.io](https://www.neogate.io)"
        await query.edit_message_text(msg, parse_mode='Markdown', disable_web_page_preview=True,
                                      reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back_to_main")]]))
        return

    if query.data == "notifications":
        await query.edit_message_text("🔔 *Notification preferences:*\n\nSelect when you want to be notified:",
                                      parse_mode="Markdown", reply_markup=notifications_menu())
        return

    if query.data == "settings":
        await query.edit_message_text("⚙️ *Settings:*", parse_mode="Markdown", reply_markup=settings_menu())
        return

    if query.data == "lang":
        await query.edit_message_text("🌐 *Select your language:*", parse_mode="Markdown", reply_markup=language_menu())
        return

    if query.data.startswith("lang_"):
        lang_map = {"lang_en": "🇺🇸 American", "lang_cn": "🇨🇳 Chinese", "lang_es": "🇪🇸 Spanish"}
        user_settings["lang"] = lang_map.get(query.data, "🇺🇸 American")
        await query.edit_message_text(f"✅ Language set to {user_settings['lang']}", reply_markup=settings_menu())
        return

    if query.data == "buy_mode_set":
        user_settings["buy_mode"] = cycle_option(user_settings["buy_mode"], ["Node", "Jito", "Auto"])
        await query.edit_message_text("💸 Buy mode updated.", reply_markup=settings_menu())
        return

    if query.data == "sell_mode_set":
        user_settings["sell_mode"] = cycle_option(user_settings["sell_mode"], ["Node", "Jito", "Auto"])
        await query.edit_message_text("💰 Sell mode updated.", reply_markup=settings_menu())
        return

    if query.data == "buy_mev":
        user_settings["buy_mev"] = toggle(user_settings["buy_mev"])
        await query.edit_message_text("🛡 Buy MEV Protect toggled.", reply_markup=settings_menu())
        return

    if query.data == "sell_mev":
        user_settings["sell_mev"] = toggle(user_settings["sell_mev"])
        await query.edit_message_text("🛡 Sell MEV Protect toggled.", reply_markup=settings_menu())
        return

    if query.data == "back_to_main":
        user_settings["awaiting_license"] = False
        await query.edit_message_text("👋 Back to main menu.", reply_markup=main_menu())
        return

    responses = {
        "positions": "📭 You have no open positions at the moment.",
        "logs": "📝 No logs available yet. Start trading to generate activity.",
        "refresh": "🔄 Menu refreshed.",
        "close": "❌ Menu closed. Type /start to reopen.",
        "notif_all": "📢 You will now receive all listings.",
        "notif_filtered": "🎯 You'll only get alerts matching your filters.",
        "notif_bought": "🤖 Only listings you've bought will trigger alerts.",
        "notif_none": "🔕 All notifications disabled."
    }

    if query.data in responses:
        await query.edit_message_text(responses[query.data],
                                      reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back_to_main")]]))
    else:
        await query.edit_message_text("⚠️ Unknown action.", reply_markup=main_menu())

# 🚀 Launch
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()
