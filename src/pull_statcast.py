"""Pull Statcast pitch-level data, one parquet file per season."""
from pathlib import Path

from pybaseball import cache, statcast

cache.enable()          # avoids re-downloading if you stop and restart

RAW = Path("data/raw")
RAW.mkdir(parents=True, exist_ok=True)

SEASONS = {
    2021: ("2021-04-01", "2021-10-03"),
    2022: ("2022-04-07", "2022-10-05"),
    2023: ("2023-03-30", "2023-10-01"),
    2024: ("2024-03-28", "2024-09-29"),
}

def pull_season(year, start, end):
    out = RAW / f"statcast_{year}.parquet"
    if out.exists():
        print(f"{year}: already downloaded, skipping")
        return
    print(f"{year}: pulling {start} to {end} ...")
    df = statcast(start_dt=start, end_dt=end)
    df.to_parquet(out)
    print(f"{year}: {len(df):,} pitches saved")

if __name__ == "__main__":
    for year, (start, end) in SEASONS.items():
        pull_season(year, start, end)