from gr_aggregation.borda_count import BordaCount

def borda_count(data: list, factor: int) -> dict:
    borda_instance = BordaCount(data, factor)
    return borda_instance.borda_result()