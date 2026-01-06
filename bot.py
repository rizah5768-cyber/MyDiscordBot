import discord
from discord import app_commands
from discord.ext import commands
import os
from keep_alive import keep_alive  # استدعاء ملف البقاء حياً

# ---------------------- إعدادات البوت ----------------------
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # مزامنة الأوامر مع ديسكورد
        await self.tree.sync()
        print(f"✅ تم تحديث أوامر السلاش!")

bot = MyBot()

# ---------------------- أوامر السلاش الذكية ----------------------

@bot.tree.command(name="say", description="إرسال رسالة منسقة عبر البوت")
async def say(interaction: discord.Interaction, message: str):
    embed = discord.Embed(description=message, color=discord.Color.blue())
    embed.set_footer(text=f"بواسطة: {interaction.user.display_name}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="اعطاء-رتبة", description="إعطاء رتبة لعضو (اختر من القائمة)")
@app_commands.describe(member="العضو المستهدف", role="اختر الرتبة من القائمة")
async def give_role(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    if not interaction.user.guild_permissions.manage_roles:
        return await interaction.response.send_message("❌ ليس لديك صلاحية إدارة الرتب", ephemeral=True)
    
    try:
        await member.add_roles(role)
        embed = discord.Embed(title="✅ تم منح الرتبة", color=discord.Color.green())
        embed.add_field(name="العضو:", value=member.mention)
        embed.add_field(name="الرتبة:", value=role.mention)
        await interaction.response.send_message(embed=embed)
    except discord.Forbidden:
        await interaction.response.send_message("❌ فشل: رتبة البوت أدنى من الرتبة المطلوبة أو تنقصه صلاحيات.", ephemeral=True)

@bot.tree.command(name="ازالة-رتبة", description="إزالة رتبة من عضو (اختر من القائمة)")
@app_commands.describe(member="العضو المستهدف", role="اختر الرتبة من القائمة")
async def remove_role(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    if not interaction.user.guild_permissions.manage_roles:
        return await interaction.response.send_message("❌ ليس لديك صلاحية إدارة الرتب", ephemeral=True)

    try:
        await member.remove_roles(role)
        embed = discord.Embed(title="🗑️ تم إزالة الرتبة", color=discord.Color.red())
        embed.add_field(name="العضو:", value=member.mention)
        embed.add_field(name="الرتبة:", value=role.mention)
        await interaction.response.send_message(embed=embed)
    except discord.Forbidden:
        await interaction.response.send_message("❌ فشل: رتبة البوت أدنى من الرتبة المطلوبة.", ephemeral=True)

# ---------------------- التشغيل ----------------------
keep_alive() # تشغيل السيرفر الوهمي لمنع الإغلاق في Render

TOKEN = os.getenv('DISCORD_TOKEN')
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ خطأ: التوكن غير موجود في Environment Variables!")
