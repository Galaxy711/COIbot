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
async def send_meeting_announcement(targetTime):
    await client.wait_until_ready()

    channel = client.get_channel(988604861065080892)
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
    await channel.send(f"{happyDay}This {timeOfDay}'s meeting will be at **{meetingPlace}**. "
                       f"be there by {str(int(targetTime.strftime('%I')) + 1)}:{targetTime.strftime('%M')}!\n"
                       f"{sbgOrSg}: **{songPatrol}**\nServing Patrol: **{servingPatrol}**")


def tomorrow(now): return datetime.combine(now.date() + timedelta(days=1), time(0))


async def bg_announcement_loop():
    now = datetime.now()
    while True:
        if now.weekday() == 5:  # Saturday Edge Case
            targetTime = time(7, 0, 0)
            if now.time() > targetTime:  # It's saturday but announcement already missed
                await asyncio.sleep((tomorrow(now) - now).total_seconds())
            else:
                await asyncio.sleep((datetime.combine(now.date(), targetTime) - now).total_seconds())
                await send_meeting_announcement(targetTime)
                await asyncio.sleep((tomorrow(now) - now).total_seconds())
        elif now.weekday() == 6:  # Sunday Edge Case
            targetTime =time(11, 0, 0)
            if now.time() > targetTime:
                await asyncio.sleep((tomorrow(now) - now).total_seconds())
            else:
                await asyncio.sleep((datetime.combine(now.date(), targetTime) - now).total_seconds())
                await send_meeting_announcement(targetTime)
                await asyncio.sleep((tomorrow(now) - now).total_seconds())
        else:  # Should be normal weekdays!
            targetTime = [time(6, 30, 0), time(16, 30, 0)]
            if now.time() > targetTime[1]:  # Missed both announcement times, sleep to next day.
                await asyncio.sleep((tomorrow(now) - now).total_seconds())
            elif now.time() > targetTime[0]:
                await asyncio.sleep((datetime.combine(now.date(), targetTime[1]) - now).total_seconds())
                await send_meeting_announcement(targetTime[1])
                await asyncio.sleep((tomorrow(now) - now).total_seconds())
            else:
                await asyncio.sleep((datetime.combine(now.date(), targetTime[0]) - now).total_seconds())
                await send_meeting_announcement(targetTime[0])
                await asyncio.sleep((datetime.combine(now.date(), targetTime[2]) - now).total_seconds())


@client.command()
async def test(ctx, month, day, hour):
    x = datetime(2022, int(month), int(day), int(hour), 0, 0, 000000)
    await send_meeting_announcement(x)
    # await ctx.send(f"{x.strftime('%Y')}, {x.strftime('%B')}, {x.strftime('%A')} {str(x.day)}, {x.strftime('%I')}:{x.strftime('%M')}{x.strftime('%p')}")


@client.command()
async def changeServers(ctx, *, newPatrol):
    with open('Extra_Serving_Duties.txt', 'w') as file:
        file.write(newPatrol)
    await ctx.send(f"Okay, changed the patrol with extra serving duties to **{newPatrol}**")


@client.event
async def on_ready():
    print(f"{client.user} ready.")


if __name__ == "__main__":
    client.loop.create_task(bg_announcement_loop())
    client.run(TOKEN)
