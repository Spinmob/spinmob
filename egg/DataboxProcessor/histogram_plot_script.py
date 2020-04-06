##########################################
# Histogram DataboxProcessor Plot Script #
##########################################

# List of datasets you'd like to plot, e.g. 'V1' (not 'V1.values', 'V1.counts', etc)
plot_columns = []

# Leaving plot_columns = [] will plot them all.

##############################
# No need to edit below this #
##############################
x = None
y = []

# If none are supplied, get them all!
if plot_columns==None or len(plot_columns) == 0:
  for n in range(len(d.ckeys)):
    k = d.ckeys[n]
    if k[len(k)-7:] == '.values': 
      plot_columns.append(k[0:len(k)-7])

# Now generate the data to plot and axes labels
x  = []
y  = []
ey = []
xlabels = []
ylabels = []
for k in plot_columns:
  
  # Data to plot
  x.append(d[k+'.values'])
  y.append(d[k+'.counts'])
  if k+'.counts.std_mean' in d.ckeys:
    ey.append(d[k+'.counts.std_mean'])

  # Axes labels
  xlabels.append(k)
  ylabels.append(k+'.counts')

# If we have no ey's, kill em so the script doesn't crash.
if len(ey) == 0: ey = None
