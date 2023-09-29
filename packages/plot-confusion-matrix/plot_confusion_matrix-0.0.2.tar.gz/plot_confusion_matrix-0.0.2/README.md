# Simple confusion matrix

Plot a simple confusion matrix using matplotlib

Usage:
```py
confusion_matrix(matrix, labels)
```
`labels` is optional.
Returns a matplotlib Figure

Example:

```py
from plot_confusion_matrix import confusion_matrix
from matplotlib import pyplot

matrix = [[5, 2, 0],
		  [1, 2, 3],
		  [2, 1, 6]]

confusion_matrix(matrix)
pyplot.show(block=True)
```

Output:

![Result](https://github.com/eduardo-gomes/plot-confusion-matrix/blob/main/img/plot.png?raw=true)

```py
confusion_matrix(matrix, ["A", "B", "C"])
```
![Plot with label](https://github.com/eduardo-gomes/plot-confusion-matrix/blob/main/img/plot_label.png?raw=true)