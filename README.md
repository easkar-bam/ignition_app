# Ignition Data Analysis

This repository contains `ign_code.py`, which defines the `ignition` class for loading and analyzing measurement data. It supports adding a time column, plotting data, and calculating maximum slopes using a Savitzky–Golay filter.

## Requirements

Python 3.10 or later is recommended.

Install the required packages from the project directory:

```powershell
python -m pip install -r requirements.txt
```

## Input data

By default, the class reads a semicolon-separated file, uses a comma as the decimal separator, and treats the eighth line as the column header (`hd=7`).

## Usage

```python
from pathlib import Path
from ign_code import ignition

datafile = Path("Datafiles") / "example_data.dat"
data = ignition(datafile)

# Add a time column.
# fq is the sampling frequency in Hz; unit sets the time unit.
data.addtime(fq=1, unit="s")

# Plot column 0 against column 1.
data.ignplot(xcol=0, ycol=1)
```

Adjust the file path and column indices to match your data. The default `ignplot` labels its axes as time and pressure, so change the labels in `ign_code.py` if your plotted data represents something else.

## Calculate maximum slopes

```python
results, target_dpdt, target_x = data.calcslopes(
    na=10,
    ne=100,
    xcol=0,
    ycol=1,
    target=21,
)
```

`calcslopes` checks odd window lengths from `na` to `ne`, inclusive. `target` must be one of those window lengths. The method returns:

- `results`: a pandas DataFrame containing each window length, its maximum slope, and the corresponding x-value
- `target_dpdt`: the maximum slope for the selected window, rounded to two decimal places
- `target_x`: the x-value at which that maximum slope occurs

The window length must be greater than the polynomial order and no larger than the number of data points.