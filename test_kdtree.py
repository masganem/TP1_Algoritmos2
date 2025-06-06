from util import load_dataframe, build_kdtree, query_kdtree


def test_kdtree_range_search_matches_pandas():
    """
    KDTree range_search should return exactly the same rows as a Pandas bounding-box filter.
    """
    df = load_dataframe()
    tree = build_kdtree(df)

    # Use the first point as centre of a small bounding box so at least one match is guaranteed.
    center_lat, center_lon = df.loc[0, ["lat", "lng"]]
    delta = 0.002  # ~200 m
    min_lat, max_lat = center_lat - delta, center_lat + delta
    min_lon, max_lon = center_lon - delta, center_lon + delta

    pandas_matches = df[(df["lat"] >= min_lat) & (df["lat"] <= max_lat) &
                         (df["lng"] >= min_lon) & (df["lng"] <= max_lon)]
    kd_matches = query_kdtree(tree, min_lat, max_lat, min_lon, max_lon)

    pandas_ids = set(pandas_matches.index)
    kd_ids = {tpl[2] for tpl in kd_matches}

    # They should match exactly.
    assert kd_ids == pandas_ids, (
        f"Mismatch between KDTree (n={len(kd_ids)}) and Pandas (n={len(pandas_ids)}) "
        f"for box lat:[{min_lat},{max_lat}] lon:[{min_lon},{max_lon}]"
    )

    # Additionally, ensure at least one point was found (sanity check).
    assert kd_ids, "Expected at least one point in bounding box, found none." 