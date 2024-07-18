import numpy as np
from tqdm import tqdm

ranks = 32
_traveltimes = []
for rank in tqdm(range(ranks)):
    traveltimes = np.load(f"fmm_out/traveltimes_{rank}.npy")
    s_indices = np.load(f"fmm_out/s_indices_{rank}.npy")
    # print(s_indices)
    _traveltimes.append(traveltimes)

# print(np.sum(_traveltimes, axis=0))
# print(np.sum(_traveltimes, axis=0).shape)

np.save("fmm_traveltimes.npy", np.sum(_traveltimes, axis=0))
