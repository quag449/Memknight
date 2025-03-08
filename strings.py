EMOJI_COMPLEAT = "<:compleated:1327063094014513183>"
EMOJI_R = "<:manar:1317337889675280444>"
EMOJI_U = "<:manau:1317337903113703477>"
EMOJI_G = "<:manag:1317337912966381628>"

  

PODLETTERS =  ["N","A","C","E"]
PODNUMBERS =  ["I","II","III","IV","V","VI","VII","VIII","IX","X"]

LETTER2NAME = {
    "N": "Novice",
    "A": "Aspirant",
    "C": "Contender",
    "E": "Exemplar"
}

NAME2LETTER = {
    "NOVICE": "N",
    "ASPIRANT": "A",
    "CONTENDER": "C",
    "EXEMPLAR": "E"
}

NUMBER2ROMAN = {
    "1": "I",
    "2": "II",
    "3": "III",
    "4": "IV",
    "5": "V",
    "6": "VI",
    "7": "VII",
    "8": "VIII",
    "9": "IX",
    "10": "X"
}

RESULT2STRING = {
    "0": "L (0)",
    "0.5": "T (0.5)",
    "1": "W (1)",
    "Discrepancy": "Discrepancy",
    "Incomplete": "Incomplete"
}

RESULT2NUM = {
    "0": 0,
    "0.5": 1,
    "1": 2
}

RESULT2EMOJI = {
    "0": "🔴 L",
    "0.5": "🟡 T",
    "1": "🔵 W"
}

RESULT2SHORTEMOJI = {
    0: "🔴",
    0.5: "🟡",
    1: "🔵"
}


INV2EMOJI = {
    "1": "🔴 L",
    "0.5": "🟡 T",
    "0": "🔵 W"
}

HELPTEXT = {
    "getmatch": "Use with a Match ID to get a summary of that match in chat.\nThe optional parameter usediscordids can be used to toggle between signatures and discord mentions.",
    "peekmatch": "Use with a Match ID to get a summary of that match that only you can see.\nThe optional parameter usediscordids can be used to toggle between signatures and discord mentions.",
    "pingmatch": "Use with a Match ID and Memknight will list all gurus signed to the match, pinging any registered discords.",
    "writeup": "The longer alternative to /writeup, adding in /getmatch and /pingmatch.\nUsed in a guru-match-help thread with a Match ID to connect that thread to the match. The linked thread will be included in other commands that reference that match as well as on the sheet. Each match can only be linked to one thread at a time, but multiple matches can be linked to the same thread. It will also provide information about that match and ping all gurus on that match that have registered their name.",
    "summary": "Used with a Pod ID to give information about the matches remaining in that pod.\nThe optional parameter privacystatus can be used to toggle between the summary being shown to everyone or only to you.\nThe optional parameter onlydiscrepancies can be used to toggle between only listing details for discrepancies or for all matches.",
    "summaryall": "Give information about the matches remaining across all pods.\nThe optional parameter privacystatus can be used to toggle between the summary being shown to everyone or only to you.\nThe optional parameter onlydiscrepancies can be used to toggle between only listing details for discrepancies or for all matches.",
    "gurusummary": "Used with a signature to give information about the matches remaining with that signature. Private by default.\nThe optional parameter podid can be used to limit this summary to only a single pod.\nThe optional parameter privacystatus can be used to toggle between the summary being shown to everyone or only to you.\nThe optional parameter onlydiscrepancies can be used to toggle between only listing details for discrepancies or for all matches.",
    "tlink": "The shorter alternative to /writeup.\nUsed in a guru-match-help thread with a Match ID to connect that thread to the match. The linked thread will be included in other commands that reference that match as well as on the sheet. Each match can only be linked to one thread at a time, but multiple matches can be linked to the same thread.",
    "ulink": "Used with a Match ID to remove the link created by /tlink or /writeup.",
    "registerguru": "Use with the name you sign on the guru sheets. This is done so several other commands can ping the correct person. You can register to more than one name, and names are not case sensitive.",
    "unregisterguru": "Use with a name you have already registered to no longer be pinged when the signature is pinged.",
    "discrepancyurl": "This function provides a private hyperlink to the guru match hub so you can access it anywhere.",
    "Match IDs": "Multiple functions take an input of a Match ID, which is composed of a pod type, a pod number, and a match number. Several spacing patterns can be parsed. For Novice II 113, the accepted inputs are:\n- NII113\n- NII 113\n- N2 113\n- N II 113\n- N 2 113\n- Novice II 113\n- Novice 2 113\nThe exemplar pod does not have a pod number, so Exemplar 97 could be input as\n- E97\n- E 97\n- Exemplar 97",
}

DEFAULTHELPTEXT = "All of Memknight's commands are accessible by typing a slash at the start of a message. Add a parameter to /help to hear about a specific function, or read the full documentation here:\nhttps://docs.google.com/document/d/1q17rMTJsOicrJLAYlmSjVxT74e7WOUl-RxZC-5FqKxQ/edit?usp=sharing"