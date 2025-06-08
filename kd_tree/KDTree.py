from kd_tree_cpp import KDTreeCPP

class KDTree:
    def __init__(self, df):
        try:
            points = [(row.lat, row.lng, int(idx)) for idx, row in df.iterrows()]
        except Exception as e:
            raise Exception(f"Failed to build KD_Tree: {e}")
        self._kdt = KDTreeCPP(points)

    def query(self, min_lat, max_lat, min_lon, max_lon):
        return self._kdt.range_search(min_lat, max_lat, min_lon, max_lon)
