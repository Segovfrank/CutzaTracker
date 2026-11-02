from functools import lru_cache
from dask.distributed import Client, LocalCluster

@lru_cache(maxsize=1) #Singleton
def get_client(workers_total: int = 1, threads_per_worker: int = 8) -> Client:
    return Client(LocalCluster(n_workers=workers_total, threads_per_worker=threads_per_worker, processes=False))

def close_client() -> None:
    if get_client.cache_info().currsize:
        client = get_client()
        client.close()
        client.cluster.close()
        get_client.cache_clear()
        