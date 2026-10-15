from raw import download_raw

URL = "https://api.frankfurter.app/2020-01-01..?base=USD&symbols=ZAR"

if __name__ == "__main__":
    path = download_raw(URL, "fx", "usd_zar", "json")
    print(f"saved {path}")