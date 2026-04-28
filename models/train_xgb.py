import itertools
import json
import numpy as np
import pandas as pd
import xgboost as xgb
from pathlib import Path
from sklearn.metrics import (
    accuracy_score, roc_auc_score, log_loss, brier_score_loss
)

PROC_DIR  = Path(__file__).parent.parent / "data" / "processed"
MODEL_DIR = Path(__file__).parent

TRAIN_YEARS = [2019, 2020, 2021, 2022, 2023]
VAL_YEARS   = [2024]

# Fixed across all grid candidates; early stopping controls tree count
BASE_PARAMS = {
    'learning_rate':         0.05,
    'n_estimators':          500,
    'eval_metric':           'logloss',
    'early_stopping_rounds': 30,
    'random_state':          42,
}

# Previous grid showed reg_alpha/subsample/reg_lambda std of 0.0012 — fix at best.
# New grid focuses on tree complexity and recency decay.
FIXED_PARAMS = {
    'subsample':        0.8,
    'colsample_bytree': 0.7,
    'reg_alpha':        0,
    'reg_lambda':       3,
}

PARAM_GRID = {
    'max_depth':        [3, 4, 5],
    'min_child_weight': [1, 3, 5],
    'decay_rate':       [0.5, 0.7, 0.9, 1.0],   # 1.0 = no decay (baseline)
}

FEATURES = [
    # Match context
    'surface_enc', 'tourney_level_enc', 'round_ord', 'best_of',
    # Player A — match-time
    'A_rank', 'A_rank_pts', 'A_seed', 'A_age', 'A_ht', 'A_h2h', 'hand_A_L',
    # Player B — match-time
    'B_rank', 'B_rank_pts', 'B_seed', 'B_age', 'B_ht', 'B_h2h', 'hand_B_L',
    # H2H context
    'days_since_h2h',
    # Matchup comparison (derived)
    'rank_diff', 'rank_pts_diff',
    # Player A — lagged surface stats
    'win_rate_A', 'completed_winrate_A', 'strsets_rate_A', 'tiebreaks_winrate_A',
    'rank_improvement_A', 'injured_during_swing_A', 'matches_played_A',
    'ace_rate_A', 'df_rate_A', 'first_serve_pct_A', 'first_serve_win_pct_A',
    'second_serve_win_pct_A', 'bp_save_pct_A', 'sv_gms_won_pct_A', 'rtn_win_pct_A',
    # Player B — lagged surface stats
    'win_rate_B', 'completed_winrate_B', 'strsets_rate_B', 'tiebreaks_winrate_B',
    'rank_improvement_B', 'injured_during_swing_B', 'matches_played_B',
    'ace_rate_B', 'df_rate_B', 'first_serve_pct_B', 'first_serve_win_pct_B',
    'second_serve_win_pct_B', 'bp_save_pct_B', 'sv_gms_won_pct_B', 'rtn_win_pct_B',
]


def load_splits(path: Path) -> tuple:
    """Load dataset and split into train (2019-2023) and val (2024).

    Args:
        path: Path to model_dataset.csv.
    Returns:
        Tuple (X_train, X_val, y_train, y_val, train_years).
    """
    df = pd.read_csv(path)
    train = df[df['year'].isin(TRAIN_YEARS)]
    val   = df[df['year'].isin(VAL_YEARS)]
    return (
        train[FEATURES], val[FEATURES],
        train['label'],  val['label'],
        train['year'],
    )


def _compute_weights(years: pd.Series, decay_rate: float) -> np.ndarray:
    """Compute exponential recency weights so recent matches matter more.

    Most recent training year gets weight 1.0; each prior year is
    multiplied by decay_rate. decay_rate=1.0 means equal weights.

    Args:
        years: Series of match years for training rows.
        decay_rate: Per-year decay factor in (0, 1].
    Returns:
        numpy array of sample weights, same length as years.
    """
    return decay_rate ** (years.max() - years).values


def _fit_candidate(
    params: dict, X_tr, y_tr, X_val, y_val, sample_weight=None
) -> tuple:
    """Fit one XGBoost candidate and return its val log-loss and model.

    Args:
        params: XGBoost hyperparameter dict (merged with BASE_PARAMS and FIXED_PARAMS).
        X_tr, y_tr: Training data.
        X_val, y_val: Validation data for early stopping.
        sample_weight: Optional per-sample weights for training rows.
    Returns:
        Tuple (val_logloss, fitted_model).
    """
    model = xgb.XGBClassifier(**{**BASE_PARAMS, **FIXED_PARAMS, **params})
    model.fit(
        X_tr, y_tr,
        sample_weight=sample_weight,
        eval_set=[(X_val, y_val)],
        verbose=False,
    )
    return model.best_score, model


def grid_search(
    X_train: pd.DataFrame, y_train: pd.Series,
    X_val:   pd.DataFrame, y_val:   pd.Series,
    train_years: pd.Series,
) -> tuple:
    """Grid search over PARAM_GRID including decay_rate, scored on val log-loss.

    decay_rate is extracted before passing params to XGBClassifier and used
    to compute exponential recency weights via _compute_weights.

    Args:
        X_train, y_train: Training data.
        X_val, y_val: Validation data.
        train_years: Year of each training row (for weight computation).
    Returns:
        Tuple (best_params_dict, best_model, results_df).
    """
    keys   = list(PARAM_GRID.keys())
    combos = list(itertools.product(*PARAM_GRID.values()))
    total  = len(combos)
    print(f'Grid search: {total} combinations')

    results, best_loss, best_params, best_model = [], float('inf'), None, None
    for i, vals in enumerate(combos, 1):
        params      = dict(zip(keys, vals))
        decay_rate  = params.pop('decay_rate')
        weights     = _compute_weights(train_years, decay_rate)
        loss, model = _fit_candidate(params, X_train, y_train, X_val, y_val, weights)
        results.append({**params, 'decay_rate': decay_rate,
                        'val_logloss': loss, 'best_iter': model.best_iteration})
        if loss < best_loss:
            best_loss   = loss
            best_params = {**params, 'decay_rate': decay_rate}
            best_model  = model
        if i % 12 == 0 or i == total:
            print(f'  {i}/{total}  best so far: {best_loss:.4f}')

    results_df = pd.DataFrame(results).sort_values('val_logloss').reset_index(drop=True)
    return best_params, best_model, results_df


def evaluate(
    model: xgb.XGBClassifier,
    X: pd.DataFrame, y: pd.Series,
    split_name: str,
) -> dict:
    """Compute and print accuracy, AUC, log-loss, and Brier score.

    Args:
        model: Fitted XGBClassifier.
        X: Feature matrix.
        y: True labels.
        split_name: Label for printed output.
    Returns:
        Dict of metric name → value.
    """
    prob = model.predict_proba(X)[:, 1]
    pred = (prob >= 0.5).astype(int)
    metrics = {
        'accuracy':    accuracy_score(y, pred),
        'roc_auc':     roc_auc_score(y, prob),
        'log_loss':    log_loss(y, prob),
        'brier_score': brier_score_loss(y, prob),
    }
    print(f'\n── {split_name} ─────────────────────────')
    for name, val in metrics.items():
        print(f'  {name:<14} {val:.4f}')
    return metrics


def feature_importance(model: xgb.XGBClassifier, top_n: int = 20) -> pd.DataFrame:
    """Print and return top-N features sorted by XGBoost gain.

    Args:
        model: Fitted XGBClassifier.
        top_n: Number of features to display.
    Returns:
        DataFrame sorted by gain descending.
    """
    scores = model.get_booster().get_score(importance_type='gain')
    imp = (
        pd.DataFrame({'feature': list(scores.keys()), 'gain': list(scores.values())})
        .sort_values('gain', ascending=False)
        .reset_index(drop=True)
    )
    print(f'\n── Top {top_n} features by gain ──────────────────')
    print(imp.head(top_n).to_string(index=False))
    return imp


def save_outputs(
    model: xgb.XGBClassifier,
    imp: pd.DataFrame,
    best_params: dict,
    grid_results: pd.DataFrame,
) -> None:
    """Save model, feature importance, best params, and full grid results.

    Args:
        model: Best fitted XGBClassifier.
        imp: Feature importance DataFrame.
        best_params: Best hyperparameter dict.
        grid_results: Full grid search results DataFrame.
    """
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model.save_model(MODEL_DIR / 'xgb_model.json')
    imp.to_csv(MODEL_DIR / 'feature_importance.csv', index=False)
    grid_results.to_csv(MODEL_DIR / 'grid_search_results.csv', index=False)
    with open(MODEL_DIR / 'best_params.json', 'w') as f:
        json.dump({**BASE_PARAMS, **best_params}, f, indent=2)
    print('\nSaved: xgb_model.json, feature_importance.csv, '
          'grid_search_results.csv, best_params.json')


if __name__ == '__main__':
    X_train, X_val, y_train, y_val, train_years = load_splits(
        PROC_DIR / 'model_dataset.csv'
    )
    print(f'Train: {len(X_train):,}  Val: {len(X_val):,}')
    print('Year weights (decay previewed at each decay_rate candidate):')
    for dr in PARAM_GRID['decay_rate']:
        w = _compute_weights(train_years, dr)
        yr_mean = train_years.groupby(train_years).apply(lambda _: None)
        by_yr = {yr: round(dr ** (train_years.max() - yr), 3)
                 for yr in sorted(train_years.unique())}
        print(f'  decay={dr}: {by_yr}')

    best_params, best_model, grid_results = grid_search(
        X_train, y_train, X_val, y_val, train_years
    )

    print('\n── Best hyperparameters ──────────────────')
    for k, v in best_params.items():
        print(f'  {k:<22} {v}')

    evaluate(best_model, X_train, y_train, 'Train 2019-2023')
    evaluate(best_model, X_val,   y_val,   'Val   2024')

    imp = feature_importance(best_model)
    save_outputs(best_model, imp, best_params, grid_results)
