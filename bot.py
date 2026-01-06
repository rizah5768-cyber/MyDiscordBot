import discord
from discord import app_commands
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# ---------------------- نظام البقاء حياً (Flask) ----------------------
# هذا الجزء مهم جداً لمنصة Render لكي لا يتوقف البوت
app = Flask('')

@app.route('/')
def home():
    return "البوت يعمل بنجاح 24/7!"

def run_flask():
    # Render يستخدم المنفذ 10000 تلقائياً في الخطة المجانية
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
        # مزامنة أوامر السلاش عند تشغيل البوت
        await self.tree.sync()
        print(f"✅ تم تحديث جميع الأوامر ومزامنتها بنجاح!")

bot = MyBot()

# ---------------------- أوامر السلاش ----------------------

@bot.tree.command(name="say", description="إرسال رسالة منسقة عبر البوت")
async def say(interaction: discord.Interaction, message: str):
    embed = discord.Embed(description=message, color=discord.Color.blue())
    embed.set_footer(text=f"بواسطة: {interaction.user.display_name}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="اعطاء-رتبة", description="إعطاء رتبة لعضو (اختر من القائمة)")
@app_commands.describe(member="العضو المستهدف", role="اختر الرتبة")
async def give_role(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    if not interaction.user.guild_permissions.manage_roles:
        return await interaction.response.send_message("❌ ليس لديك صلاحية إدارة الرتب", ephemeral=True)
    try:
        await member.add_roles(role)
        await interaction.response.send_message(f"✅ تم إعطاء رتبة {role.mention} للعضو {member.mention}")
    except:
        await interaction.response.send_message("❌ فشل: تأكد أن رتبة البوت أعلى من الرتبة المطلوبة.")

@bot.tree.command(name="ازالة-رتبة", description="إزالة رتبة من عضو (اختر من القائمة)")
@app_commands.describe(member="العضو المستهدف", role="اختر الرتبة")
async def remove_role(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    if not interaction.user.guild_permissions.manage_roles:
        return await interaction.response.send_message("❌ ليس لديك صلاحية إدارة الرتب", ephemeral=True)
    try:
        await member.remove_roles(role)
        await interaction.response.send_message(f"🗑️ تم إزالة رتبة {role.mention} من العضو {member.mention}")
    except:
        await interaction.response.send_message("❌ فشل: تأكد أن رتبة البوت أعلى من الرتبة المطلوبة.")

@bot.tree.command(name="كشف-رتبة", description="يظهر قائمة بأسماء الأعضاء الذين لديهم هذه الرتبة")
@app_commands.describe(role="اختر الرتبة المراد كشف أعضائها")
async def list_role_members(interaction: discord.Interaction, role: discord.Role):
    await interaction.response.defer()
    
    members = role.members
    if not members:
        return await interaction.followup.send(f"⚠️ لا يوجد أعضاء يحملون رتبة {role.mention}")

    member_list = "\n".join([f"• {m.mention} ({m.name})" for m in members[:20]])
    if len(members) > 20:
        member_list += f"\n\n... وغيرها {len(members) - 20} عضواً"

    embed = discord.Embed(
        title=f"قائمة أعضاء رتبة: {role.name}",
        description=member_list,
        color=role.color
    )
    embed.set_footer(text=f"إجمالي الأعضاء: {len(members)}")
    await interaction.followup.send(embed=embed)

# ---------------------- تشغيل البوت ----------------------
if __name__ == "__main__":
    # تشغيل خادم ويب مصغر في الخلفية لإبقاء البوت متصلاً
    keep_alive()
    
    # قراءة التوكن من Environment Variables في Render
    TOKEN = os.getenv('DISCORD_TOKEN')
    
    if TOKEN:
        try:
            bot.run(TOKEN)
        except Exception as e:
            print(f"❌ حدث خطأ أثناء محاولة تشغيل البوت: {e}")
    else:
        print("❌ التوكن (DISCORD_TOKEN) مفقود من إعدادات البيئة!")
