"""Optional standardize -> PCA -> standardize -> penalized Cox reference adapter."""
import numpy as np


def fit_cox_reference(features, time, event, *, components, penalty, max_iter, tolerance):
    """No hidden production defaults; fit only on caller-provided development data.

    Use components=32 for the published pipeline family, or None for a new
    direct-feature experiment (not a released result). This does not implement
    the private experiment's complete convergence audit or data partitioning.
    """
    from sklearn.decomposition import PCA
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
    from sksurv.linear_model import CoxPHSurvivalAnalysis
    from sksurv.util import Surv
    x, t, e = np.asarray(features, float), np.asarray(time, float), np.asarray(event)
    if x.ndim != 2 or t.ndim != 1 or e.ndim != 1 or not (len(x) == len(t) == len(e)):
        raise ValueError("Expected aligned feature and survival arrays")
    if not np.isfinite(x).all() or not np.isfinite(t).all() or np.any(t < 0) or not np.isin(e, [0, 1]).all():
        raise ValueError("Invalid features or survival labels")
    if penalty is None or penalty <= 0 or tolerance <= 0 or max_iter < 1:
        raise ValueError("Supply positive penalty, tolerance and max_iter")
    steps = [("scale", StandardScaler())]
    if components is not None:
        if not isinstance(components, int) or not 1 <= components <= min(x.shape):
            raise ValueError("Invalid PCA component count")
        steps += [("pca", PCA(components, svd_solver="full")), ("post_scale", StandardScaler())]
    steps += [("cox", CoxPHSurvivalAnalysis(alpha=penalty, n_iter=max_iter,
                                           tol=tolerance, ties="breslow"))]
    model = Pipeline(steps).fit(x, Surv.from_arrays(e.astype(bool), t))
    if not np.isfinite(model.named_steps["cox"].coef_).all():
        raise RuntimeError("Nonfinite Cox coefficients")
    return model


def predict_event_risk(model, features, *, horizon):
    """P(T <= H) from the fitted baseline; no extrapolation beyond training times."""
    survival = model.predict_survival_function(np.asarray(features, float))
    return np.asarray([1.0 - fn(horizon) for fn in survival])
