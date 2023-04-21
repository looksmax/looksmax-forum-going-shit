
import header, numpy as np, math
import matplotlib.patheffects as PathEffects

def plot_text(axes,collection,boxplot_dict,V_OFFSET,mode=0):

    FONT_SIZE = 8
    STROKE_THICKNESS = 2

    means = [np.mean(np.array(lifespans)) for lifespans in collection]
    axes.scatter(x=range(1, 1+len(collection)), y=means, c='r')

    for i, line in enumerate(boxplot_dict['medians']):
        # get position data for median line
        x1, y1 = line.get_xydata()[0]  # top of median line
        x2, y2 = line.get_xydata()[1]  # top of median line

        valign1 = bit = (mode >> 0) & 1 # 0 = top 1 = bottom
        valign2 = bit = (mode >> 1) & 1 # 0 = top 1 = bottom

        # overlay median value
        txt = axes.text((x1 + x2) / 2, y1 + V_OFFSET * (2*valign1 - 1), 'Median=\n%g' % round(y1,2), horizontalalignment='center',
                verticalalignment='top' if valign1 else 'bottom', fontsize=FONT_SIZE, **header.NARROW_FONT)
        txt.set_path_effects([PathEffects.withStroke(linewidth=STROKE_THICKNESS, foreground='w')])

        y = means[i]
        # overlay mean value
        txt = axes.text((x1 + x2) / 2, means[i] + V_OFFSET * (2*valign2 - 1), 'Mean=\n%g' % round(y,max(1,3-math.floor(math.log10(y)))), horizontalalignment='center',
                verticalalignment='top' if valign2 else 'bottom', fontsize=FONT_SIZE, **header.NARROW_FONT)
        txt.set_path_effects([PathEffects.withStroke(linewidth=STROKE_THICKNESS, foreground='w')])

def stagger(ax): #https://stackoverflow.com/questions/51898101/how-do-i-stagger-or-offset-x-axis-labels-in-matplotlib
    # [1::2] means start from the second element in the list and get every other element
    for tick in ax.xaxis.get_major_ticks()[1::2]:
        tick.set_pad(30)

def color_bar(figure,scatterplot):
    from datetime import datetime
    cbar = figure.colorbar(scatterplot, ticks=header.COLOR_BAR_TICKS_POSITIONS)
    cbar.ax.set_yticklabels([datetime.utcfromtimestamp(epoch).year if not datetime.utcfromtimestamp(
        epoch).year == datetime.utcfromtimestamp(epoch - 60 * 60 * 24).year else '' for epoch in
                             header.COLOR_BAR_TICKS_POSITIONS])
    cbar.ax.set_ylim([header.BINS_SEPARATORS_TIMESTAMPS[0], header.BINS_SEPARATORS_TIMESTAMPS[-1]])
