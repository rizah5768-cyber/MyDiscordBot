import discord
from discord import app_commands
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# ---------------------- نظام البقاء حياً (Flask) لـ Render ----------------------
# هذا الجزء مهم جداً لمنصة Render لكي لا يتوقف البوت
app = Flask('')

@app.route('/')
def home():
    return "البوت يعمل بنجاح 24/7!"

def run_flask():
    # Render يحتاج المنفذ 10000 أو المنفذ المحدد في البيئة
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# ---------------------- إعدادات البوت ----------------------
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # مزامنة أوامر السلاش فوراً عند التشغيل
        await self.tree.sync()
        print(f"✅ تم تحديث ومزامنة جميع الأوامر بنجاح!")

bot = MyBot()

# ---------------------- أوامر السلاش (Slash Commands) ----------------------

# 1. أمر التحدث (Say) - مجهول
@bot.tree.command(name="say", description="إرسال رسالة منسقة عبر البوت (مجهول)")
@app_commands.describe(message="النص الذي تريد من البوت كتابته")
async def say(interaction: discord.Interaction, message: str):
    embed = discord.Embed(description=message, color=discord.Color.blue())
    await interaction.response.send_message(embed=embed)

# 2. أمر إعطاء رتبة (باستخدام قائمة ديسكورد المنسدلة)
@bot.tree.command(name="اعطاء-رتبة", description="إعطاء رتبة واحدة لعضو باستخدام القائمة المنسدلة")
@app_commands.describe(member="العضو المستهدف", role="اختر الرتبة من القائمة")
async def give_role(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    if not interaction.user.guild_permissions.manage_roles:
        return await interaction.response.send_message("❌ ليس لديك صلاحية إدارة الرتب", ephemeral=True)
    
    try:
        await member.add_roles(role)
        embed = discord.Embed(title="تعديل الرتب ✅", color=discord.Color.green())
        embed.add_field(name="الحالة:", value=f"تم إعطاء رتبة {role.mention} للعضو {member.mention}", inline=False)
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message("❌ فشل: تأكد أن رتبة البوت أعلى من الرتبة المطلوبة.", ephemeral=True)

# 3. أمر إزالة رتبة (باستخدام قائمة ديسكورد المنسدلة)
@bot.tree.command(name="ازالة-رتبة", description="إزالة رتبة واحدة من عضو باستخدام القائمة المنسدلة")
@app_commands.describe(member="العضو المستهدف", role="اختر الرتبة من القائمة")
async def remove_role(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    if not interaction.user.guild_permissions.manage_roles:
        return await interaction.response.send_message("❌ ليس لديك صلاحية إدارة الرتب", ephemeral=True)
    
    try:
        await member.remove_roles(role)
        embed = discord.Embed(title="تعديل الرتب 🗑️", color=discord.Color.red())
        embed.add_field(name="الحالة:", value=f"تم إزالة رتبة {role.mention} من العضو {member.mention}", inline=False)
        await interaction.response.send_message(embed=embed)
    except:
        await interaction.response.send_message("❌ فشل: تأكد أن رتبة البوت أعلى من الرتبة المطلوبة.", ephemeral=True)

# 4. أمر كشف رتبة (نموذج كبير ومنسق)
@bot.tree.command(name="كشف-رتبة", description="يظهر قائمة بأسماء الأعضاء الذين يحملون هذه الرتبة في نموذج كبير")
@app_commands.describe(role="اختر الرتبة المراد كشف أعضائها")
async def list_role_members(interaction: discord.Interaction, role: discord.Role):
    await interaction.response.defer()
    
    members = role.members
    if not members:
        embed = discord.Embed(
            title=f"قائمة أعضاء رتبة: {role.name}",
            description=f"⚠️ لا يوجد أعضاء يحملون رتبة {role.mention}",
            color=discord.Color.orange()
        )
        return await interaction.followup.send(embed=embed)

    member_list = "\n".join([f"• {m.mention} ({m.name})" for m in members])
    
    embed = discord.Embed(
        title=f"قائمة رتبة: {role.name}",
        description=member_list,
        color=role.color if role.color.value != 0 else discord.Color.blue()
    )
    embed.add_field(name="إحصائيات:", value=f"إجمالي عدد الحاصلين عليها: **{len(members)}** عضو")
    embed.set_footer(text=f"طلب بواسطة: {interaction.user.display_name}")
    
    await interaction.followup.send(embed=embed)

# ---------------------- تشغيل البوت ----------------------
if __name__ == "__main__":
    keep_alive()
    TOKEN = os.getenv('DISCORD_TOKEN')
    
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ خطأ: التوكن (DISCORD_TOKEN) غير موجود في إعدادات البيئة!")
