"""Patient-grouped nested Ridge probing; users must supply regularization grid."""
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold, GridSearchCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from .metrics import global_age_r2


def crossfit_age(features, age, patient_groups, *, alphas, outer_folds=5, inner_folds=4):
    """Fit transforms within inner/outer training folds; pool outer predictions.

    The supplied grid/folds are a user configuration, not undisclosed paper seeds.
    Rows are ECGs; all ECGs of a patient remain in the same outer and inner fold.
    """
    x, y, g = np.asarray(features, float), np.asarray(age, float), np.asarray(patient_groups)
    if x.ndim != 2 or y.ndim != 1 or g.ndim != 1 or len(x) != len(y) or len(y) != len(g):
        raise ValueError("Expected aligned features [N,D], age [N], groups [N]")
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError("Features and ages must be finite")
    if outer_folds < 2 or inner_folds < 2 or len(np.unique(g)) < outer_folds:
        raise ValueError("Insufficient groups or invalid folds")
    grid = np.asarray(alphas, float)
    if grid.ndim != 1 or not len(grid) or not np.isfinite(grid).all() or np.any(grid <= 0):
        raise ValueError("Supply positive finite Ridge alphas explicitly")
    oof = np.full(len(y), np.nan)
    fold_id = np.full(len(y), -1, dtype=int)
    selected = []
    for fold, (train, test) in enumerate(GroupKFold(outer_folds).split(x, y, g)):
        if len(np.unique(g[train])) < inner_folds:
            raise ValueError("Too few training groups for inner CV")
        search = GridSearchCV(make_pipeline(StandardScaler(), Ridge()),
                              {"ridge__alpha": grid.tolist()},
                              cv=GroupKFold(inner_folds), scoring="neg_mean_squared_error",
                              n_jobs=1, error_score="raise")
        search.fit(x[train], y[train], groups=g[train])
        oof[test] = search.predict(x[test])
        fold_id[test] = fold
        selected.append(float(search.best_params_["ridge__alpha"]))
    return {"global_age_r2": global_age_r2(y, oof), "oof_prediction": oof,
            "outer_fold": fold_id, "selected_alphas": selected}
