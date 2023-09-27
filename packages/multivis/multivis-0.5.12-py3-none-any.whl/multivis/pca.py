import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import seaborn as sns

def pca(data, imageFileName='PCA.png', saveImage=True, dpi=200, pcx=1, pcy=2, group_label=None, sample_label=None, peak_label=None, markerSize=100, fontSize=12, figSize=(20,10), background_colour='white', grid=True, transparent=False, cmap='Set1'):
    """Creates a Principal Component Analysis (PCA) scores and loadings plot.

    Parameters
    -------------------
    data: array-like, shape (n_samples, n_features)
    imageFileName: The image file name to save to (default: 'PCA.png')
    saveImage: Setting to 'True' will save the image to file (default: True)
    dpi: The number of Dots Per Inch (DPI) for the image (default: 200)
    pcx: The first component (default: 1)
    pcy: The second component (default: 2)
    group_label: Labels to assign to each group/class in the PCA plot (default: None)
    sample_label: Labels to assign to each sample in the PCA plot (default: None)
    peak_label: Labels to assign to each peak in the loadings biplot (default: None)
    markerSize: The size of each marker (default: 100)
    fontSize: The font size for all text (default: 12)
    figSize: The figure size as a tuple (width,height) (default: (20,10))
    background_colour: Set the background colour (default: 'white')
    grid: Setting to 'True' will overlay a grid (default: True)
    transparent: Setting to 'True' will ignore background_colour and make the background transparent (default: False)
    cmap: The CMAP colour palette to use (default: 'Set1')
    """

    # Set model
    model = PCA()
    model.fit(data)
    scores = model.transform(data)
    explained_variance = model.explained_variance_ratio_ * 100

    # Extract scores, explained variance, and loadings for pcx and pcy
    x_score = scores[:, (pcx - 1)]
    y_score = scores[:, (pcy - 1)]
    x_expvariance = explained_variance[(pcx - 1)]
    y_expvariance = explained_variance[(pcy - 1)]
    x_load = model.components_[(pcx - 1), :]
    y_load = model.components_[(pcy - 1), :]

    # Set the background colour
    plt.rcParams['figure.facecolor'] = background_colour

    fig, (ax1, ax2) = plt.subplots(ncols=2, sharey=True, figsize=figSize)

    if grid:
        ax1.grid(True)
        ax2.grid(True)
    else:
        ax1.grid(False)
        ax2.grid(False)

    # Scores plot
    ax1.set_title("PCA Scores Plot", fontsize=fontSize)

    ax1.set_xlabel("PC {} ({:0.1f}%)".format(pcx, x_expvariance), fontsize=fontSize)
    ax1.set_ylabel("PC {} ({:0.1f}%)".format(pcy, y_expvariance), fontsize=fontSize)

    ax1.tick_params(labelsize=fontSize)

    if np.array(sample_label).any() != None:
        for i, txt in enumerate(list(sample_label)):
            ax1.annotate(txt, (x_score[i]+.04, y_score[i]), fontsize=fontSize)

    score_plot = sns.scatterplot(x=x_score, y=y_score, hue=group_label, s=markerSize, style=group_label, ax=ax1, alpha=0.7, palette=cmap)
    score_plot.legend(fontsize=fontSize)

    # Loadings plot
    ax2.set_title("PCA Loadings Plot", fontsize=fontSize)

    ax2.set_xlabel("PC{} ({:0.1f}%)".format(pcx, x_expvariance), fontsize=fontSize)
    ax2.set_ylabel("PC{} ({:0.1f}%)".format(pcy, y_expvariance), fontsize=fontSize)

    ax2.tick_params(labelsize=fontSize)

    if list(peak_label) != None:
        for i, txt in enumerate(list(peak_label)):
            ax2.annotate(txt, (x_load[i]+.001, y_load[i]), fontsize=fontSize)

    sns.scatterplot(x=x_load, y=y_load, ax=ax2, s=markerSize, alpha=0.7)

    fig.tight_layout()

    if saveImage:
        fig.savefig(imageFileName, dpi=dpi, transparent=transparent)