"""Regenerate repository figures and an offline documentation gallery from CSVs.

This reproduces displayed aggregates, not training or patient-level analyses.
"""
import csv
import html
from pathlib import Path
import shutil
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "docs" / "figures"
BLUE, ROSE, INK, GREY = "#1767AE", "#CF4165", "#172B46", "#7C8793"
COHORTS = [("CODE", "CODE-15% · 5 years"), ("MIMIC", "MIMIC-IV-ECG · 90 days")]


def read(name):
    with (ROOT / "results" / name).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def save(fig, name):
    fig.savefig(FIG / (name + ".svg"), bbox_inches="tight", metadata={"Date": None})
    fig.savefig(FIG / (name + ".png"), dpi=170, bbox_inches="tight", metadata={"Software":"ecg-age-retention public renderer"})
    plt.close(fig)


def clean(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(alpha=.25, color="#B0BDC8")
    ax.set_axisbelow(True)


def primary():
    data = read("primary.csv")
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.8), sharex=True, sharey=True)
    for ax, (cohort, label) in zip(axes, COHORTS):
        rows = [r for r in data if r["cohort"] == cohort]
        for i, r in enumerate(rows):
            x, y = float(r["global_age_r2"]), float(r["abs_q75_per_1000"])
            focal = r["encoder"] == "SMS"
            ax.scatter(x, y, s=100 if focal else 48, c=ROSE if focal else BLUE,
                       marker="D" if focal else "o", edgecolor="white", zorder=3)
            offsets = {"CODE": {"byol":(-19,10), "dae":(-22,-5), "vicreg":(2,-14), "mae":(6,5)},
                       "MIMIC": {"dae":(-13,12), "vicreg":(8,-16), "byol":(8,6), "mae":(7,-12), "ssl":(-12,-14)}}
            offset = offsets.get(cohort, {}).get(r["encoder"], (5, 4 if i % 2 else -12))
            ax.annotate(str(i+1), (x, y), xytext=offset, textcoords="offset points", fontsize=9, color=INK,
                        arrowprops={"arrowstyle":"-", "color":"#B0BDC8", "lw":.5} if r["encoder"] in offsets[cohort] else None)
        ax.set_title(label, loc="left", fontweight="bold")
        ax.set_xlabel("Global age-R² (pooled out-of-fold predictions)")
        ax.set_xlim(.32, .85)
        ax.set_ylim(0, 80)
        clean(ax)
    axes[0].set_ylabel("Older-patient absolute risk error |Q≥75| / 1,000")
    names = [r["encoder_label"] for r in data if r["cohort"] == "CODE"]
    fig.text(.09, .04, "    ".join(f"{i+1}. {n}" for i,n in enumerate(names[:5])), fontsize=9)
    fig.text(.09, .005, "    ".join(f"{i+6}. {n}" for i,n in enumerate(names[5:])), fontsize=9)
    fig.suptitle("Age-information retention and subgroup risk error", x=.09, ha="left", fontsize=18, fontweight="bold")
    fig.text(.09, .915, "Ten encoders • PCA-32 survival readout • Point estimates, not causal effects", fontsize=10, color=GREY)
    fig.subplots_adjust(top=.82, bottom=.20, wspace=.15)
    save(fig, "primary_age_risk")


def thresholds():
    data = read("rank_agreement.csv")
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.7), sharex=True, sharey=True)
    for ax, (cohort, label) in zip(axes, COHORTS):
        for excluded, color, marker, name in [("0", BLUE, "o", "All 10 encoders"), ("1", ROSE, "D", "Without age-auxiliary (9)")]:
            rows = [r for r in data if r["cohort"] == cohort and r["exclude_age_auxiliary"] == excluded]
            ax.plot([int(r["age_threshold"]) for r in rows], [float(r["rho_agree"]) for r in rows],
                    color=color, marker=marker, label=name, linewidth=2)
        ax.set_title(label, loc="left", fontweight="bold")
        ax.set_xticks([60,65,70,75,80])
        ax.set_ylim(0,1)
        ax.set_xlabel("Age threshold τ (years; subgroup age ≥ τ)")
        clean(ax)
    axes[0].set_ylabel("Rank agreement ρagree")
    axes[0].legend(frameon=False, loc="lower left")
    fig.suptitle("Age-threshold sensitivity", x=.09, ha="left", fontsize=18, fontweight="bold")
    fig.text(.09, .03, "Overlapping age subgroups; sensitivity analyses are not independent replications. Exact p-values are in the CSV.", fontsize=10, color=GREY)
    fig.subplots_adjust(top=.80, bottom=.21, wspace=.15)
    save(fig, "threshold_sensitivity")


def budgets():
    data = read("budget_selection.csv")
    specs = [("age_r2", "Holdout age-R²", BLUE, "o"), ("rankme", "RankMe", BLUE, "v"),
             ("diagnostic_auroc", "Diagnostic AUROC", BLUE, "P"), ("diagnostic_auprc", "Diagnostic AUPRC", BLUE, "*"),
             ("uno_c", "Uno's C", ROSE, "s"), ("ipcw_brier", "IPCW Brier", ROSE, "^"),
             ("older_abs_bias", "Older |Q|", ROSE, "D"), ("overall_abs_bias", "Full-cohort |Q|", ROSE, "+")]
    fig, axes = plt.subplots(2,2,figsize=(12.5,8.8), sharex=True)
    for rowidx, (cohort, label) in enumerate(COHORTS):
        for col, endpoint in enumerate(["selected_older_error", "selected_uno_c"]):
            ax = axes[rowidx,col]
            for key, title, color, marker in specs:
                rows = sorted([r for r in data if r["cohort"]==cohort and r["endpoint"]==endpoint and r["selector"]==key], key=lambda r:float(r["budget"]))
                x = np.arange(len(rows))
                mean = np.array([float(r["mean"]) for r in rows])
                lo, hi = np.array([float(r["lower"]) for r in rows]), np.array([float(r["upper"]) for r in rows])
                ax.errorbar(x, mean, yerr=np.maximum(0,np.vstack([mean-lo,hi-mean])), color=color, marker=marker,
                            linestyle="--", linewidth=1.6, markersize=5.5, elinewidth=.6, capsize=2,
                            markerfacecolor=color if key=="age_r2" else "white", label=title)
            ax.set_title(label, loc="left", fontweight="bold")
            ax.set_xticks(range(5), ["5", "10", "25", "50", "100"])
            ax.set_ylabel("Selected |Q≥75| / 1,000" if col==0 else "Selected Uno's C")
            ax.set_ylim((0,85) if col==0 else (.68,.81))
            clean(ax)
    for ax in axes[1]:
        ax.set_xlabel("Encoder-selection patient budget (%)")
    handles, labels = axes[0,0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4, bbox_to_anchor=(.5,.018), frameon=False, fontsize=10)
    fig.suptitle("Limited-budget encoder selection", x=.09, ha="left", fontsize=18, fontweight="bold")
    fig.text(.09,.925,"Fixed full-selection-set Cox references • 95% Monte Carlo mean intervals • Uno's C uses a focused vertical scale",fontsize=9.5,color=GREY)
    fig.subplots_adjust(top=.86,bottom=.19,wspace=.21,hspace=.28)
    save(fig, "budget_selection")


def auxiliary():
    data = read("auxiliary_survival.csv")
    fig, axes = plt.subplots(2,2,figsize=(12.5,8.2))
    for ci,(cohort,label) in enumerate(COHORTS):
        base = [r for r in data if r["cohort"]==cohort and r["condition"]=="base_ecg"]
        plus = {r["method_key"]:r for r in data if r["cohort"]==cohort and r["condition"]=="age_aux_ecg"}
        for col,(metric,low,high) in enumerate([("signed_q_per_1000","signed_q_ci_low","signed_q_ci_high"), ("uno_c","uno_c_ci_low","uno_c_ci_high")]):
            ax=axes[ci,col]
            for i,r in enumerate(base):
                r2 = plus[r["method_key"]]
                ax.plot([float(r[metric]),float(r2[metric])],[i,i],color="#C5CCD2",lw=2)
                for offset,record,color,marker,name in [(-.12,r,BLUE,"o","Original objective"),(.12,r2,ROSE,"D","+ auxiliary age")]:
                    val=float(record[metric])
                    ax.errorbar(val,i+offset,xerr=[[val-float(record[low])],[float(record[high])-val]],
                                fmt=marker,color=color,ms=5,elinewidth=.7,capsize=2,label=name if i==0 else None)
            ax.set_yticks(range(6),[r["method"] for r in base]); ax.invert_yaxis()
            ax.set_title(label,loc="left",fontweight="bold")
            ax.set_xlabel("Observed − predicted risk, age ≥75 / 1,000" if col==0 else "Uno's C (focused scale)")
            ax.set_xlim((-5,90) if col==0 else (.66,.82)); clean(ax)
    handles, labels = axes[0,0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=2, bbox_to_anchor=(.5,.065), frameon=False, fontsize=10)
    fig.suptitle("Auxiliary age supervision: artifact-backed paired configurations",x=.09,ha="left",fontsize=17,fontweight="bold")
    fig.text(.09,.925,"Patient-bootstrap 95% intervals for each endpoint; these are not paired-difference intervals.",fontsize=10,color=GREY)
    fig.text(.09,.02,"MIMIC SSL-MAE and DAE show lower Uno's C point estimates with age supervision; historical draft discrepancies are disclosed.",fontsize=9.5,color=GREY)
    fig.subplots_adjust(top=.85,bottom=.20,wspace=.30,hspace=.40)
    save(fig,"auxiliary_survival")


def external():
    data=read("external_auxiliary.csv")
    names={"simclr":"SimCLR","mae":"SSL-MAE","byol":"BYOL","vicreg":"VICReg","dae":"DAE","clocs":"CLOCS-style"}
    fig,axes=plt.subplots(1,3,figsize=(12.5,5.4),sharey=True)
    for ax,metric,title in zip(axes,["age_r2","auroc","auprc"],["Age-R²","Diagnostic AUROC","Diagnostic AUPRC"]):
        rows=[r for r in data if r["metric"]==metric]
        for i,r in enumerate(rows):
            val=float(r["paired_delta"])
            ax.errorbar(val,i,xerr=[[val-float(r["ci_low"])],[float(r["ci_high"])-val]],fmt="D",color=BLUE if val>=0 else ROSE,capsize=3)
        ax.axvline(0,color=GREY,lw=1); ax.set_title(title,loc="left",fontweight="bold");clean(ax)
        ax.set_xlabel("Paired change (+ age − base)")
    axes[0].set_yticks(range(6),[names[r["method"]] for r in rows]);axes[0].invert_yaxis()
    fig.suptitle("Within-cohort training across four external ECG cohorts",x=.09,ha="left",fontsize=17,fontweight="bold")
    fig.text(.09,.895,"Equal cohort averages • 95% paired seed-mean intervals, five seeds • Not cross-cohort encoder transfer",fontsize=10,color=GREY)
    fig.text(.09,.02,"CLOCS-style reuses the SimCLR fallback in three cohorts; diagnostic improvements are not universal.",fontsize=10,color=GREY)
    fig.subplots_adjust(top=.79,bottom=.19,wspace=.23)
    save(fig,"external_auxiliary")


def gallery():
    cards=[("primary_age_risk","Age retention and older-patient risk", "Ten frozen encoders, two independently fitted survival readouts. Point estimates. The primary ρagree values are 0.855 and 0.818; excluding age-auxiliary gives 0.800 and 0.750.","primary.csv"),
           ("threshold_sensitivity","Sensitivity to the older-age threshold","Thresholds define overlapping subgroups. Exact two-sided permutation p-values are unadjusted and available in the downloadable table.","rank_agreement.csv"),
           ("budget_selection","Choosing an encoder with limited selection data","The age selector uses holdout age-R². Budgets restrict selection, not final Cox fitting. Intervals describe Monte Carlo uncertainty across valid repetitions; see CSV denominators. Diagnostic labels in MIMIC are report-derived, not adjudicated.","budget_selection.csv"),
           ("auxiliary_survival","Age supervision: benefit and trade-offs","All six displayed methods have smaller older-patient risk-error point estimates. Uno’s C is not uniformly higher. The artifact-backed SSL-MAE and DAE MIMIC values differ from the historical draft; see the release notes.","auxiliary_survival.csv"),
           ("external_auxiliary","Within-cohort evidence beyond survival data","Encoders are trained within each of four ECG cohorts. Age-information gains coexist with diagnostic trade-offs. These cohorts do not support the survival analyses reported above.","external_auxiliary.csv")]
    sections=[]
    for filename,title,note,csvfile in cards:
        sections.append(f'<section id="{filename}"><p class="eyebrow">RESEARCH SNAPSHOT</p><h2>{html.escape(title)}</h2><p>{html.escape(note)}</p><a href="figures/{filename}.svg"><img src="figures/{filename}.svg" alt="{html.escape(title)}. {html.escape(note)}" loading="lazy"></a><p class="links"><a href="figures/{filename}.svg">SVG figure</a><a href="figures/{filename}.png">PNG figure</a><a href="results/{csvfile}">Aggregate CSV</a></p></section>')
    page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>ECG Age-Retention Audit · Research Snapshot</title><style>
    :root{color-scheme:light;--ink:#172b46;--blue:#1767ae}*{box-sizing:border-box}body{margin:0;background:#f4f7fa;color:var(--ink);font:16px/1.6 system-ui,-apple-system,Segoe UI,sans-serif}header{background:var(--ink);color:#fff;padding:62px 28px}header>div,main{max-width:1120px;margin:auto}h1{font-size:clamp(30px,4vw,51px);line-height:1.12;max-width:900px;margin:18px 0}header p{color:#d3dfeb;max-width:820px}.eyebrow{font-size:12px;letter-spacing:.14em;font-weight:700;color:#65809a}header .eyebrow{color:#aacbe6}.badge{display:inline-block;border:1px solid #587088;padding:4px 12px;border-radius:5px;font-size:12px;margin:8px 7px 0 0}main{padding:28px 18px}nav{display:flex;flex-wrap:wrap;gap:18px;margin:0 0 22px}a{color:var(--blue);text-underline-offset:4px}section{background:white;padding:30px;margin:24px 0;border:1px solid #e0e7ee;border-radius:10px}h2{font-size:25px;line-height:1.25;margin:7px 0 12px}section p{max-width:950px;color:#485c70}img{display:block;width:100%;height:auto;margin:22px 0 10px}.links{display:flex;gap:24px;flex-wrap:wrap;font-size:14px}.notice{border-left:4px solid #cf4165;padding:14px 20px;background:#fff1f5}footer{padding:26px 0;color:#607284;font-size:14px}@media(max-width:600px){header{padding:36px 22px}section{padding:18px}h2{font-size:22px}.links{gap:14px}}
    </style></head><body><header><div><p class="eyebrow">ECG REPRESENTATION EVALUATION / v0.2.0</p><h1>What survives in a frozen ECG representation?</h1><p>Toward Reliable ECG-based Survival Models: Evaluating Age-Information Retention</p><span class="badge">10 survival encoders</span><span class="badge">2 survival cohorts</span><span class="badge">4 within-cohort studies</span><span class="badge">Aggregate results only</span></div></header><main><nav><a href="../README.md">Repository guide</a><a href="METHOD.md">Method</a><a href="REPRODUCIBILITY.md">Reproducibility scope</a><a href="RELEASE_NOTES.md">Evidence notes</a><a href="../results/provenance.json">Provenance</a></nav><p class="notice">Research-use reference release. No patient data or trained weights. This page redraws saved aggregates; it is not an end-to-end reproduction or a clinically validated risk tool.</p>'''
    page = page.replace('href="../README.md"', 'href="https://github.com/tawnymountains/ecg-age-retention"').replace('href="../results/provenance.json"', 'href="results/provenance.json"')
    page += "\n".join(sections) + '<footer>Snapshot: 2026-10-14 · All figures regenerated from bundled aggregate CSVs · No external scripts, fonts, telemetry or automatic network requests.</footer></main></body></html>'
    (ROOT/"docs/index.html").write_text(page,encoding="utf-8")
    (ROOT/"docs/results").mkdir(exist_ok=True)
    for source in (ROOT/"results").iterdir():
        if source.suffix in {".csv", ".json", ".md"}:
            shutil.copyfile(source, ROOT/"docs/results"/source.name)


def main():
    FIG.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"axes.labelcolor":INK,"text.color":INK,
                         "axes.edgecolor":"#8794A0","svg.fonttype":"none","svg.hashsalt":"ecg-audit-v020"})
    for function in [primary,thresholds,budgets,auxiliary,external,gallery]:
        function()
    print("Generated 5 SVGs, 5 PNGs, and docs/index.html from bundled aggregates.")


if __name__=="__main__":
    main()
