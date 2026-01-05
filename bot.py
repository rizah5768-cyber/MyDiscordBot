import discord
from discord import app_commands
from discord.ext import commands
import os

# ---------------------- إعدادات البوت ----------------------
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"✅ تمت مزامنة أوامر السلاش بنجاح!")

bot = MyBot()

# ---------------------- دالة معالجة الرتب ----------------------
async def process_roles(interaction, member, roles_input, action_type):
    role_names = [r.strip() for r in roles_input.split(',')]
    if len(role_names) > 10:
        return await interaction.response.send_message("❌ لا يمكنك معالجة أكثر من 10 رتب في المرة الواحدة.", ephemeral=True)

    await interaction.response.defer()
    success, failed = [], []
    color = discord.Color.green() if action_type == "add" else discord.Color.red()

    for name in role_names:
        role = discord.utils.get(interaction.guild.roles, name=name) or \
               (discord.utils.get(interaction.guild.roles, id=int(name.strip('<@&>')) if name.strip('<@&>').isdigit() else 0))
        if role:
            try:
                if action_type == "add": await member.add_roles(role)
                else: await member.remove_roles(role)
                success.append(f"✅ {role.name}")
            except: failed.append(f"❌ {name} (نقص صلاحيات)")
        else: failed.append(f"❌ {name} (غير موجودة)")

    embed = discord.Embed(title="إدارة الرتب", color=color)
    embed.add_field(name="العضو المستهدف:", value=member.mention, inline=False)
    if success:
        label = "تم إعطاء الرتب:" if action_type == "add" else "تم إزالة الرتب:"
        embed.add_field(name=label, value="\n".join(success), inline=False)
    if failed:
        embed.add_field(name="فشل في:", value="\n".join(failed), inline=False)
    
    await interaction.followup.send(embed=embed)

# ---------------------- أوامر السلاش ----------------------

@bot.tree.command(name="say", description="يجعل البوت يرسل رسالتك داخل نموذج منسق")
@app_commands.describe(message="النص الذي تريد من البوت كتابته")
async def say(interaction: discord.Interaction, message: str):
    embed = discord.Embed(
        description=message,
        color=discord.Color.blue() 
    )
    embed.set_footer(text=f"أرسل بواسطة: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="اعطاء-رتب", description="إعطاء حتى 10 رتب لشخص (افصل بينهم بفاصلة)")
@app_commands.describe(member="العضو المطلوب", roles="أسماء الرتب مفصولة بفاصلة")
async def give_roles(interaction: discord.Interaction, member: discord.Member, roles: str):
    if not interaction.user.guild_permissions.manage_roles:
        return await interaction.response.send_message("❌ لا تملك صلاحية إدارة الرتب", ephemeral=True)
    await process_roles(interaction, member, roles, "add")

@bot.tree.command(name="ازالة-رتب", description="إزالة حتى 10 رتب من شخص (افصل بينهم بفاصلة)")
@app_commands.describe(member="العضو المطلوب", roles="أسماء الرتب مفصولة بفاصلة")
async def remove_roles(interaction: discord.Interaction, member: discord.Member, roles: str):
    if not interaction.user.guild_permissions.manage_roles:
        return await interaction.response.send_message("❌ لا تملك صلاحية إدارة الرتب", ephemeral=True)
    await process_roles(interaction, member, roles, "remove")

@bot.tree.command(name="كشف-رتب", description="عرض قائمة الأعضاء الذين يمتلكون رتبة معينة")
@app_commands.describe(role="اختر الرتبة")
async def check_role(interaction: discord.Interaction, role: discord.Role):
    members = role.members
    embed = discord.Embed(title=f"قائمة رتبة: {role.name}", color=role.color)
    if not members:
        embed.description = "⚠️ لا يوجد أحد يمتلك هذه الرتبة."
    else:
        mentions = [m.mention for m in members[:30]]
        embed.add_field(name=f"العدد الإجمالي: {len(members)}", value="\n".join(mentions))
    await interaction.response.send_message(embed=embed)

# ---------------------- تشغيل البوت بشكل آمن ----------------------
# (DISCORD_TOKEN) سيتم سحب التوكن من إعدادات رندر وليس من الكود
TOKEN = os.getenv('MTQ1NzQ1NjM3MjI3MzY0NzcwNw.GKtdfI.0_kHgbKbH_7Gf0J61rGD0YdWnw6LEAtuS0UC3A')

if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ خطأ: لم يتم العثور على التوكن في إعدادات Render!")

