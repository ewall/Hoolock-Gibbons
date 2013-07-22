Hoolock-Gibbons
===============

## About

We employ Hoolock-Gibbons to munge HULOCK snapshot logs taken every 5 minutes into data we can get useful statistics and charts from.

If you don't know what HULOCK is you probably don't care about it. The logs are orderly but chunky, so this bit o' Python is tightly coupled with that format.

Oh, and this program doesn't really have anything to do with [hoolock gibbons](https://en.wikipedia.org/wiki/Hoolock_gibbon). But they're so cute! Here's a picture to prove it: 

![hoolock gibbon just hanging out](http://www.birding2asia.com/InFocus/photos/HoolockGibbon1.jpg-for-web-LARGE.jpg "Western Hoolock Gibbon")


## License
Copyright 2013 Eric W. Wallace / MaineHealth

> This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

> This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

> You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.


## Requirements
- a bunch of log files in this very particular format
- Python 2.7 with NumPy, pandas, matplotlib… *or* [Enthought Canopy](https://www.enthought.com/products/canopy/)


## Usage
- hulock_logging_script.m: edit paths as appropriate, paste into Caché prompt, leave session open to log every 5 minutes
- renameLogs.py: rename from old unsortable names
- importFiles.py: read in the logs and build a DataFrame


## TO DO
- [x] rename files
- [x] import/build DataFrame
- [x] save DataFrame in a reusable format
- [ ] first set of stats & charts
- [ ] dig deeper into outliers
- [ ] edit M script to use ISO date format
