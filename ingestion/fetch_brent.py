from raw import download_raw

URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DCOILBRENTEU"

if __name__ == "__main__":
    path = download_raw(URL, "brent", "brent", "csv")
    print(f"saved {path}")