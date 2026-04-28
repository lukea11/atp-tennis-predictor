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

TRAIN_YEARS = [2019, 2020, 2021]
VAL_YEARS   = [2022]
TEST_YEARS  = [2023, 2024]

XGB_PARAMS = {
    'n_estimators':       500,
    'learning_rate':      0.05,
    'max_depth':          5,
    'min_child_weight':   3,
    'subsample':          0.8,
    'colsample_bytree':   0.8,
    'eval_metric':        'logloss',
    'early_stopping_rounds': 30,
    'random_state':       42,
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
    """Load dataset and split into train, validation, and test sets by year.

    Train: 2019-2021 | Val: 2022 (early stopping) | Test: 2023-2024.

    Args:
        path: Path to model_dataset.csv.
    Returns:
        Tuple (X_train, X_val, X_test, y_train, y_val, y_test).
    """
    df = pd.read_csv(path)
    train = df[df['year'].isin(TRAIN_YEARS)]
    val   = df[df['year'].isin(VAL_YEARS)]
    test  = df[df['year'].isin(TEST_YEARS)]
    return (
        train[FEATURES], val[FEATURES], test[FEATURES],
        train['label'],  val['label'],  test['label'],
    )


def train_model(
    X_train: pd.DataFrame, y_train: pd.Series,
    X_val:   pd.DataFrame, y_val:   pd.Series,
) -> xgb.XGBClassifier:
    """Train XGBoost classifier with early stopping on validation set.

    Args:
        X_train: Training features.
        y_train: Training labels.
        X_val: Validation features (used for early stopping only, not test).
        y_val: Validation labels.
    Returns:
        Fitted XGBClassifier.
    """
    model = xgb.XGBClassifier(**XGB_PARAMS)
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=False,
    )
    print(f'Best iteration: {model.best_iteration}  '
          f'val log-loss: {model.best_score:.4f}')
    return model


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
        split_name: Label for printed output (e.g. 'Test 2023-2024').
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
    """Print and return top-N features by XGBoost gain importance.

    Args:
        model: Fitted XGBClassifier.
        top_n: Number of top features to display.
    Returns:
        DataFrame of feature importances sorted by gain descending.
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


def save_model(model: xgb.XGBClassifier, imp: pd.DataFrame) -> None:
    """Save the trained model and feature importance table.

    Args:
        model: Fitted XGBClassifier.
        imp: Feature importance DataFrame.
    """
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model.save_model(MODEL_DIR / 'xgb_model.json')
    imp.to_csv(MODEL_DIR / 'feature_importance.csv', index=False)
    print(f'\nModel saved to models/xgb_model.json')


if __name__ == '__main__':
    X_train, X_val, X_test, y_train, y_val, y_test = load_splits(
        PROC_DIR / 'model_dataset.csv'
    )
    print(f'Train: {len(X_train):,}  Val: {len(X_val):,}  Test: {len(X_test):,}')

    model = train_model(X_train, y_train, X_val, y_val)
    evaluate(model, X_train, y_train, 'Train 2019-2021')
    evaluate(model, X_val,   y_val,   'Val   2022')
    evaluate(model, X_test,  y_test,  'Test  2023-2024')

    imp = feature_importance(model)
    save_model(model, imp)
