import os
from dotenv import load_dotenv
load_dotenv()

import typing

import pandas as pd

import discord
from discord.ext import commands
from discord import app_commands

from parsefuncts import *
from strings import *

import gspread
from oauth2client.service_account import ServiceAccountCredentials

class Client(commands.Bot):
    async def on_ready(self):
        print(f'Logged on as {client.user}!')
        try:
            guild = discord.Object(id=os.getenv('GUILD_ID'))
            synced = await self.tree.sync(guild=guild)
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(e)

intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix="!", intents=intents)

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(eval(os.getenv('GOOGLE_API_JSON')), scope)
gc = gspread.authorize(creds)
sh = gc.open_by_key(os.getenv('SHEET_KEY'))
matchSheet = sh.worksheet("data")
guruSheet = sh.worksheet("guruData")
THREAD_COLUMN = 22

GUILD_ID = discord.Object(id=os.getenv('GUILD_ID'))
MATCH_THREADS_ID = discord.Object(id=os.getenv('MATCH_THREADS_ID'))

@client.tree.command(name="getmatch", description="Get info about a specific matchup", guild=GUILD_ID)
@app_commands.describe(
    matchid='Match ID for the match',
    usediscordids='Attempt to use Discord IDs instead of Signatures'
    )
async def getMatch(interaction: discord.Interaction, matchid: str, usediscordids: typing.Literal['Signatures','Discord IDs']='Signatures'):
    await getMatchHelper(interaction, matchid, False, usediscordids=='Discord IDs')

@client.tree.command(name="peekmatch", description="Privately get info about a specific matchup", guild=GUILD_ID)
@app_commands.describe(
    matchid='Match ID for the match',
    usediscordids='Attempt to use Discord IDs instead of Signatures'
    )
async def getMatch(interaction: discord.Interaction, matchid: str, usediscordids: typing.Literal['Signatures','Discord IDs']='Signatures'):
    await getMatchHelper(interaction, matchid, True, usediscordids=='Discord IDs')

async def getMatchHelper(interaction: discord.Interaction, matchid: str, publishResults:bool, usediscordids:bool):    
    podLetter, podNumber, matchNumber, fullName = parseMatchID(matchid)
    if (fullName == -1):
        await interaction.response.send_message(f"Unable to parse `{matchid}` as match ID", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=publishResults)
    matchData = getMatchData(podLetter, podNumber, matchNumber, pd.DataFrame(matchSheet.get_all_records()))
    if (matchData.get("matchExists")):
        if (usediscordids): guruSheet_df = pd.DataFrame(guruSheet.get_all_records())
        else: guruSheet_df = None
        matchSummary = f"{fullName}\n{formatMatch(matchData, usediscordids, guruSheet_df)}"
        await interaction.followup.send(matchSummary)
        return
    await interaction.followup.send(f"Could not find {fullName}")

@client.tree.command(name="summary", description="Give a summary of matches remaining in a pod", guild=GUILD_ID)
@app_commands.describe(
    podid='Pod ID for the pod that will be summarized',
    privacystatus='Force the status of the response',
    onlydiscrepancies='Force only discrepancies or all unfinished matches',
)
async def summary(interaction: discord.Interaction, podid: str, onlydiscrepancies:typing.Literal['Only Discrepancies','Everything']='Everything', privacystatus:typing.Literal['Private','Public']='Public'):
    podLetter, podNumber, fullName = parsePodID(podid)
    if (fullName == -1):
        await interaction.response.send_message(f"Unable to parse `{podid}` as pod ID", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=(privacystatus=='Private'))
    df = pd.DataFrame(matchSheet.get_all_records())
    if (podLetter == "E"):
        podCode = podLetter
    else:
        podCode = podLetter+' '+podNumber
    incdes_df = df[(df['PID'] == podCode) & (df['InDs'] == 1)]
    inc_df = incdes_df[incdes_df['Inc'] == 1]
    totalInc = len(inc_df)
    des_df = incdes_df[incdes_df['Des'] == 1]
    totalDes = len(des_df)
    if(totalInc + totalDes == 0):
        await interaction.followup.send(f"**{fullName}**: {EMOJI_COMPLEAT}")
        return
    totalR = inc_df['RGu'].sum()
    totalU = inc_df['UGu'].sum()
    totalG = inc_df['GGu'].sum()
    headerString = f"**{fullName}**: {totalInc + totalDes} total matches remaining | {totalDes} discrepancies | {totalInc} incompletes ({EMOJI_R} {totalR} | {EMOJI_U} {totalU} | {EMOJI_G} {totalG})"
    await interaction.followup.send(formatSummary(headerString, inc_df, des_df,False,onlydiscrepancies=='Only Discrepancies',"Incompletes"))

@client.tree.command(name="gurusummary", description="Give a summary of matches remaining for a guru", guild=GUILD_ID)
@app_commands.describe(
    guru='Guru signature of the guru to summarize',
    podid='Pod ID for the pod that will be summarized, if you want to restrict',
    privacystatus='Force the status of the response',
    onlydiscrepancies='Force only discrepancies or all unfinished matches',
)
async def guruSummary(interaction: discord.Interaction, guru: str, podid:str=None, onlydiscrepancies:typing.Literal['Only Discrepancies','Everything']='Everything', privacystatus:typing.Literal['Private','Public']='Private'):
    if(podid):
        podLetter, podNumber, fullName = parsePodID(podid)
        if (fullName == -1):
            await interaction.response.send_message(f"Unable to parse `{podid}` as pod ID", ephemeral=True)
            return 
    await interaction.response.defer(ephemeral=(privacystatus=='Private'))
    guruStripped = guru.strip().casefold()
    df = pd.DataFrame(matchSheet.get_all_records())
    if(podid): 
        if (podLetter == "E"):
            podCode = podLetter
        else:
            podCode = podLetter+' '+podNumber
        df = df[df['PID'] == podCode]
        inPod = f" in {podCode}"
    else: inPod = ""
    incdes_df = df[(df['InDs'] == 1) & ( ( df.RGuru.str.strip().str.casefold() == guruStripped ) | ( df.UGuru.str.strip().str.casefold() == guruStripped ) | ( df.GGuru.str.strip().str.casefold() == guruStripped ) )]
    inc_df = incdes_df[incdes_df['Inc'] == 1]
    totalInc = len(inc_df)
    unf_df = inc_df[((inc_df['RRs'] == "") & (inc_df.RGuru.str.strip().str.casefold() == guruStripped)) | ((inc_df['URs'] == "") & (inc_df.UGuru.str.strip().str.casefold() == guruStripped)) | ((inc_df['GRs'] == "") & (inc_df.GGuru.str.strip().str.casefold() == guruStripped))]
    totalUnf = len(unf_df)
    des_df = incdes_df[incdes_df['Des'] == 1]
    totalDes = len(des_df)
    if(totalInc + totalDes == 0):
        await interaction.followup.send(f"{guru} is {EMOJI_COMPLEAT}{inPod}")
        return
    headerString = f"{totalInc + totalDes} matches remaining for {guru}{inPod} | {totalDes} discrepancies | {totalUnf} unfilled | {totalInc-totalUnf} incompletes by other gurus"
    await interaction.followup.send(formatSummary(headerString, unf_df, des_df,True,onlydiscrepancies=='Only Descrepancies',"Unfilled Matches"), ephemeral=True)

@client.tree.command(name="summaryall", description="Give a summary of matches remaining in all pods", guild=GUILD_ID)
@app_commands.describe(
    privacystatus='Force the status of the response',
    onlydiscrepancies='Force only discrepancies or all unfinished matches',
)
async def summaryAll(interaction: discord.Interaction, onlydiscrepancies:typing.Literal['Only Descrepancies','Everything']='Everything', privacystatus:typing.Literal['Private','Public']='Public'):
    await interaction.response.defer(ephemeral=(privacystatus=='Private'))
    df = pd.DataFrame(matchSheet.get_all_records())
    incdes_df = df[df['InDs'] == 1]
    inc_df = incdes_df[incdes_df['Inc'] == 1]
    totalInc = len(inc_df)
    des_df = incdes_df[incdes_df['Des'] == 1]
    totalDes = len(des_df)
    if(totalInc + totalDes == 0):
        await interaction.followup.send(f"**All Pods**: {EMOJI_COMPLEAT}")
        return
    headerString = f"**All Pods**: {totalInc + totalDes} matches remaining | {totalDes} discrepancies | {totalInc} incompletes"
    await interaction.followup.send(formatSummary(headerString, inc_df, des_df,True,onlydiscrepancies=='Only Descrepancies',"Incompletes"))

@client.tree.command(name="inverseerrors", description="Check all pods for inverse errors", guild=GUILD_ID)
@app_commands.describe(
    privacystatus='Force the status of the response',
)
async def inverseErrors(interaction: discord.Interaction, privacystatus:typing.Literal['Private','Public']='Public'):
    await interaction.response.defer(ephemeral=(privacystatus=='Private'))
    df = pd.DataFrame(matchSheet.get_all_records())
    error_df = df[df['IVRs'] == 'Error Suspected']
    total = len(error_df)
    if(total == 0):
        await interaction.followup.send(f"No suspected errors")
        return
    headerString = f"{total} suspected errors"
    await interaction.followup.send(formatSummary(headerString, error_df, error_df,True,True,""))

@client.tree.command(name="tlink", description="Link a thread to a match", guild=GUILD_ID)
@app_commands.describe(matchid='Match ID for the match to be linked')
async def tLink(interaction: discord.Interaction, matchid: str):
    try:
        validThread = (interaction.channel.parent_id == MATCH_THREADS_ID.id)
    except:
        validThread = False
    if (not validThread):
        await interaction.response.send_message("tlink can only be used in a thread in guru-match-help", ephemeral=True)
        return
    else:
        podLetter, podNumber, matchNumber, fullName = parseMatchID(matchid)
        if (fullName == -1):
            await interaction.response.send_message(f"Unable to parse `{matchid}` as match ID", ephemeral=True)
            return
        await interaction.response.defer()
        matchData = getMatchData(podLetter, podNumber, matchNumber, pd.DataFrame(matchSheet.get_all_records()))
        if (matchData.get("matchExists")):
            if (not matchData["linkedID"] == "0"):
                await interaction.followup.send(f"{fullName} already linked to <#{matchData['linkedID']}>")
            else:
                matchSheet.update_cell(matchData["rowNumber"], THREAD_COLUMN, str(interaction.channel_id))
                await interaction.followup.send(f"Link created from {fullName} to <#{interaction.channel_id}>")
            return
        await interaction.followup.send(f"Could not find {fullName}")

@client.tree.command(name="writeup", description="Combines getmatch, pingmatch, and tlink", guild=GUILD_ID)
@app_commands.describe(matchid='Match ID for the match to be written up')
async def writeup(interaction: discord.Interaction, matchid: str):
    try:
        validThread = (interaction.channel.parent_id == MATCH_THREADS_ID.id)
    except:
        validThread = False
    if (not validThread):
        await interaction.response.send_message("writeup can only be used in a thread in guru-match-help", ephemeral=True)
        return
    else:
        podLetter, podNumber, matchNumber, fullName = parseMatchID(matchid)
        if (fullName == -1):
            await interaction.response.send_message(f"Unable to parse `{matchid}` as match ID", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        matchData = getMatchData(podLetter, podNumber, matchNumber, pd.DataFrame(matchSheet.get_all_records()))
        if (matchData.get("matchExists")):
            if (not matchData["linkedID"] == "0"):
                await interaction.followup.send(f"{fullName} already linked to <#{matchData['linkedID']}>")
            else:
                matchSheet.update_cell(matchData["rowNumber"], THREAD_COLUMN, str(interaction.channel_id))
                responseString = f"Link created from {fullName} to <#{interaction.channel_id}>"
                responseString += f"\n{formatMatch(matchData, True, pd.DataFrame(guruSheet.get_all_records()))}"
                await interaction.channel.send(responseString)
                await interaction.delete_original_response()
            return
        await interaction.followup.send(f"Could not find {fullName}")

@client.tree.command(name="ulink", description="Remove all linked threads threads for a match", guild=GUILD_ID)
@app_commands.describe(matchid='Match ID for the match to be unlinked')
async def ulink(interaction: discord.Interaction, matchid: str):
    podLetter, podNumber, matchNumber, fullName = parseMatchID(matchid)
    if (fullName == -1):
        await interaction.response.send_message(f"Unable to parse `{matchid}` as match ID", ephemeral=True)
        return
    await interaction.response.defer()
    matchData = getMatchData(podLetter, podNumber, matchNumber, pd.DataFrame(matchSheet.get_all_records()))
    if (matchData.get("matchExists")):
        if (matchData["linkedID"] == "0"):
            await interaction.followup.send(f"{fullName} is not linked to any thread", ephemeral=True)
        else:
            matchSheet.update_cell(matchData["rowNumber"], THREAD_COLUMN, "0")
            await interaction.followup.send(f"Link removed from {fullName} to <#{matchData['linkedID']}>")
        return
    await interaction.followup.send(f"Could not find {fullName}", ephemeral=True)

@client.tree.command(name="pingmatch", description="Ping all gurus for a specific match", guild=GUILD_ID)
@app_commands.describe(matchid='Match ID for the match to be pinged')
async def pingMatch(interaction: discord.Interaction, matchid: str):
    podLetter, podNumber, matchNumber, fullName = parseMatchID(matchid)
    if (fullName == -1):
        await interaction.response.send_message(f"Unable to parse `{matchid}` as match ID", ephemeral=True)
        return
    await interaction.response.defer(ephemeral=True)
    matchData = getMatchData(podLetter, podNumber, matchNumber, pd.DataFrame(matchSheet.get_all_records()))
    if (matchData.get("matchExists")):
        guru_df = pd.DataFrame(guruSheet.get_all_records())
        pingString = f"{fullName}"
        pingString += f"\n> {EMOJI_R} {getGuruString(matchData.get('guruR'),True,guru_df)}"
        pingString += f"\n> {EMOJI_U} {getGuruString(matchData.get('guruU'),True,guru_df)}"
        pingString += f"\n> {EMOJI_G} {getGuruString(matchData.get('guruG'),True,guru_df)}"
        await interaction.channel.send(f"{pingString}")
        await interaction.delete_original_response()
        return
    await interaction.followup.send(f"Could not find {fullName}", ephemeral=True)

@client.tree.command(name="registerguru", description="Connect your discord to your guru signature", guild=GUILD_ID)
@app_commands.describe(signature='Guru signature to register to your account')
async def registerGuru(interaction: discord.Interaction, signature: str):
    await interaction.response.defer()
    savedSignature = signature.strip().casefold()
    if (len(savedSignature)==0):
        await interaction.followup.send(f"Could not parse {signature}")
        return
    if (len(savedSignature)>128):
        await interaction.followup.send(f"Signature is too long", ephemeral=True)
        return
    cell = guruSheet.find(savedSignature)
    if (cell):
        registedID = guruSheet.cell(cell.row, 2).value
        await interaction.followup.send(f"{signature} has already been registered to <@{registedID}>")
    else:
        emptyCell = guruSheet.find("###")
        if(emptyCell):
            guruSheet.update_cell(emptyCell.row, 1, savedSignature)
            guruSheet.update_cell(emptyCell.row, 2, str(interaction.user.id)) 
            await interaction.followup.send(f"Registered  <@{interaction.user.id}> to {signature}")
        else:
            await interaction.followup.send("Guru registry full")

@client.tree.command(name="unregisterguru", description="Remove your discord from a guru signature", guild=GUILD_ID)
@app_commands.describe(signature='Guru signature to unregister from your account')
async def unregisterGuru(interaction: discord.Interaction, signature: str):
    await interaction.response.defer()
    savedSignature = signature.strip().casefold()
    if (len(savedSignature)==0):
        await interaction.followup.send(f"Could not parse {signature}", ephemeral=True)
        return
    if (len(savedSignature)>128):
        await interaction.followup.send(f"Signature is too long", ephemeral=True)
        return
    cell = guruSheet.find(savedSignature)
    if (cell):
        registedID = guruSheet.cell(cell.row, 2).value
        if (str(registedID) == str(interaction.user.id)):
            guruSheet.update_cell(cell.row, 1, '###')
            guruSheet.update_cell(cell.row, 2, '0')
            await interaction.followup.send(f"Unregistered  <@{interaction.user.id}> from {signature}")
        else:
            await interaction.followup.send(f"You can only unregister your own signatures.")
    else:
        await interaction.followup.send(f"{signature} has not been registered")

@client.tree.command(name="discrepancyurl", description="Gives URL to Guru Match Hub", guild=GUILD_ID)
async def discrepancyUrl(interaction: discord.Interaction):
    await interaction.response.send_message(f"https://docs.google.com/spreadsheets/d/13EZdVCNI6yZMzAqlVC_JvDm0EoFH7BEFPBJ_rRAifp8/edit?usp=sharing", ephemeral=True)

@client.tree.command(name="help", description="Information about Memknight commands", guild=GUILD_ID)
@app_commands.describe(
    command='Command to get info about'
    )
async def getMatch(interaction: discord.Interaction, command:typing.Literal['getmatch', 'peekmatch', 'pingmatch', 'writeup', 'summary', 'summaryall', 'gurusummary', 'tlink', 'ulink', 'registerguru', 'unregisterguru', 'discrepancyurl', 'Match IDs']=None):
    await interaction.response.send_message(HELPTEXT.get(command,DEFAULTHELPTEXT), ephemeral=True)

client.run(os.getenv('TOKEN'))