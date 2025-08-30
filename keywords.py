# keywords.py

# A comprehensive list of keywords, hashtags, and phrases for detecting potentially
# hostile or anti-India narratives on social media.
# Note: Many of these terms can be used in legitimate criticism. The goal is to
# use this list as a first-pass filter, with further analysis (sentiment, network)
# determining the actual intent.

KEYWORDS = [
    # --- Direct Anti-India & Derogatory Hashtags ---
    "#BoycottIndia",
    "#IndiaIsFailing",
    "#ShameOnIndia",
    "#Endia",          # Common derogatory spelling
    "#IndiaOut",
    "#GoBackModi",
    "#IndianStateTerrorism",
    "#FascistIndia",
    "#RSSterror",

    # --- Narratives on Kashmir ---
    "#FreeKashmir",
    "#KashmirGenocide",
    "#StandWithKashmir",
    "#KashmirUnderSiege",
    "Indian occupation of Kashmir",
    "Kashmiri oppression",
    "atrocities in Kashmir",
    "demographic change Kashmir",

    # --- Religious & Communal Divisiveness ---
    "Hindu mobs",
    "Hindutva terror",
    "Saffron terror",
    "Islamophobia in India",
    "Muslims under attack in India",
    "RSS extremists",
    "BJP anti-muslim",
    "Christian persecution India",
    "Dalit oppression",
    "Brahminical patriarchy", # Often used in divisive narratives
    "Anti-Sikh riots",

    # --- Separatist & Insurgency Narratives ---
    "#Khalistan",
    "#SikhGenocide",
    "Khalistan Referendum",
    "Free Punjab",
    "#FreeNagaland",
    "#FreeManipur",
    "Never Forget 1984",

    # --- Political & Governance Criticism (Co-opted for Propaganda) ---
    "Modi fascist",
    "Indian dictatorship",
    "failing democracy India",
    "BJP destroying India",
    "undeclared emergency",
    "suppression of dissent India",
    "no freedom of speech India",
    "EVM scam",
    "death of democracy",

    # --- Economic & Social Issues (Weaponized) ---
    "#IndiaEconomyCollapse",
    "India poverty crisis",
    "unemployment crisis India",
    "failing state India",
    "human rights violations India",
    "Hunger Index India", # Often used to portray state failure
    "Press Freedom Index India",

    # --- Geopolitical & Foreign Relations Narratives ---
    "Indian interference",
    "Indian hegemony",
    "RAW agent",          # Common in conspiracy theories
    "Indian spy",
    "China-India border clash",
    "Pakistan Zindabad",  # Often paired with anti-India content

    # --- Common Propaganda Phrases & Slang ---
    "Godi media",         # Accusation of media being pro-government
    "Bhakts",             # Derogatory term for supporters
    "Andh Bhakts",        # A more intense version
    "IT Cell",            # Refers to political party's social media teams
    "Indian state-sponsored propaganda",
    "Two Nation Theory",
    "presstitutes",

    # --- Variations using "OR" (Handled by the query builder) ---
    "Indian Army atrocities OR Indian Army war crimes",
    "lynching in India OR mob violence India"
]