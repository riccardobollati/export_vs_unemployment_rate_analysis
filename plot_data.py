import matplotlib.pyplot as plt
from sklearn import preprocessing
import seaborn as sns

def plot_series(country, normalized, df, cat_map):
    """
    plot the cuntries unemploynment vs its exports divided by category
    along with respective correlation as heatmap
    """

    df_to_plot = df.loc[df['country'] == country]
    
    fig, ax = plt.subplots(1,2,figsize=(20,8))

    ax[0].set_xlabel('year')
    ax[0].set_ylabel('unemployment')
    
    if normalized:
        normalized_data = preprocessing.normalize([df_to_plot['value']])
        ax[0].plot(df_to_plot['year'], normalized_data[0], linewidth=3, ls = '--')
        
    else:
        ax[0].plot(df_to_plot['year'], df_to_plot['value'], linewidth=3, ls = '--')

    ax2 = ax[0].twinx()
    ax2.set_ylabel('exports')

    cmap = plt.get_cmap('tab10')
    colors = [cmap(i/5) for i in range(1,6)]

    for cat, color in zip(df_to_plot.iloc[:,2:7], colors):
        if normalized:
            
            normalized_data = preprocessing.normalize([df_to_plot[cat][df_to_plot[cat].notna()]])
            ax2.plot(df_to_plot['year'][df_to_plot[cat].notna()], normalized_data[0], label = f"({cat}) {cat_map[cat]['description']}", color = color)
        
        else:
            ax2.plot(df_to_plot['year'], df_to_plot[cat], label = f"({cat}) {cat_map[cat]['description']}", color = color)
        
    plt.legend(title = 'exports categories', title_fontproperties = {'weight' : 'bold'})
    
    fig.tight_layout()
    
    data_columns = ['value', '205', '236', '245', '253', '268']
    corr_mat = df_to_plot[data_columns].corr()
    sns.heatmap(corr_mat, ax=ax[1], annot = True, cmap = 'viridis', vmin = -1.0, vmax = 1.0)
    ax[1].set_title('correlation', weight  = 'heavy', size = 20)