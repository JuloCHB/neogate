import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

load_dotenv()
TOKEN = "7713512345:AAEF-UfSbtpPtH8wtFyhRbBKPQj8R91LIIk"

# Features that require purchase
locked_features = ["wallets", "filters", "listings"]

user_settings = {
    "lang_options": ["🇺🇸 American", "🇨🇳 Chinese", "🇪🇸 Spanish"],
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

translations = {
    "🇺🇸 American": {
        "welcome": "👋 *Welcome to NeoGate Bot!*",
        "desc": "🚀 _Get real-time token listings alerts, filters, and auto-trading tools._",
        "use_menu": "💡 *Use the menu below to configure and monitor your strategy 👇*",
        "language_set": "✅ Language set to American."
    },
    "🇨🇳 Chinese": {
        "welcome": "👋 *欢迎使用 NeoGate 机器人！*",
        "desc": "🚀 _获取实时代币上线提醒、筛选器和自动交易工具。_",
        "use_menu": "💡 *请使用下方菜单来配置和监控你的策略 👇*",
        "language_set": "✅ 语言设置为中文。"
    },
    "🇪🇸 Spanish": {
        "welcome": "👋 *¡Bienvenido al Bot de NeoGate!*",
        "desc": "🚀 _Recibe alertas de nuevos tokens, filtros y herramientas de auto-trading en tiempo real._",
        "use_menu": "💡 *Usa el menú abajo para configurar y monitorear tu estrategia 👇*",
        "language_set": "✅ Idioma configurado a Español."
    }
}

def language_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇺🇸 American", callback_data="lang_american")],
        [InlineKeyboardButton("🇨🇳 Chinese", callback_data="lang_chinese")],
        [InlineKeyboardButton("🇪🇸 Spanish", callback_data="lang_spanish")],
        [InlineKeyboardButton("⬅️ Back", callback_data='settings')]
    ])

def settings_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🌐 Language: {user_settings['lang']}", callback_data='lang')],
        [InlineKeyboardButton(f"💸 Buy Mode: {user_settings['buy_mode']}", callback_data='buy_mode_set')],
        [InlineKeyboardButton(f"💰 Sell Mode: {user_settings['sell_mode']}", callback_data='sell_mode_set')],
        [InlineKeyboardButton(f"🛡 Buy MEV: {user_settings['buy_mev']}", callback_data='buy_mev')],
        [InlineKeyboardButton(f"🛡 Sell MEV: {user_settings['sell_mev']}", callback_data='sell_mev')],
        [InlineKeyboardButton("⬅️ Back", callback_data='back_to_main')]
    ])

def main_menu():
    auto_buy_icon = "✅" if user_settings["auto_buy"] == "ON" else "❌"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💼 Wallets", callback_data='wallets'), InlineKeyboardButton("💼 Positions", callback_data='positions')],
        [InlineKeyboardButton(f"🤖 Auto Buy {auto_buy_icon}", callback_data='auto_buy'), InlineKeyboardButton("📈 Buy Mode", callback_data='buy_mode')],
        [InlineKeyboardButton("📊 DEX / CEX Filters", callback_data='filters'), InlineKeyboardButton("📡 Listings Live", callback_data='listings')],
        [InlineKeyboardButton("🔔 Notifications", callback_data='notifications'), InlineKeyboardButton("🧾 Logs", callback_data='logs')],
        [InlineKeyboardButton("⚙️ Settings", callback_data='settings'), InlineKeyboardButton("🔄 Refresh", callback_data='refresh')],
        [InlineKeyboardButton("🔑 Activate your license", callback_data='activate')],
        [InlineKeyboardButton("❌ Close", callback_data='close')]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_settings["awaiting_license"] = False
    tr = translations.get(user_settings["lang"], translations["🇺🇸 American"])
    text = (
        f"{tr['welcome']}\n\n"
        f"{tr['desc']}\n\n"
        "📘 [X](https://example.com) | 🧵 [Website](https://example.com) | 📺 [Whitepaper](https://example.com)\n\n"
        f"{tr['use_menu']}"
    )
    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=main_menu())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "lang":
        await query.edit_message_text("🌐 Select your language:", reply_markup=language_menu())
        return

    if query.data.startswith("lang_"):
        lang_map = {
            "lang_american": "🇺🇸 American",
            "lang_chinese": "🇨🇳 Chinese",
            "lang_spanish": "🇪🇸 Spanish"
        }
        selected_lang = lang_map.get(query.data)
        if selected_lang:
            user_settings["lang"] = selected_lang
            await query.edit_message_text(translations[selected_lang]["language_set"], reply_markup=settings_menu())
        return

    if query.data == "settings":
        await query.edit_message_text("⚙️ *Settings:*", parse_mode="Markdown", reply_markup=settings_menu())
        return

    # Le reste des interactions sera géré ici…

# Launch
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()
