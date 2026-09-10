"""Aggregate pitch-level data to one row per pitcher-appearance."""
from pathlib import Path

import pandas as pd

RAW  = Path("data/raw")
PROC = Path("data/processed")
PROC.mkdir(parents=True, exist_ok=True)

KEEP = ["game_date", "game_pk", "pitcher", "player_name", "pitch_type",
        "release_speed", "release_spin_rate", "release_pos_x",
        "release_pos_z", "release_extension", "p_throws", "inning"]

FASTBALLS = ["FF", "SI", "FC"]

def build_season(year):
    df = pd.read_parquet(RAW / f"statcast_{year}.parquet", columns=KEEP)
    df["game_date"] = pd.to_datetime(df["game_date"])

    # R: group_by(pitcher, player_name, game_pk, game_date) %>% summarise(...)
    app = (df.groupby(["pitcher", "player_name", "game_pk", "game_date"],
                      as_index=False)
             .agg(n_pitches    = ("release_speed", "size"),
                  mean_velo    = ("release_speed", "mean"),
                  max_velo     = ("release_speed", "max"),
                  mean_spin    = ("release_spin_rate", "mean"),
                  rel_x_sd     = ("release_pos_x", "std"),
                  rel_z_sd     = ("release_pos_z", "std"),
                  mean_ext     = ("release_extension", "mean"),
                  first_inning = ("inning", "min"),
                  last_inning  = ("inning", "max")))

    # fastball velocity computed separately, then joined back
    # R: filter(pitch_type %in% FASTBALLS) %>% group_by(...) %>% summarise(...)
    fb = (df[df["pitch_type"].isin(FASTBALLS)]
            .groupby(["pitcher", "game_pk"], as_index=False)
            .agg(fb_velo=("release_speed", "mean"),
                 fb_spin=("release_spin_rate", "mean")))

    # R: left_join(app, fb, by = c("pitcher", "game_pk"))
    app = app.merge(fb, on=["pitcher", "game_pk"], how="left")
    app["season"] = year
    return app

if __name__ == "__main__":
    years = [2021, 2022, 2023, 2024]
    out = pd.concat([build_season(y) for y in years], ignore_index=True)
    out = out.sort_values(["pitcher", "season", "game_date"])
    out.to_parquet(PROC / "appearances.parquet")
    print(f"{len(out):,} appearances, {out['pitcher'].nunique():,} pitchers")