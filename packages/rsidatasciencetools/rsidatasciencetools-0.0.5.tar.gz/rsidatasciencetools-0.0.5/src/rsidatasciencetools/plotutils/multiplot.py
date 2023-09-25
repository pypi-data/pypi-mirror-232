from matplotlib import pyplot as plt
import numpy as np


def plot_roc_curves(roc_curve_data, auc_data):
    fig, ax = plt.subplots()
    annot_pos = []
    for lbl, roc_data in roc_curve_data.items():
        ax.plot(*roc_data[0][:2],linewidth=2,
                label=f'{lbl.capitalize()} | AUC={auc_data[lbl+"_roc_auc_score"]:.2f}')
        thr = roc_data[0][2]
        subselect = np.arange(len(thr))[
            np.array([(len(thr)-1)*posfrac for posfrac in [0.25,0.5,0.8]],dtype=int)]
        for thres, x, y in zip(thr[subselect],
                                roc_data[0][0][subselect],
                                roc_data[0][1][subselect]):
            pos = np.array([x*0.9,y*1.1])
            if any([np.linalg.norm(pos-prev) < 0.05 for prev in annot_pos]):
                continue
            annot_pos.append(pos)
            ax.annotate(f'thres:{thres:.2f}',pos,fontsize=10,alpha=0.8)
    ax.plot([0,1],[0,1],color='tab:red',linestyle='--',linewidth=2,label='Random')
    ax.plot([0,0,1],[0,1,1],color='k',linestyle=':',linewidth=2,label='Ideal')
    ax.set_title('ROC Curve (missed events vs. false alarms trade-off)',fontsize=14)
    ax.set_xlabel('False positive rate',fontsize=14)
    ax.set_ylabel('True positive rate',fontsize=14)
    ax.legend(fontsize=13)
    return fig, ax