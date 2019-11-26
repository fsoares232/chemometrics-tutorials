import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objs as go


def manhattan_plot(pvalues, beta, sig=0.05, xvalues=None):
    """

    :param np.ndarray pvalues: Numpy array with the p-values. These can also be adjusted, or fdr corrected/estimates
    :param np.ndarray beta: Numpy array with the regression coefficients or other effect size estimate.
    :param float sig: Significance value to plot
    :param np.ndarray xvalues: Variable names
    :return: Matplotlib figure with the Manhattan plot
    """

    logged_p = -np.log10(pvalues)
    plt.figure()
    plt.title("Manhattan plot")
    plt.ylabel(r"Sign($\beta$) $\times$ - $log_{10}$p-value")
    plt.xlabel("$\delta$ppm")
    if xvalues is None:
        xvalues = np.arange(pvalues.size)
    plt.scatter(xvalues, np.sign(beta) *logged_p, s=10, c=beta)
    plt.axhline(-np.log10(sig), linestyle='--')
    plt.axhline(- 1*-np.log10(sig), linestyle='--')

    # plt.plot(np.mean(X, axis=0).T)
    plt.colorbar()
    plt.gca().invert_xaxis()
    plt.show()


def interactive_manhattan(pvalues, beta, sig=0.05, xvalues=None):
    """

    :param np.ndarray pvalues: Numpy array with the p-values. These can also be adjusted, or fdr corrected/estimates
    :param np.ndarray beta: Numpy array with the regression coefficients or other effect size estimate.
    :param float sig: Significance value to plot
    :param np.ndarray xvalues: Variable names
    :return: Data structure ready for interactive plotting with plotly
    """

    data = []

    if xvalues is None:
        xvalues = np.arange(pvalues.size)

    logged_p = -np.log10(pvalues)
    yvals = np.sign(beta) * logged_p

    W_str = ["%.4f" % i for i in beta]  # Format text for tooltips
    maxcol = np.max(abs(beta))

    Xvals = xvalues
    hovertext = ["ppm: %.4f; W: %s" % i for i in zip(Xvals, W_str)]  # Text for tooltips

    point_text = ["p-value: " + pval for pval in pvalues.astype(str)]

    manhattan_scatter = go.Scattergl(
        x=Xvals,
        y=yvals,
        mode='markers',
        marker=dict(color=beta, size=5, colorscale='RdBu',
                    cmin=-maxcol, cmax=maxcol, showscale=True),
        text=point_text)

    data.append(manhattan_scatter)

    xReverse = 'reversed'
    Xlabel = chr(948) + 'ppm 1H'
    Ylabel = r"Sign($\beta$) $\times$ - $log_{10}$p-value"

    # Add annotation
    layout = {
        'xaxis': dict(
            title=Xlabel,
            autorange=xReverse),
        'yaxis': dict(title=Ylabel),
        'title': 'Manhattan plot',
        'hovermode': 'closest',
        'bargap': 0,
        'barmode': 'stack',
        'shapes': [{
            'type': 'line',
            'x0': min(Xvals),
            'y0': np.log10(sig),
            'x1': max(Xvals),
            'y1': np.log10(sig),
            'line': {
                'color': 'rgb(50, 171, 96)',
                'width': 4,
                'dash': 'dashdot'}},
            {
                'type': 'line',
                'x0': min(Xvals),
                'y0': -np.log10(sig),
                'x1': max(Xvals),
                'y1': -np.log10(sig),
                'line': {
                    'color': 'rgb(50, 171, 96)',
                    'width': 4,
                    'dash': 'dashdot'}}]}
    fig = {
        'data': data,
        'layout': layout,
    }

    return fig


def _lineplots(mean, error=None, xaxis=None):

    fig, ax = plt.subplots()
    if xaxis is None:
        ax.plot(mean)
        xaxis = range(mean.size)
    else:
        ax.plot(xaxis, mean)
    if error is not None:
        ax.fill_between(xaxis, mean - error, mean + error, alpha=0.2, color='red')

    return fig, ax


def _barplots(mean, error=None, xaxis=None):

    fig, ax = plt.subplots()
    if xaxis is None:
        xaxis = range(mean.size)

    if error is None:
        ax.bar(xaxis, height=mean)
    else:
        ax.bar(xaxis, height=mean, yerr=error)
    return fig, ax


def _shiftedColorMap(cmap, start=0, midpoint=0.5, stop=1.0, name='shiftedcmap'):
	'''
	From Paul H at Stack Overflow
	http://stackoverflow.com/questions/7404116/defining-the-midpoint-of-a-colormap-in-matplotlib
	Function to offset the "center" of a colormap. Useful for
	data with a negative min and positive max and you want the
	middle of the colormap's dynamic range to be at zero

	Input
	-----
	  cmap : The matplotlib colormap to be altered
	  start : Offset from lowest point in the colormap's range.
		  Defaults to 0.0 (no lower ofset). Should be between
		  0.0 and `midpoint`.
	  midpoint : The new center of the colormap. Defaults to
		  0.5 (no shift). Should be between 0.0 and 1.0. In
		  general, this should be  1 - vmax/(vmax + abs(vmin))
		  For example if your data range from -15.0 to +5.0 and
		  you want the center of the colormap at 0.0, `midpoint`
		  should be set to  1 - 5/(5 + 15)) or 0.75
	  stop : Offset from highets point in the colormap's range.
		  Defaults to 1.0 (no upper ofset). Should be between
		  `midpoint` and 1.0.
	'''
	cdict = {
		'red': [],
		'green': [],
		'blue': [],
		'alpha': []
	}

	# regular index to compute the colors
	reg_index = np.linspace(start, stop, 257)

	# shifted index to match the data
	shift_index = np.hstack([
		np.linspace(0.0, midpoint, 128, endpoint=False),
		np.linspace(midpoint, 1.0, 129, endpoint=True)
	])

	for ri, si in zip(reg_index, shift_index):
		r, g, b, a = cmap(ri)

		cdict['red'].append((si, r, r))
		cdict['green'].append((si, g, g))
		cdict['blue'].append((si, b, b))
		cdict['alpha'].append((si, a, a))

	newcmap = matplotlib.colors.LinearSegmentedColormap(name, cdict)
	plt.register_cmap(cmap=newcmap)

	return newcmap

