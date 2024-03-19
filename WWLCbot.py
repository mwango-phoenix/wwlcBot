import discord
from discord.ext import commands, app_commands
from discord.ui import View, TextInput, ui
import json

# Load configuration from a local file
with open('config.json') as f:
    config = json.load(f)

bot = commands.Bot(command_prefix='!', intents=config['intents'])

# Bot token loaded from config file
TOKEN = config['token']

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'We have logged in as {bot.user}')

class Message(ui.Modal, title='Event info'):
    message = ui.TextInput(label='What is the event?', required=True, placeholder="rock climbing (social), OPLC(comp), OLC(fa comp)")
    where = ui.TextInput(label='Where is the event?', required=False)
    time = ui.TextInput(label='Enter start time', required=False, placeholder="4pm")
    date = ui.TextInput(label='Enter date', required=False, placeholder="Mon, Jan 1")

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'Sending notification!', ephemeral=True)
        global props
        props = {"message": self.message.value, "where": self.where.value, "time": self.time.value, "date": self.date.value}

@bot.tree.command(name="notify", description="Send a notification to members")
@app_commands.describe(notif_type="choose notification type")
@app_commands.choices(notif_type=[
    discord.app_commands.Choice(name='events', value=1),
    discord.app_commands.Choice(name='pool', value=2),
    discord.app_commands.Choice(name='fa', value=3)
])
async def notify(interaction: discord.Interaction, notif_type: int):
    execRole = interaction.guild.get_role(config['exec_role_id'])
    if execRole not in interaction.user.roles:
        return

    messageModal = Message()

    await interaction.response.send_modal(messageModal)
    waiting = await messageModal.wait()

    message, where, time, date = props.values()

    if notif_type == 1:
        channel_id = config['channels']['events']
        title = "Social Event"
        role = '🎟️'
        message = f'We will be holding a {message} team social. \n\n 📍**Where:** {where} \n :calendar_spiral: {date} at {time} \n\n Hope to see you there!'
    elif notif_type == 2:
        channel_id = config['channels']['pool']
        title = "Pool Comp"
        role = '🏊'
        message = f'The {message} registration is open. Competition details are as follows: \n 📍**Where:** {where} \n :calendar_spiral: {date} at {time} \n Please let us know if you want to compete!'
    elif notif_type == 3:
        channel_id = config['channels']['fa']
        title = "First Aid Comp"
        role = '🚑'
        message = f'The {message} registration is open. Competition details are as follows: \n 📍**Where:** {where} \n :calendar_spiral: {date} at {time} \n Please let us know if you want to compete!'

    else:
        await interaction.send("Invalid event type. Please use !notify ('events'/'pool'/'fa').")
        return

    channel = interaction.guild.get_channel(channel_id)
    styled_message = f'## [{title} Alert] \n <@&{config["roles"][role]}> \n {message}'
    await channel.send(styled_message)

@bot.event
async def on_raw_reaction_add(payload):
    guild = bot.get_guild(payload.guild_id)
    role = guild.get_role(config['roles'][payload.emoji.name])
    member = payload.member
    await member.add_roles(role)
    print("Success adding role")

@bot.event
async def on_raw_reaction_remove(payload):
    guild = bot.get_guild(payload.guild_id)
    role = guild.get_role(config['roles'][payload.emoji.name])
    print(payload.member)
    member = await guild.fetch_member(payload.user_id)
    await member.remove_roles(role)
    print("Success removing role")

bot.run(TOKEN)
