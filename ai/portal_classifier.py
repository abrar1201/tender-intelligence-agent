KEYWORDS = [

"tender",
"procurement",
"rfp",
"bid opportunity",
"supplier registration",
"contract opportunity"

]


def is_procurement_portal(text):

    text = text.lower()

    for k in KEYWORDS:

        if k in text:

            return True

    return False