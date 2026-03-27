import os
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, InlineQueryHandler

games = {}

# /start مع الحقوق
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("اتحدى واحد يامرعبهم 😉", switch_inline_query="")]]
    await update.message.reply_text(
        "🔥 هلا بيك منور/ة🔥\n"
        "اضغط الزر وطب بيهم بالطابوكة دوسة ونص  😎\n\n@wwwwl2 -- صانع البوت",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# إنشاء التحدي
async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query
    user = query.from_user
    chat_type = getattr(query, "chat_type", "private")  # private, group, supergroup, channel

    game_id = str(user.id)
    games[game_id] = {"player1": user.id, "player2": None, "choices": {}}
    p1_name = f"@{user.username}" if user.username else user.first_name

    # النص حسب الشخص أو المجموعة/القناة
    if chat_type == "private":
        text = f"{p1_name} يتحداك تقدر تسحلة بالطابوكة ورقة مقص؟"
    else:
        text = f"{p1_name} يتحداكم منو بيكم يقدر يسحله بالطابوكة ورقة مقص؟"

    result = InlineQueryResultArticle(
        id=game_id,
        title="طابوكة ورقة مقص",
        input_message_content=InputTextMessageContent(text),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("تعال اخسرك يابوت 😜", callback_data=f"join_{game_id}")]
        ])
    )
    await query.answer([result])

# دخول اللاعب الثاني
async def join_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    game_id = query.data.split("_")[1]
    user = query.from_user

    if game_id not in games:
        await query.answer("اللعبة انتهت يلا روحوا لاهلكم خلصنة", show_alert=True)
        return

    game = games[game_id]

    if user.id == game["player1"]:
        await query.answer("ما تكدر تلعب ويا نفسك 😂", show_alert=True)
        return

    if game["player2"] is None:
        game["player2"] = user.id
    else:
        await query.answer("شعدك داخل مجاي تشوفهم يلعبون", show_alert=True)
        return

    keyboard = [[
        InlineKeyboardButton("🪨 طابوكة", callback_data=f"pick_{game_id}_حجرة"),
        InlineKeyboardButton("📄 ورقة", callback_data=f"pick_{game_id}_ورقة"),
        InlineKeyboardButton("✂️ مقص", callback_data=f"pick_{game_id}_مقص")
    ]]

    await query.edit_message_text(
        f"🔥 {user.first_name} دخل اللعبة!\nكل واحد يختار بسرعة 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# الاختيار والنتيجة
async def pick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, game_id, choice = query.data.split("_")
    user = query.from_user
    game = games.get(game_id)
    if not game: return

    if user.id not in [game["player1"], game["player2"]]:
        await query.answer("انتي او انت مو لاعب او لاعبة ", show_alert=True)
        return

    game["choices"][user.id] = choice

    if len(game["choices"]) < 2:
        await query.answer("تم طلع اسمك بالرعاية انتظر الثاني")
        return

    # الحصول على اللاعبين
    p1_id = game["player1"]
    p2_id = game["player2"]
    c1 = game["choices"][p1_id]
    c2 = game["choices"][p2_id]

    p1_chat = await context.bot.get_chat(p1_id)
    p2_chat = await context.bot.get_chat(p2_id)
    p1_name = f"@{p1_chat.username}" if p1_chat.username else p1_chat.first_name
    p2_name = f"@{p2_chat.username}" if p2_chat.username else p2_chat.first_name

    # العد التنازلي قبل النتيجة
    for i in range(3, 0, -1):
        await asyncio.sleep(1)
        await query.edit_message_text(f"بعد شوي للنتيجة: {i} ...")
    await asyncio.sleep(1)

    # تحديد الفائز برسائل ممتعة
    if c1 == c2:
        result = "🤝 تعادل لا خاسر ولا فايز "
    elif (c1 == "حجرة" and c2 == "مقص") or (c1 == "ورقة" and c2 == "حجرة") or (c1 == "مقص" and c2 == "ورقة"):
        result = f"{p1_name} فلش الخصم وفاز 🔥"
    else:
        result = f" {p2_name} فلش الخصم وفاز 🔥"

    await query.edit_message_text(
        f"🧑‍🦱 {p1_name}: {c1}\n"
        f"🧑‍🦰 {p2_name}: {c2}\n\n{result}"
    )

    del games[game_id]

# تشغيل البوت باستخدام متغير البيئة
TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    raise ValueError("يجب وضع متغير البيئة TOKEN لتوكن البوت")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(InlineQueryHandler(inline_query))
app.add_handler(CallbackQueryHandler(join_game, pattern="join_"))
app.add_handler(CallbackQueryHandler(pick, pattern="pick_"))
app.run_polling()
