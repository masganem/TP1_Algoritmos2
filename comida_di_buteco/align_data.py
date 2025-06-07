import pandas as pd

def remove_non_anc(s):
    """
    Removes non alphanumeric characters
    """
    _s = s
    illegal = [".", "*", "-", "--", "'s", "’s", "' s", "’ s", "s'"]
    for c in illegal:
       _s = _s.replace(c, "") 
    return _s

def remove_buzzwords(s):
    buzzwords = ["bar", "restaurante", "ltda", "e", "ave", "rua", "avenida", "das", "dos", "de", "da", "do", "delivery", "fogo", "parrilla", "picanha", "cia", "alimentacao"] 
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
    """
    Return *pbh_data* with an extra column `cdb_idx` indicating the index
    of the matching buteco in `butecos_data`.
    """
    result_df = pbh_data.copy()

    but_df = butecos_data.copy().reset_index().rename(columns={"index": "cdb_idx"})
    pbh_df = pbh_data.copy().reset_index().rename(columns={"index": "pbh_idx"})

    but_df["name_norm"]    = but_df["name"].apply(normalize)
    but_df["address_hash"] = but_df["address"].apply(lambda x: x.split('|')[0]).apply(get_address_hash)

    pbh_df["name_norm"]    = pbh_df["name"].apply(normalize)
    pbh_df["address_hash"] = pbh_df["address"].apply(get_address_hash)

    but_df   = but_df.rename(columns={"name_norm": "name_buteco_norm"})
    pbh_df   = pbh_df.rename(columns={"name_norm": "name_pbh_norm"})

    merged = pbh_df.merge(
        but_df[["address_hash", "name_buteco_norm", "cdb_idx"]],
        on="address_hash",
        how="left"
    )

    def _names_intersect(row):
        if pd.isna(row.get("name_buteco_norm")):
            return False
        words_buteco = set(row["name_buteco_norm"].split())
        words_pbh    = set(row["name_pbh_norm"].split())
        return len(words_buteco.intersection(words_pbh)) > 0

    matched = merged[merged.apply(_names_intersect, axis=1)]

    mapping = matched.groupby("pbh_idx")["cdb_idx"].first()

    result_df["cdb_idx"] = result_df.index.map(mapping).fillna(-1).astype(int)

    num_matches = (result_df["cdb_idx"] != -1).sum()
    print(f"Matched {num_matches} of {len(result_df)} PBH entries")

    return result_df
