import discord
from discord import app_commands
from discord.ext import commands
import os
from keep_alive import keep_alive 

# ---------------------- إعدادات البوت ----------------------
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"✅ تم تحديث جميع الأوامر بما فيها كشف الرتب!")

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
    await interaction.response.defer() # للتعامل مع الرتب التي بها أعضاء كثر
    
    members = role.members
    if not members:
        return await interaction.followup.send(f"⚠️ لا يوجد أعضاء يحملون رتبة {role.mention}")

    # تنسيق القائمة
    member_list = "\n".join([f"• {m.mention} ({m.name})" for m in members[:20]]) # عرض أول 20 عضو لتجنب طول الرسالة
    if len(members) > 20:
        member_list += f"\n\n... وغيرها {len(members) - 20} عضواً"

    embed = discord.Embed(
        title=f"قائمة أعضاء رتبة: {role.name}",
        description=member_list,
        color=role.color
    )
    embed.set_footer(text=f"إجمالي الأعضاء: {len(members)}")
    
    await interaction.followup.send(embed=embed)

# ---------------------- التشغيل ----------------------
keep_alive()

TOKEN = os.getenv('DISCORD_TOKEN')
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ التوكن مفقود!")
