import re
import pandas as pd
from strings import *

def parseMatchID(input: str):
    """
    Parses strings as one of several common Match id formats.

    Args:
        input: The string to parse.

    Returns:
        Returns a 4-tuple. If the match fails to parse, all returns will be -1
            podLetter: The one-letter code for the pod type
            podNumber: The roman neumeral of the pod number. The one Exemplar pod has pod number 0.
            matchNumber: The decimal match number
            fullName: A string name of the match using the full name of the pod type, a roman numeral if not Exemplar, and the decimal match number
    """
    chunks = input.split()
    match len(chunks):
        case 3:
            matchNumber = chunks[2]
        case 2:
            matchNumber = chunks[1]
        case 1:
            try:
                matchNumber = re.search(r"(\d+)$", input).group()
            except:
                return -1, -1, -1, -1
        case _:
            return -1, -1, -1, -1
    podID = input[:input.rfind(matchNumber)].strip()
    podLetter, podNumber, fullName = parsePodID(podID)
    if (podLetter == -1):
        return -1, -1, -1, -1
    return podLetter, podNumber, matchNumber, fullName+" "+matchNumber

def parsePodID(input: str):
    """
    Parses strings as one of several common Pod id formats.

    Args:
        input: The string to parse.

    Returns:
        Returns a 3-tuple. If the match fails to parse, all returns will be -1
            podLetter: The one-letter code for the pod type
            podNumber: The roman neumeral of the pod number. The one Exemplar pod has pod number 0.
            fullName: A string name of the match using the full name of the pod type and a roman numeral if not Exemplar
    """
    if (input.upper() == "E" or input.upper() == "EXEMPLAR"or input.upper() == "EX"):
        return "E", "0", "Exemplar"
    chunks = input.split()
    match len(chunks):
        case 2:
            rawPodName = chunks[0].upper()
            rawPodNumber = chunks[1].upper()
        case 1:
            rawPodName = input[:1].upper()
            rawPodNumber = input[1:].upper()
        case _:
            return -1, -1, -1
    if (rawPodNumber.isnumeric()):
        podNumber = NUMBER2ROMAN.get(rawPodNumber, -1)
    else:
        podNumber = rawPodNumber if rawPodNumber in PODNUMBERS else -1
    if (podNumber == -1):
        return -1, -1, -1
    if (len(rawPodName) == 1):
        podLetter = rawPodName if rawPodName in PODLETTERS else -1
    else:
        podLetter = NAME2LETTER.get(rawPodName, -1)
    if (podLetter == -1):
        return -1, -1, -1
    if (podLetter == "E"):
        fullName = LETTER2NAME.get(podLetter)    
    else:
        fullName = LETTER2NAME.get(podLetter)+" "+podNumber    
    return podLetter, podNumber, fullName

def formatMatch(matchData: dict, ping: bool, allGurus: pd.DataFrame=None):
    """
    Formats a match's data into a discord mesage summary

    Args:
        matchData: A dictionary of match data, as returned by getMatchData
        ping: A boolean that if true will attemp to turn any signatures into pings of the guru registered to that signature
        allGurus: A DataFrame used to match guru signatures to discord IDs

    Returns:
        A string formated to be a discord message as used by /getmatch and others.
    """
    if (not matchData["matchExists"]): return
    guruR = matchData["guruR"] if matchData["guruR"] else "**None**"
    guruU = matchData["guruU"] if matchData["guruU"] else "**None**"
    guruG = matchData["guruG"] if matchData["guruG"] else "**None**"
    matchSummary = f"> P1 - {matchData['deckA']}\n> P2 - {matchData['deckB']}"
    matchSummary += f"\n> {EMOJI_R} `{matchData['resultR']}` {getGuruString(matchData.get('guruR'),ping,allGurus)}"
    matchSummary += f"\n> {EMOJI_U} `{matchData['resultU']}` {getGuruString(matchData.get('guruU'),ping,allGurus)}"
    matchSummary += f"\n> {EMOJI_G} `{matchData['resultG']}` {getGuruString(matchData.get('guruG'),ping,allGurus)}"
    if (not matchData["linkedID"] == "0"):
        matchSummary = matchSummary + f"\n> \n> Thread - <#{matchData['linkedID']}>"
    matchSummary += f"\n> \n> Inverse - `{matchData['inverseEmoji']}` {matchData['inverseID']}"
    return matchSummary

def getMatchData(podLetter: str, podNumber: str, matchNumber: str, allMatches: pd.DataFrame):
    """
    Pulls match data from a specified match up from the provided match data DatFrame

    Args:
        podLetter: The one-letter code for the pod type of the match to pull
        podNumber: The roman neumeral pod number, or 0-if the pod is Exemplar, of the match to pull
        matchNumber: The match ID number of the match to pull
        allMatches: A dataframe of all match result data

    Returns:
        Returns a dictionary. If the match is not found, matchExists with be the only parameter and will be set to false. Otherwise, it will have
            matchExists: Will be True if the match is found 
            deckA: String of P1's deck
            deckB: String of P2's deck
            resultR: The emoji + W/T/L/- of the red guru's result
            guruR: The red guru's signature
            resultU: The emoji + W/T/L/- of the blue guru's result
            guruU: The blue guru's signature
            resultG: The emoji + W/T/L/- of the green guru's result
            guruG: The green guru's signature
            result: The string of the total result, which can be 0, 0.5, 1, incomplete, or discrepancy
            inverseID: The full name of the inverse match
            inverseEmoji: The emoji + W/T/L/- of the inverse match's result
            linkedID: The ID of the thread linked to this match, if one exists
            rowNumber: The row in the google sheet this match is in
    """
    matchID = podLetter+" "+podNumber+" "+matchNumber
    rowIndex = (allMatches.index[allMatches['FID'] == matchID]).values
    if (len(rowIndex) != 1): return {"matchExists": False}
    row = rowIndex[0]
    invID = podLetter + " " + podNumber + " " + str(allMatches['IVID'].iloc[row])
    result = str(allMatches['Rst'].iloc[row])
    try:
        invRow = (allMatches.index[allMatches['FID'] == invID]).values[0]
        invResRaw = str(allMatches['Rst'].iloc[invRow])
        if(RESULT2NUM.get(result,-1)>=0 and RESULT2NUM.get(invResRaw,-1)>=0 and RESULT2NUM[result] < RESULT2NUM["1"] - RESULT2NUM[invResRaw]):
            invEmoji = INV2EMOJI.get(invResRaw) + " ⚠️ Error Suspected ⚠️"
        else:
            invEmoji = INV2EMOJI.get(invResRaw,"⚪ -")
    except:
        invEmoji = "⚪ -"
    return {
        "matchExists": True,
        "deckA": str(allMatches['P1Deck'].iloc[row]),
        "deckB": str(allMatches['P2Deck'].iloc[row]),
        "resultR": RESULT2EMOJI.get(str(allMatches['RRs'].iloc[row]),"⚪ -"),
        "guruR": str(allMatches['RGuru'].iloc[row]),
        "resultU": RESULT2EMOJI.get(str(allMatches['URs'].iloc[row]),"⚪ -"),
        "guruU": str(allMatches['UGuru'].iloc[row]),
        "resultG": RESULT2EMOJI.get(str(allMatches['GRs'].iloc[row]),"⚪ -"),
        "guruG": str(allMatches['GGuru'].iloc[row]),
        "result": result,
        "inverseID": LETTER2NAME.get(podLetter)+" "+((podNumber+" ") if podLetter!="E" else "")+str(allMatches['IVID'].iloc[row]),
        "inverseEmoji": invEmoji,
        "linkedID": str(allMatches['TLink'].iloc[row]),
        "rowNumber": row + 2
    }

def getGuruString(guru: str, ping: bool, allGurus: pd.DataFrame=None):
    """
    Turns guru signatures into the string to be used in the discord message

    Args:
        guru: The signature
        ping: A boolean that if true will attemp to turn the into pings of the guru registered to that signature
        allGurus: A DataFrame used to match guru signatures to discord IDs

    Returns:
        A sting. If ping is false, it will return exactly the input signature.
    """
    if(not ping): return guru
    try:
        strippedGuru = guru.strip().casefold()
        guruRow = (allGurus.index[allGurus['NAME'] == strippedGuru]).values[0]
        guruID = str(allGurus['GURUID'].iloc[guruRow])
        return f"<@{guruID}>"
    except:
        return guru

def formatSummary(headerString: str, inc_df: pd.DataFrame, des_df: pd.DataFrame, incudePodID: bool, skipInc: bool, incName: str):
    """
    Creates a summary message from DataFrames of incomplete and discrepancy matches.

    Args:
        headerString: The string to be the first line of the discord message
        inc_df: DataFrame of of matches that have not been completed
        des_df: DataFrame of of matches that are discrepancies
        incudePodID: A boolean for if the Pod ID should be used to identify matches
        skipInc: A boolen to not list any incomplete matches, even if it could fit
        incName: What to call incomplete matches

    Returns:
        A string formated for a discord mesage of the header string followed by a listing of the matches and linked threads as space allows.
        Will attemp to return a message no longer than 2000 charactrers per discord limits, returning the header sting if none fit.
        Read more about the choices made to limit mesage size in the bot documentation. 
    """
    if(len(des_df) <= 25 and len(des_df) > 0):
        desFull = desCond = f"\nDiscrepancies"
        for index, row in des_df.iterrows():
            line = f"\n-"
            if (row['TLink']): 
                line += f" <#{row['TLink']}>"
            if (incudePodID): 
                line += f" {row['PID']}"
            line += f" {row['NID']}"
            desFull += line + f": {row['P1Deck']} vs {row['P2Deck']}"
            desCond += line
    else: desFull = desCond = f""
    if(len(inc_df) <= 25 and len(inc_df) > 0 and len(des_df) + len(inc_df) <= 30 and not skipInc):
        incFull = incCond = f"\n{incName}"
        for index, row in inc_df.iterrows():
            line = f"\n-"
            if (row['TLink']): 
                line += f" <#{row['TLink']}>"
            if (incudePodID): 
                line += f" {row['PID']}"
            line += f" {row['NID']}"
            incFull += line + f": {row['P1Deck']} vs {row['P2Deck']}"
            incCond += line
    else: incFull = incCond = f""
    if (2000 >= len(headerString) + len(desFull) + len(incFull)): return  headerString + desFull + incFull
    if (2000 >= len(headerString) + len(desFull) + len(incCond)): return  headerString + desFull + incCond
    if (2000 >= len(headerString) + len(desCond) + len(incCond)): return  headerString + desCond + incCond
    if (2000 >= len(headerString) + len(desFull)): return  headerString + desFull
    if (2000 >= len(headerString) + len(desCond)): return  headerString + desCond
    return headerString

def threadSummary(linked_df: pd.DataFrame):
    """
    Lists each guru's result on all provided matches in an extremely compact discord mesage format.

    Args:
        linked_df: A DataFrame of the matches to list.

    Returns:
        Returns a monospaced formated discord mesage as a small grid listing all matches and each guru's result.
    """
    summary =f"```\nMatch ID  |🟥🟦🟩"
    for index, row in linked_df.iterrows():
        names=row["FID"].split(" ")
        if (names[1]=="0"):
            names[1] = ""
        summary += f"\n"+names[0]+" "+names[1].ljust(3)+" "+names[2].ljust(4)
        summary +=f"|"+RESULT2SHORTEMOJI.get(row['RRs'],"⚪")+RESULT2SHORTEMOJI.get(row['URs'],"⚪")+RESULT2SHORTEMOJI.get(row['GRs'],"⚪")
    summary += f"```"
    return summary