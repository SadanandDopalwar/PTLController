


async def colormap(user_id, ptlcolor):
    colormap_dict = {
        "SW": '2"!',
        "W": "33!",
        "BW": "33#",

        "SR": "2\x11!",
        "R": "3\x11!",
        "BR": "3\x11#",

        "SG": "1!!",
        "G": "11!",
        "BG": "11#",

        "SB": "1\x12!",
        "B": "1\x13!",
        "BB": "1\x13#",

        "SY": "2!!",
        "Y": "31!",
        "BY": "31#",

        "SP": "2\x12!",
        "P": "3\x13!",
        "BP": "3\x13#",

        "SC": '1"!',
        "C": "13!",
        "PC": "13#",
        
        "BM": "3\x121"
    }
    
    return colormap_dict.get(ptlcolor)