from util import load_dataframe, build_kdtree, query_kdtree

df = load_dataframe()

tree = build_kdtree(df)

# Balaio de Gato
results = query_kdtree(tree, -19.9261809 - 0.002, -19.9261809 + 0.002, -43.9488649 - 0.002, -43.9488649 + 0.002)

print(results)

for result in results:
    print(df.loc[result[2]])