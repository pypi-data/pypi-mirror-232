import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import StratifiedShuffleSplit, train_test_split
from sklearn.metrics import roc_auc_score
from rsidatasciencetools.datautils.collections_data import CaseGenerator


def test_case_generator():
    cases = CaseGenerator(seed=42)

    df = pd.DataFrame([cases.get_sample() for r in range(100)])

    for col in [c for c in df.columns if '_payments_' in c]:
        if '90' in col:
            assert ((0 <= df[col].values) & (df[col].values <= 3)).all()
        elif '120' in col:
            assert ((0 <= df[col].values) & (df[col].values <= 6)).all()
        elif '360' in col:
            assert ((0 <= df[col].values) & (df[col].values <= 12)).all()
    

def test_collections_model_build(debug=0):
    cases = CaseGenerator(seed=42)
    df = pd.DataFrame([cases.get_sample() for r in range(1000)])

    for new, lt, ot in zip(
            ['ratio_late2ontime_90days','ratio_late2ontime_180days','ratio_late2ontime_360days'],
            ['late_payments_90days','late_payments_180days','late_payments_360days'],
            ['ontime_payments_90days','ontime_payments_180days','ontime_payments_360days']):
        df[new] = df[lt].values/np.maximum(1,df[ot].values)

    df['has_used_payment_plan'] = df.has_used_payment_plan.astype(int).values
    cols = ['ratio_late2ontime_90days','ratio_late2ontime_180days','ratio_late2ontime_360days',
            'od_90days','od_180days','od_360days','od_now','has_used_payment_plan',
            'contact_90days','contact_180days','contact_360days', 'no_accts']
    X, y = df[cols].values, df['target_resolved'].values

    gbm = GradientBoostingClassifier(
        loss='log_loss',
        learning_rate=0.1,
        n_estimators=200,
        subsample=1.0,
        criterion='friedman_mse',
        min_samples_split=2,
        min_samples_leaf=1,
        min_weight_fraction_leaf=0.0,
        max_depth=5,
        min_impurity_decrease=0.0,
        init=None,
        random_state=np.random.RandomState(seed=42),
        max_features=None,
        verbose=0,
        max_leaf_nodes=None,
        warm_start=False,
        validation_fraction=0.1,
    )

    X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.33, random_state=43, stratify=y)


    gbm.fit(X_train, y_train)
    train_perf, test_perf = gbm.score(X_train, y_train), gbm.score(X_test, y_test)
    train_auc, test_auc = roc_auc_score(y_train, gbm.predict_proba(X_train)[:,1]), roc_auc_score(
        y_test, gbm.predict_proba(X_test)[:,1])
    print(f'train_perf:{train_perf:.3f}, test_perf:{test_perf:.3f}, train_auc:{train_auc:.3f}, test_auc:{test_auc:.3f}')

    assert all(0.9 < perf <= 1.0 for perf in [train_perf, test_perf, train_auc, test_auc])

    if debug:
        from sklearn.metrics import RocCurveDisplay, roc_curve
        from matplotlib import pyplot as plt
        _, ax = plt.subplots(1,1)
        for split, _y, _X in zip(['train', 'test'], [y_train, y_test], [X_train, X_test]):
            y_score = gbm.predict_proba(_X)
            fpr, tpr, thresh = roc_curve(_y, y_score[:,1])
            auc = roc_auc_score(_y, y_score[:,1])
            ax.plot(fpr,tpr,label=f"{split}: AUC={auc:.4g}",linewidth=2)


        ax.plot([0,1],[0,1],'k--',label=f"Chance level: AUC={0.5}",linewidth=2)
        ax.axis("square")
        ax.set_xlabel("False Positive Rate")
        ax.set_ylabel("True Positive Rate")
        ax.set_title("ROC")
        ax.legend()
        plt.show()