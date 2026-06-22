print("起動してる")

import discord
import os
import random
from parser import parse_pdf
from db import load_questions, reset_all, init_db
from discord.ui import View, Button

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

user_sessions = {}
pending_category = {}

# ✅ ボタン
class AnswerView(View):
    def __init__(self, user_id):
        super().__init__(timeout=120)
        self.user_id = user_id

    async def handle(self, interaction, choice):
        session = user_sessions[self.user_id]
        q = session["questions"][session["index"]]

        if choice == q["answer"]:
            result = "✅ 正解！"
            session["score"] += 1
        else:
            result = f"❌ 不正解！正解は {q['answer']}"

        session["index"] += 1

        if session["index"] >= len(session["questions"]):
            await interaction.response.send_message(
                f"{result}\n\n🎉 終了！ {session['score']}/{len(session['questions'])}"
            )
            del user_sessions[self.user_id]
            return

        next_q = session["questions"][session["index"]]

        text = f"{result}\n\n📘 {session['category']} Q{session['index']+1}\n\n{next_q['question']}\n\n"
        for k, v in next_q["choices"].items():
            text += f"{k}: {v}\n"

        view = AnswerView(self.user_id)

        if next_q.get("image"):
            file = discord.File(next_q["image"])
            await interaction.response.send_message(text, file=file, view=view)
        else:
            await interaction.response.send_message(text, view=view)

    @discord.ui.button(label="A", style=discord.ButtonStyle.primary)
    async def a(self, i, b): await self.handle(i, "A")
    @discord.ui.button(label="B", style=discord.ButtonStyle.primary)
    async def b(self, i, b): await self.handle(i, "B")
    @discord.ui.button(label="C", style=discord.ButtonStyle.primary)
    async def c(self, i, b): await self.handle(i, "C")
    @discord.ui.button(label="D", style=discord.ButtonStyle.primary)
    async def d(self, i, b): await self.handle(i, "D")
    @discord.ui.button(label="E", style=discord.ButtonStyle.primary)
    async def e(self, i, b): await self.handle(i, "E")


@client.event
async def on_ready():
    init_db()
    print(f"✅ ログイン成功: {client.user}")


@client.event
async def on_message(message):
    if message.author.bot:
        return

    print("📩 受信:", message.content)
    print("📎 添付:", message.attachments)

    # ✅ loadコマンド
    if message.content.startswith(")load"):
        parts = message.content.split(" ")

        if len(parts) < 2:
            await message.channel.send("❌ 例: )load 感染")
            return

        pending_category[message.author.id] = parts[1]

        await message.channel.send("📄 PDF送ってください")
        return

    # ✅ PDF処理
    if message.attachments:
        print("✅ 添付あり")

        for att in message.attachments:
            print("ファイル:", att.filename)

            # ✅ 小文字化で確実に検出
            if att.filename.lower().endswith(".pdf"):

                category = pending_category.get(message.author.id)
                print("カテゴリ:", category)

                if not category:
                    await message.channel.send("❌ 先に )load 分野名")
                    return

                path = f"./{att.filename}"
                await att.save(path)
                print("保存OK")

                try:
                    count = parse_pdf(path, category)
                    print("解析結果:", count)

                    await message.channel.send(f"✅ {category}：{count}問登録")
                except Exception as e:
                    print("❌ エラー:", e)
                    await message.channel.send(f"❌ エラー発生: {e}")

                del pending_category[message.author.id]
                return

        # ✅ PDFじゃなかった場合
        await message.channel.send("❌ PDFファイルを送ってください")
        return

    # ✅ CBT開始
    if message.content.startswith(")start"):
        parts = message.content.split(" ")

        if len(parts) < 2:
            await message.channel.send("❌ 例: )start 感染")
            return

        category = parts[1]

        qs = load_questions(category if category != "all" else "all")

        if not qs:
            await message.channel.send("❌ 問題なし")
            return

        random.shuffle(qs)

        user_sessions[message.author.id] = {
            "index": 0,
            "score": 0,
            "questions": qs,
            "category": category
        }

        await message.channel.send("✅ スタート")
        await send_question(message)
        return

    # ✅ 全削除
    if message.content == ")reset_all":
        reset_all()
        user_sessions.clear()
        await message.channel.send("✅ 全削除完了")


async def send_question(ctx):
    uid = ctx.author.id
    session = user_sessions[uid]
    q = session["questions"][session["index"]]

    text = f"📘 {session['category']} Q1\n\n{q['question']}\n\n"
    for k, v in q["choices"].items():
        text += f"{k}: {v}\n"

    view = AnswerView(uid)

    if q.get("image"):
        file = discord.File(q["image"])
        await ctx.channel.send(text, file=file, view=view)
    else:
        await ctx.channel.send(text, view=view)


client.run(TOKEN)
