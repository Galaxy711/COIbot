import asyncio
import discord
from discord.ext import commands
from Bot_Globals import *
from datetime import *

client = commands.Bot(command_prefix=PREFIX)


# Functions to determine contents of the meeting reminders
def determine_meeting_place(now):
    if now.hour > 12 and (now.weekday() == 2 or now.weekday() == 6):  # Edge Cases! (Afternoons)
        if now.weekday() == 2:
            return "Ecology Lodge"
        if now.weekday() == 6:
            return "Handicraft Shelter"
    else:
        places = ["First Aid", "Activity Building", "Dining Hall", "Handicraft Shelter", "First Aid", "First Aid",
                  "Activity Building"]
        return places[now.weekday()]


def determine_song_patrol(now):
    if now.hour < 12:  # AM
        patrols = ["Shooting Sports", "Stem", "Ecology", "Aquatics", "Scoutcraft", "None", "None"]
    else:  # Should be PM
        patrols = ["Civ Dev", "Handicraft", "None", "Trading Post", "Pathfinder", "None", "Aquatics"]
    return patrols[now.weekday()]


def determine_serving_patrol(now):
    with open('Extra_Serving_Duties.txt', 'r') as file:
        xtraDutiesPatrol = file.readline()
    patrols = ["Pep Nips", "Funky Monkeys", xtraDutiesPatrol, "The Ladybugs", "Sssquandypost", "None", xtraDutiesPatrol]
    return patrols[now.weekday()]


# Formulate and send the meeting announcement
async def send_meeting_announcement():
    await client.wait_until_ready()

    # channel = client.get_channel(POINT_CHANNEL)
    channel = client.get_channel(POINT_CHANNEL)
    now = datetime.now()

    meetingPlace = determine_meeting_place(now)
    songPatrol = determine_song_patrol(now)
    servingPatrol = determine_serving_patrol(now)

    if now.hour < 12:
        timeOfDay = "morning"
        sbgOrSg = "Song, Big Idea, and Grace"
        happyDay = f"Happy {now.strftime('%A')}! "
    else:
        timeOfDay = "afternoon"
        sbgOrSg = "Song and Grace"
        happyDay = ""

    # Determine actual meeting time
    if now.weekday() == 5 or (now.weekday() == 6 and now.hour < 12):
        actualMeetingTime = "7:00 AM" if now.weekday() == 5 else "11:00 AM"
    else:
        actualMeetingTime = "7:30 AM" if now.hour < 12 else "5:30 PM"

    await channel.send(f"{happyDay}This {timeOfDay}'s meeting will be at **{meetingPlace}**. "
                       f"Be there by **{actualMeetingTime}**!\n"
                       f"{sbgOrSg}: **{songPatrol}**\nServing Patrol: **{servingPatrol}**\n@everyone")


def tomorrow(now): return datetime.combine(now.date() + timedelta(days=1), time(0))


async def bg_announcement_loop():
    while True:
        now = datetime.now()
        if now.weekday() == 5:  # Saturday Edge Case
            targetTime = time(6, 15, 0)
            if now.time() > targetTime:  # It's saturday but announcement already missed
                await asyncio.sleep((tomorrow(now) - now).total_seconds())
            else:
                await asyncio.sleep((datetime.combine(now.date(), targetTime) - now).total_seconds())
                await send_meeting_announcement()
                await asyncio.sleep((tomorrow(now) - now).total_seconds())
        elif now.weekday() == 6 and now.hour < 12:  # Sunday Edge Case
            targetTime = time(10, 15, 0)
            if now.time() > targetTime:
                await asyncio.sleep((tomorrow(now) - now).total_seconds())
            else:
                await asyncio.sleep((datetime.combine(now.date(), targetTime) - now).total_seconds())
                await send_meeting_announcement()
                await asyncio.sleep(timedelta(hours=3, minutes=45).total_seconds())
        else:  # Should be normal weekdays!
            targetTime = [time(6, 45, 0), time(16, 45, 0)]
            if now.time() > targetTime[1]:  # Missed both announcement times, sleep to next day.
                await asyncio.sleep((tomorrow(now) - now).total_seconds())
            elif now.time() > targetTime[0]:
                await asyncio.sleep((datetime.combine(now.date(), targetTime[1]) - now).total_seconds())
                await send_meeting_announcement()  # Actual meeting time is at 5:30pm
                await asyncio.sleep((tomorrow(now) - now).total_seconds())
            else:
                await asyncio.sleep((datetime.combine(now.date(), targetTime[0]) - now).total_seconds())
                await send_meeting_announcement()  # Actual meeting time is at 7:30am
                await asyncio.sleep((datetime.combine(now.date(), targetTime[1]) - now).total_seconds() - 30)


@client.command()
async def manual(ctx):
    await send_meeting_announcement()


@client.command()
async def changeServers(ctx, *, newPatrol):
    if newPatrol not in ["The Ladybugs", "Sssquandypost", "Pep Nips", "Funky Monkeys"]:
        await ctx.send("THAT IS NOT A PATROL!!!!")
    else:
        with open('Extra_Serving_Duties.txt', 'w') as file:
            file.write(newPatrol)
        await ctx.send(f"Okay, changed the patrol with extra serving duties to **{newPatrol}**")


@client.command()
async def test(ctx):
    await ctx.send("Up and working!")


@client.command()
async def pogoTeam(ctx, arg):
    await client.wait_until_ready()
    mysticRole = ctx.guild.get_role(990955798211473428)
    valorRole = ctx.guild.get_role(990956081935155200)
    instinctRole = ctx.guild.get_role(990956366766166056)

    userRoles = ctx.author.roles

    if mysticRole in userRoles:
        await ctx.author.remove_roles(mysticRole)
    if valorRole in userRoles:
        await ctx.author.remove_roles(valorRole)
    if instinctRole in userRoles:
        await ctx.author.remove_roles(instinctRole)

    if arg.lower() == "mystic" or arg.lower() == "blue":
        await ctx.author.add_roles(mysticRole)
        await ctx.send("You now have the team **Mystic** role")
    elif arg.lower() == "valor" or arg.lower() == "red":
        await ctx.author.add_roles(valorRole)
        await ctx.send("You now have the team **Valor** role")
    elif arg.lower() == "instinct" or arg.lower() == "yellow":
        await ctx.author.add_roles(instinctRole)
        await ctx.send("You now have the team **Instinct** role")
    else:
        await ctx.send("Not a valid pokemon go team!")


@client.event
async def on_ready():
    print(f"{client.user} ready.")


if __name__ == "__main__":
    client.loop.create_task(bg_announcement_loop())
    client.run(TOKEN)
