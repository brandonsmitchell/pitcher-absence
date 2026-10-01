# Pitcher Absence Prediction
# Predicting Extended MLB Pitcher Absences

A Python project that uses public MLB Statcast data to build features for predicting extended pitcher absences (injured list stints and other long layoffs).

## Status

In progress. The data pipeline and feature engineering are complete, including a leakage-safe train/validation/test split. Model development has not been started.

## Project Goal

Pitcher injuries are costly for teams and difficult to anticipate. This project asks whether patterns in pitch-level data, such as changes in velocity, spin, and usage, carry information about the probability that a pitcher will miss an extended period of time.

## Data

- Source: public MLB Statcast pitch-level data, pulled with the `pybaseball` package
- Seasons covered: 2021 to 2024
- Definition of an extended absence: no confirmed injured list data exists publicly at the pitch-level grain this project uses, so absence is defined as a gap before a pitcher's next appearance, and the gap is treated as an honest proxy for injury rather than a direct measurement of it. The threshold is role specific rather than a single flat number, since a missed rotation turn and an unused bullpen stretch are structurally different events: 9 or more days for starters and 11 or more days for relievers, each chosen from that role's own empirical gap distribution rather than an arbitrary cutoff. This yields an overall absence rate of about 4.6 percent, 8.2 percent for starters and 3.5 percent for relievers.

## Approach

1. **Data collection:** Download pitch-level Statcast data for the 2021 to 2024 seasons.
2. **Aggregation:** Collapse pitch-level rows to one row per pitcher per appearance, computing pitch counts, velocity, spin, and release-point variability per outing.
3. **Outcome definition:** Derive the role-specific absence outcome described above directly from the gaps between a pitcher's own appearances.
4. **Feature engineering:** Build backward-looking features from prior appearances only, including rolling workload (pitch and appearance counts over 7, 14, and 30 days), usage rates (entering in the 9th inning or later, short outings, appearances on one day of rest), velocity relative to a pitcher's own season average, and a single usage index built with PCA from the three usage rates, used only as a prior-season value so it cannot leak information from games that have not happened yet.
5. **Splitting:** Train on 2021 and 2022, validate on 2023, and test on 2024, with a grouped cross-validation check confirming that splitting by row rather than by pitcher lets the same person's appearances leak across folds.
6. **Modeling (next):** Train and evaluate predictive models that output the probability of an extended absence.

## Tools

- Python, with pandas, numpy, pybaseball, and scikit-learn as the main packages
- Conda for environment management
- Git and GitHub for version control
- Positron as the development environment

## Repository Structure

```text
data/         raw and processed Statcast data (not tracked in Git)
notebooks/    data exploration, outcome definition, and split validation
src/          pipeline scripts: download, aggregation, feature engineering
outputs/      saved figures (populated once modeling begins)
README.md
```

## How to Run

```bash
conda create -n pitching python=3.11
conda activate pitching
pip install pybaseball pandas numpy scikit-learn jupyter

git clone https://github.com/brandonsmitchell/pitcher-absence.git
cd pitcher-absence

python src/pull_statcast.py
python src/build_appearances.py
python src/build_features.py
```

Then open the notebooks in `notebooks/` in order to see the outcome definition, exploratory checks, and split validation.

## Planned Work

- Fit baseline models, penalized logistic regression, including a test of whether rest predicts absence differently by role, and gradient boosting, then compare both against a small PyTorch neural network
- Evaluate with metrics suited to a rare, imbalanced outcome, precision-recall AUC, calibration, and a decision threshold set from an operational budget rather than a default cutoff
- Extend the analysis with hierarchical or mixed-effects models linking pitcher-level features to team-level context, to examine whether reliance on velocity and spin relates to divisional or postseason success

## Author

Brandon S. Mitchell, Ph.D.
