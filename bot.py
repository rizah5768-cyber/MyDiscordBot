import discord
from discord import app_commands
from discord.ext import commands
import os
from flask import Flask
from threading import Thread
from typing import Optional

# ---------------------- نظام البقاء حياً (Flask) لـ Render ----------------------
app = Flask('')

@app.route('/')
def home():
    return "البوت يعمل بنجاح 24/7!"

def run_flask():
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

# ---------------------- معالج الأوامر التلقائي وإرسال اللوق بعد اكتمال الأمر ----------------------
from typing import Union
# تأكد من استيراد discord و app_commands في بداية ملفك

@bot.event
async def on_app_command_completion(interaction: discord.Interaction, command: Union[app_commands.Command, app_commands.ContextMenu]):
    # إذا كان الأمر هو 'say' نتجاهل تسجيله تماماً
    if command.name == 'say':
        return

    if bot.log_channel_id:
        log_channel = bot.get_channel(bot.log_channel_id)
        if log_channel:
            # تجهيز نص السجل بصيغة رسالة عادية وبدون ذكر المستخدم
            # استخدمنا صيغة الوقت <t:...:F> لتبدو مرتبة في ديسكورد
            log_message = f"📝 **سجل استخدام الأوامر**\n**الأمر:** `/{command.name}`\n**القناة:** {interaction.channel.mention}\n**الوقت:** <t:{int(interaction.created_at.timestamp())}:F>"
            
            # إرسال رسالة نصية عادية (ليست Embed)
            await log_channel.send(log_message)






from datetime import datetime
# تأكد من إضافة zoneinfo في الأعلى إذا كنت تستخدم التوقيت المحلي
# من zoneinfo import ZoneInfo 

@bot.tree.command(name="استدعاء", description="إرسال طلب استدعاء رسمي إلى عضو معين في الخاص.")
@app_commands.describe(العضو="الشخص المستدعى", السبب="سبب الاستدعاء")
async def summon_slash(interaction: discord.Interaction, العضو: discord.Member, السبب: str):
    # استخدام التوقيت الحالي لضمان الدقة
    # إذا كنت تريد توقيتاً عالمياً موحداً (UTC)، استخدم datetime.utcnow().strftime(...)
    current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M") 
    
    embed = discord.Embed(
        title="🔴 إشعار رسمي (استدعاء)",
        description=f"تم استدعاؤك من قبل الإدارة بموجب هذا الإشعار.",
        color=0x992d22
    )
    embed.add_field(name="🔹 الحالة المطلوبة", value="مطلوب حضورك فوراً", inline=False)
    embed.add_field(name="📝 سبب الاستدعاء", value=السبب, inline=False)
    embed.add_field(name="📅 التاريخ :", value=current_time_str, inline=False) 
    # تم حذف سطر embed.set_thumbnail(...) لحل مشكلة الرابط
    embed.set_footer(text="في حال عدم الحضور سيتم اتخاذ الإجراءات اللازمة.")

    try:
        await العضو.send(embed=embed)
        # تأكيد إرسال الرسالة في القناة الأصلية برسالة مخفية
        await interaction.response.send_message(f"✅ تم إرسال رسالة الاستدعاء إلى {العضو.mention} في الخاص.", ephemeral=True)
    except discord.Forbidden:
        # إذا كان الخاص مغلقاً
        await interaction.response.send_message(f"❌ تعذر إرسال رسالة في الخاص للعضو {العضو.mention}. تم إرسالها هنا بدلاً من ذلك:", embed=embed)






# ---------------------- أوامر السلاش (Slash Commands) ----------------------

@bot.tree.command(name="say", description="إرسال رسالة منسقة عبر البوت (مجهول)")
@app_commands.describe(message="النص الذي تريد من البوت كتابته")
async def say(interaction: discord.Interaction, message: str):
    # تم تكبير النموذج وإضافة عنوان ووصف ليكون أجمل
    embed = discord.Embed(
        title="📣 رسالة عامة",
        description=f"```\n{message}\n```", # وضع الرسالة داخل Code Block لترتيبها
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="اعطاء-رتب", description="إعطاء حتى 10 رتب في حقول منفصلة")
@app_commands.describe(
    member="العضو المستهدف",
    role1="الرتبة 1", role2="الرتبة 2", role3="الرتبة 3", role4="الرتبة 4", role5="الرتبة 5",
    role6="الرتبة 6", role7="الرتبة 7", role8="الرتبة 8", role9="الرتبة 9", role10="الرتبة 10"
)
async def give_roles(
    interaction: discord.Interaction,
    member: discord.Member,
    role1: discord.Role, role2: Optional[discord.Role] = None, role3: Optional[discord.Role] = None,
    role4: Optional[discord.Role] = None, role5: Optional[discord.Role] = None, role6: Optional[discord.Role] = None,
    role7: Optional[discord.Role] = None, role8: Optional[discord.Role] = None, role9: Optional[discord.Role] = None,
    role10: Optional[discord.Role] = None
):
    if not interaction.user.guild_permissions.manage_roles:
        return await interaction.response.send_message("❌ ليس لديك صلاحية إدارة الرتب", ephemeral=True)
    
    await interaction.response.defer()
    roles_to_process = [role1, role2, role3, role4, role5, role6, role7, role8, role9, role10]
    success, failed = [], []

    for role in roles_to_process:
        if role is None: continue
        try:
            await member.add_roles(role)
            success.append(f"✅ {role.name}")
        except:
            failed.append(f"❌ {role.name} (نقص صلاحيات)")

    embed = discord.Embed(title="نموذج اعطاء الرتب", color=discord.Color.green())
    embed.add_field(name="العضو المستهدف:", value=member.mention, inline=False)
    if success: embed.add_field(name="تم إعطاء الرتب التالية:", value="\n".join(success), inline=False)
    if failed: embed.add_field(name="فشل في الرتب التالية:", value="\n".join(failed), inline=False)
    await interaction.followup.send(embed=embed)


@bot.tree.command(name="ازالة-رتب", description="إزالة حتى 10 رتب في حقول منفصلة")
@app_commands.describe(
    member="العضو المستهدف",
    role1="الرتبة 1", role2="الرتبة 2", role3="الرتبة 3", role4="الرتبة 4", role5="الرتبة 5",
    role6="الرتبة 6", role7="الرتبة 7", role8="الرتبة 8", role9="الرتبة 9", role10="الرتبة 10"
)
async def remove_roles(
    interaction: discord.Interaction,
    member: discord.Member,
    role1: discord.Role, role2: Optional[discord.Role] = None, role3: Optional[discord.Role] = None,
    role4: Optional[discord.Role] = None, role5: Optional[discord.Role] = None, role6: Optional[discord.Role] = None,
    role7: Optional[discord.Role] = None, role8: Optional[discord.Role] = None, role9: Optional[discord.Role] = None,
    role10: Optional[discord.Role] = None
):
    if not interaction.user.guild_permissions.manage_roles:
        return await interaction.response.send_message("❌ ليس لديك صلاحية إدارة الرتب", ephemeral=True)
    
    await interaction.response.defer()
    roles_to_process = [role1, role2, role3, role4, role5, role6, role7, role8, role9, role10]
    success, failed = [], []

    for role in roles_to_process:
        if role is None: continue
        try:
            await member.remove_roles(role)
            success.append(f"✅ {role.name}")
        except:
            failed.append(f"❌ {role.name} (نقص صلاحيات)")

    embed = discord.Embed(title="نموذج ازالة الرتب", color=discord.Color.red())
    embed.add_field(name="العضو المستهدف:", value=member.mention, inline=False)
    if success: embed.add_field(name="تم إزالة الرتب التالية:", value="\n".join(success), inline=False)
    if failed: embed.add_field(name="فشل في الرتب التالية:", value="\n".join(failed), inline=False)
    await interaction.followup.send(embed=embed)


@bot.tree.command(name="كشف-رتبة", description="يظهر قائمة بأسماء الأعضاء الذين يحملون هذه الرتبة في نموذج كبير ومرتب")
@app_commands.describe(role="اختر الرتبة المراد كشف أعضائها")
async def list_role_members(interaction: discord.Interaction, role: discord.Role):
    await interaction.response.defer()
    
    members = role.members
    if not members:
        embed = discord.Embed(title=f"قائمة أعضاء رتبة: {role.name}", description=f"⚠️ لا يوجد أعضاء يحملون رتبة {role.mention}", color=discord.Color.orange())
        return await interaction.followup.send(embed=embed)

    # تنسيق راقي: عرض قائمة الأعضاء في حقل منفصل كبير ومرتب
    # استخدام تنسيق الأعمدة الثلاثة بشكل تلقائي من ديسكورد
    member_list_formatted = [m.mention for m in members]
    
    embed = discord.Embed(
        title=f"📊 تقرير مفصل لرتبة: {role.name}",
        description=f"إجمالي عدد الأعضاء الحاصلين عليها: **{len(members)}** عضو",
        color=role.color if role.color.value != 0 else discord.Color.blue()
    )
    # إضافة حقل منفصل للأعضاء أنفسهم، ديسكورد يرتبها في أعمدة تلقائياً
    if member_list_formatted:
        embed.add_field(name="قائمة الأعضاء:", value="\n".join(member_list_formatted), inline=False)
    
    embed.set_footer(text=f"طلب بواسطة: {interaction.user.display_name}")
    
    await interaction.followup.send(embed=embed)

from flask import Flask
from threading import Thread

# 1. تعريف التطبيق
app = Flask('')

@app.route('/')
def home():
    return "I am alive"

# 2. دالة التشغيل
def run():
    app.run(host='0.0.0.0', port=10000)

# 3. دالة الـ Ping
def keep_alive():
    t = Thread(target=run)
    t.start()

# ---------------------- تشغيل البوت ----------------------
if __name__ == "__main__":
    keep_alive()
    TOKEN = os.getenv('DISCORD_TOKEN')
    
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ خطأ: التوكن (DISCORD_TOKEN) غير موجود في إعدادات البيئة!")










