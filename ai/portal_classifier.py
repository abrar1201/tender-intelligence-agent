PRIMARY_KEYWORDS = [
    # ERP
    "enterprise resource planning", "erp system", "erp solution",
    "erp implementation", "erp software", "erp procurement", "erp platform",
    # CRM
    "customer relationship management", "crm system", "crm solution",
    "crm implementation", "crm software", "crm platform",
    # Supply Chain
    "supply chain management", "supply chain system", "supply chain software",
    "scm system", "scm solution", "inventory management system",
    "warehouse management system", "logistics management system",
    # HR / HCM / Payroll
    "human capital management", "human resource management system",
    "hcm system", "hcm solution", "hr system", "hr software",
    "hr management system", "hr information system", "hris", "hrms",
    "payroll system", "payroll software", "payroll management",
    "workforce management system", "workforce management software",
    "employee management system", "employee management software",
    "staff management system",
    # Asset Management
    "asset management system", "asset management software",
    "asset management solution", "enterprise asset management",
    "eam system", "eam solution", "fixed asset management",
    # Fleet Management
    "fleet management system", "fleet management software",
    "fleet management solution", "fleet tracking system",
    "vehicle management system", "transport management system",
    # Library Management
    "library management system", "library management software",
    "library system", "lms library", "integrated library system", "ils system",
    # Finance
    "financial management system", "financial management software",
    "accounting system", "accounting software", "finance system",
    "finance software", "erp finance", "general ledger system",
    "budgeting system",
    # Platforms
    "sap", "oracle erp", "oracle fusion", "dynamics 365",
    "microsoft dynamics", "netsuite", "workday", "sage erp",
    "infor erp", "unit4", "epicor", "odoo", "syspro", "ifs erp",
    # ICT managed services
    "ict managed service", "ict solution", "ict system",
    "managed service", "managed it", "it managed service",
    "microsoft managed service",

    # ─────────────────────────────────────────────────────────────────────
    # FOREIGN LANGUAGE KEYWORDS for TED (EU) tenders
    # TED titles are in the country's language — BERT scores them lower
    # Adding keywords lets them pass via keyword path instead
    # ─────────────────────────────────────────────────────────────────────

    # Latvian (very common in TED results)
    "uzņēmuma resursu plānošanas",      # enterprise resource planning
    "personāla vadības programmatūra",  # HR management software
    "algu izmaksas vadības",            # payroll management
    "finanšu sistēmas programmatūra",   # financial system software
    "bibliotēkas programmatūra",        # library software

    # Hungarian
    "humánerőforrás-szoftver",          # HR software
    "bérszámfejtési",                   # payroll
    "vállalati erőforrás",              # enterprise resource
    "készletgazdálkodási",              # inventory management
    "flottakezelő",                     # fleet management

    # Swedish
    "administrativt bibliotekssystem",  # library management system
    "personalsystem",                   # HR system
    "lönesystem",                       # payroll system
    "affärssystem",                     # business system (ERP)
    "lagerhanteringssystem",            # warehouse management
    "flotthantering",                   # fleet management

    # Danish
    "personalesystem",                  # HR system
    "lønsystem",                        # payroll system
    "bibliotekssystem",                 # library system
    "lagerstyringssystem",              # inventory system

    # Norwegian
    "personalsystem",                   # HR system
    "lønnssystem",                      # payroll system
    "biblioteksystem",                  # library system
    "flåtestyring",                     # fleet management

    # Finnish
    "henkilöstöhallintojärjestelmä",    # HR system
    "palkanlaskentajärjestelmä",        # payroll system
    "kirjastojärjestelmä",              # library system
    "toiminnanohjausjärjestelmä",       # ERP system

    # German
    "personalverwaltungssystem",        # HR system
    "lohnbuchhaltungssystem",           # payroll system
    "bibliotheksverwaltungssystem",     # library management system
    "fuhrparkverwaltung",               # fleet management
    "warenwirtschaftssystem",           # inventory/ERP system

    # French
    "système de gestion des ressources humaines",  # HR system
    "système erp",                      # ERP system
    "logiciel de paie",                 # payroll software
    "système de gestion de bibliothèque", # library system
    "gestion de flotte",                # fleet management

    # Spanish
    "sistema de gestión de recursos humanos",  # HR system
    "software de nómina",               # payroll software
    "sistema erp",                      # ERP system
    "gestión de flota",                 # fleet management

    # Dutch
    "personeelsbeheersysteem",          # HR system
    "salarissysteem",                   # payroll system
    "bibliotheekbeheersysteem",         # library system
    "wagenparkbeheer",                  # fleet management

    # Romanian
    "sistem de management al resurselor umane",  # HR system
    "sistem erp",                       # ERP system

    # Polish
    "system zarządzania zasobami ludzkimi",  # HR system
    "system erp",                       # ERP system
]

COMPOUND_KEYWORDS = [
    ("erp", "implementation"), ("erp", "procurement"),
    ("erp", "tender"), ("erp", "rfp"),
    ("crm", "implementation"), ("crm", "procurement"),
    ("payroll", "implementation"), ("payroll", "procurement"),
    ("fleet", "software"), ("fleet", "system"),
    ("hr", "implementation"), ("hris", "implementation"),
    ("library", "software"), ("asset management", "implementation"),
    ("workforce", "software"), ("workforce", "system"),
    ("workforce", "platform"),
    ("enterprise", "software"),
    ("enterprise", "platform"),
    ("enterprise", "system"),
    ("ict", "service"),
    ("ict", "infrastructure"),
    ("microsoft", "service"),
    ("microsoft", "system"),
]

EXCLUSION_KEYWORDS = [
    # Medical
    "cancer", "mammography", "clinical simulation", "surgical",
    "medical device", "stoma", "immunisation", "immunization",
    "pharmacy", "anaesthetic", "radiology", "pathology",
    "maternity", "midwifery", "ambulance", "health visiting",
    "screening programme",
    # Social care
    "mental health service", "safeguarding", "care home", "care at home",
    "residential care", "foster", "kinship care", "child protection",
    "psychology services", "employment support",
    # Construction / physical
    "construction", "roofing", "fencing", "noise barrier",
    "anti-radiation shelter", "refurbishment", "fire strategy",
    "acoustic", "play area", "celtniecības",
    "batteries", "hi vis", "furniture", "linen", "laundry",
    "operating table", "patient positioning", "shrike",
    "bolts and fixings", "mobile operating",
    "sprutmaskiner", "säkerhetsspeglar", "mirrors", "mirror installation",
    # Chemical / military / industrial (SAM.gov false positives)
    "ethacure", "tungsten", "torpedo", "valve", "screw shoulder",
    "fin assembly", "shielding", "polygraph", "isolation repair",
    "fire alarm", "smoke exhaust", "ventilation system",
    "ammunition", "weapon", "explosive", "military supply",
    # Nature
    "tree management", "arboricultural", "ecology",
    "predator exclusion", "recycling treatment",
    # Marketing / non-IT
    "marketing campaign", "careers marketing", "wayfinding",
    "christmas illumination", "holiday activity", "food programme",
    "volunteer", "immunisations",
    # WorldBank/ADB report exclusions
    "procurement reform", "public financial management reform",
    "restructuring paper", "development policy",
    "institutional strengthening", "capacity building",
    "country partnership", "project appraisal",
    "sector review",
]

# ─────────────────────────────────────────────────────────────────────────────
# PER-SOURCE THRESHOLDS
# samgov moved to keyword-required (high=999) — too many military/chemical
# contracts that score high on LLM but are irrelevant
# ted lowered to 0.38 — foreign language titles score lower but are genuine
# ─────────────────────────────────────────────────────────────────────────────
THRESHOLDS = {
    "uk":          {"high": 0.36, "low": 0.25},
    "findatender": {"high": 0.36, "low": 0.25},
    "samgov":      {"high": 999,  "low": 0.30},  # keyword always required
    "ted":         {"high": 0.38, "low": 0.28},  # lowered for foreign languages
    "worldbank":   {"high": 999,  "low": 0.30},  # keyword always required
    "adb":         {"high": 999,  "low": 0.30},  # keyword always required
    "canada":      {"high": 999,  "low": 0.28},
    "_default":    {"high": 0.42, "low": 0.30},
}

DEBUG_SOURCES = {"uk", "findatender", "ted", "samgov"}


def _keyword_match(text: str) -> bool:
    return any(k in text for k in PRIMARY_KEYWORDS)


def _compound_match(text: str) -> bool:
    return any(a in text and b in text for a, b in COMPOUND_KEYWORDS)


def _matched_keyword(text: str) -> str:
    for k in PRIMARY_KEYWORDS:
        if k in text:
            return f'primary:"{k}"'
    for a, b in COMPOUND_KEYWORDS:
        if a in text and b in text:
            return f'compound:"{a}"&"{b}"'
    return ""


def _matched_exclusion(text: str) -> str:
    for ex in EXCLUSION_KEYWORDS:
        if ex in text:
            return ex
    return ""


def is_relevant(t: dict) -> bool:
    title = (t.get("title") or "").lower()
    description = (t.get("description") or "").lower()
    text = f"{title} {description}".strip()
    source = t.get("source", "")
    similarity = t.get("similarity")
    debug = source in DEBUG_SOURCES

    thresh = THRESHOLDS.get(source, THRESHOLDS["_default"])
    high = thresh["high"]
    low = thresh["low"]

    def log(status, reason):
        if debug:
            print(f"  [{status}] source={source} | {reason} | title={t.get('title', '')[:55]}")

    # Step 1 — exclusion check
    exclusion_hit = _matched_exclusion(text)
    if exclusion_hit:
        log("DROPPED", f"excluded:'{exclusion_hit}'")
        return False

    kw_match = _keyword_match(text) or _compound_match(text)
    matched_kw = _matched_keyword(text) if kw_match else "none"

    # Step 2 — LLM high confidence (source-specific threshold)
    if similarity is not None and similarity >= high:
        log("PASSED", f"LLM high ({similarity:.3f})")
        return True

    # Step 3 — LLM medium + keyword agreement
    if similarity is not None and similarity >= low and kw_match:
        log("PASSED", f"LLM+keyword ({similarity:.3f}, {matched_kw})")
        return True

    # Step 4 — keyword only for trusted sources
    if kw_match and source in ("uk", "findatender", "ted", "samgov"):
        if similarity is None or similarity >= 0.20:
            log("PASSED", f"keyword only ({matched_kw}), trusted source")
            return True

    sim_str = f"{similarity:.3f}" if similarity is not None else "None"
    log("DROPPED", f"sim={sim_str}, kw={kw_match}")
    return False


def is_procurement_portal(text: str) -> bool:
    text = text.lower()
    return any(k in text for k in PRIMARY_KEYWORDS)