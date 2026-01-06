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
        self.log_channel_id = None # لتخزين آيدي قناة اللوق

    async def setup_hook(self):
        # مزامنة أوامر السلاش فوراً عند التشغيل
        await self.tree.sync()
        print(f"✅ تم تحديث ومزامنة جميع الأوامر بنجاح!")
    
    async def on_ready(self):
        # البحث عن قناة اللوق بالاسم عند تشغيل البوت
        if self.log_channel_id is None:
            for guild in self.guilds:
                for channel in guild.channels:
                    # يفضل استخدام الـ ID بدلاً من الاسم لضمان الموثوقية
                    if channel.name == "ʳⁱʸᵃᵈʰ・ᵗᵒʷⁿ｜🛠️」لـوق・اونـر":
                        self.log_channel_id = channel.id
                        print(f"تم العثور على قناة اللوق: {channel.name}")
                        break
                if self.log_channel_id: break

        print(f'--- {self.user.name} يعمل الآن ---')

bot = MyBot()

# ---------------------- معالج الأوامر التلقائي وإرسال اللوق ----------------------
@bot.event
async def on_interaction(interaction: discord.Interaction):
    # نتأكد أن التفاعل هو أمر سلاش
    if interaction.type == discord.InteractionType.application_command:
        # إذا وجدنا القناة، نرسل اللوق
        if bot.log_channel_id:
            log_channel = bot.get_channel(bot.log_channel_id)
            if log_channel:
                log_embed = discord.Embed(
                    title="سجل استخدام الأوامر 📝",
                    description=f"**الأمر:** `/{interaction.command.name}`\n**المستخدم:** {interaction.user.mention}\n**القناة:** {interaction.channel.mention}",
                    color=discord.Color.gold()
                )
                await log_channel.send(embed=log_embed)
        
    # نضمن أن الأوامر الفعلية تشتغل
    await bot.process_application_commands(interaction)


# ---------------------- دالة معالجة الرتب المجمعة (تستخدم في الإعطاء والإزالة) ----------------------
async def process_multi_roles(interaction, member, roles_input, action_type):
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

    embed = discord.Embed(title="نموذج إدارة الرتب المجمعة", color=color)
    embed.add_field(name="العضو المستهدف:", value=member.mention, inline=False)
    if success:
        label = "تم إعطاء الرتب التالية:" if action_type == "add" else "تم إزالة الرتب التالية:"
        embed.add_field(name=label, value="\n".join(success), inline=False)
    if failed:
        embed.add_field(name="فشل في الرتب التالية:", value="\n".join(failed), inline=False)
    
    await interaction.followup.send(embed=embed)


# ---------------------- أوامر السلاش (Slash Commands) ----------------------

@bot.tree.command(name="say", description="إرسال رسالة منسقة عبر البوت (مجهول)")
@app_commands.describe(message="النص الذي تريد من البوت كتابته")
async def say(interaction: discord.Interaction, message: str):
    embed = discord.Embed(description=message, color=discord.Color.blue())
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="اعطاء-رتب", description="إعطاء حتى 10 رتب دفعة واحدة (افصل بينهم بفاصلة)")
@app_commands.describe(member="العضو المستهدف", roles="أسماء الرتب مفصولة بفاصلة (مثال: رتبة1, رتبة2)")
async def give_roles(interaction: discord.Interaction, member: discord.Member, roles: str):
    if not interaction.user.guild_permissions.manage_roles:
        return await interaction.response.send_message("❌ لا تملك صلاحية إدارة الرتب", ephemeral=True)
    await process_multi_roles(interaction, member, roles, "add")

@bot.tree.command(name="ازالة-رتب", description="إزالة حتى 10 رتب دفعة واحدة (افصل بينهم بفاصلة)")
@app_commands.describe(member="العضو المستهدف", roles="أسماء الرتب مفصولة بفاصلة (مثال: رتبة1, رتبة2)")
async def remove_roles(interaction: discord.Interaction, member: discord.Member, roles: str):
    if not interaction.user.guild_permissions.manage_roles:
        return await interaction.response.send_message("❌ لا تملك صلاحية إدارة الرتب", ephemeral=True)
    await process_multi_roles(interaction, member, roles, "remove")

@bot.tree.command(name="كشف-رتبة", description="يظهر قائمة بأسماء الأعضاء الذين يحملون هذه الرتبة في نموذج كبير")
@app_commands.describe(role="اختر الرتبة المراد كشف أعضائها")
async def list_role_members(interaction: discord.Interaction, role: discord.Role):
    await interaction.response.defer()
    
    members = role.members
    if not members:
        embed = discord.Embed(title=f"قائمة أعضاء رتبة: {role.name}", description=f"⚠️ لا يوجد أعضاء يحملون رتبة {role.mention}", color=discord.Color.orange())
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
