def remove_non_anc(s):
    """
    Removes non alphanumeric characters
    """
    _s = s
    illegal = [".", "*", "-", "--"]
    for c in illegal:
       _s = _s.replace(c, "") 
    return _s

def remove_buzzwords(s):
    buzzwords = ["bar", "restaurante", "ltda", "e", "ave", "rua", "avenida", "das", "dos", "de", "da", "do"] 
    return " ".join(list(filter(lambda x: x not in buzzwords, s.split(" "))))

def normalize_accents(s):
    _s = s
    accent_norm = {'á':'a','à':'a','ã':'a','â':'a','é':'e','ê':'e','í':'i','ó':'o','ô':'o','õ':'o','ú':'u','ç':'c','ü':'u'}
    for (accented, unaccented) in accent_norm.items():
        _s = _s.replace(accented, unaccented)
    return _s

def normalize(s):
    normal = s.lower().strip().replace(",,", ",").replace(", nan", ", EMPTY_COMPLEMENT").replace(", Belo Horizonte, Minas Gerais, Brasil", "")
    normal = remove_non_anc(normal)
    normal = normalize_accents(normal)
    normal = remove_buzzwords(normal)
    normal = normal.strip()
    return normal

def get_address_hash(s):
    street, number = s.split(',')[:2]
    number = normalize(number)
    street = normalize(street)
    return f"{street}#{number}"


def align_data(butecos_data, pbh_data):
    butecos_data = butecos_data.copy()
    pbh_data    = pbh_data.copy()

    butecos_data["name"]    = butecos_data["name"].apply(normalize)
    butecos_data["address"] = butecos_data["address"].apply(lambda x: x.split('|')[0])
    butecos_data["address"] = butecos_data["address"].apply(get_address_hash)

    pbh_data["name"]    = pbh_data["name"].apply(normalize)
    pbh_data["address"] = pbh_data["address"].apply(get_address_hash)

    butecos_data = butecos_data.rename(columns={"address": "address_hash"})
    pbh_data    = pbh_data.rename(columns={"address": "address_hash"})

    merged = butecos_data.merge(
        pbh_data,
        on=["address_hash", "name"],
        how="inner",                     # or 'left' / 'outer' depending on what you need
        suffixes=("_buteco", "_pbh")
    )

    return merged
