# VFR
Simple shatter script for Maya. SOuP or VFR(Voronoi algorithm)

**For use "SOuP FAST" install SOuP ( www.soup-dev.com ) it not free or use old version**

If you use Maya 2016.5, 2017:

1. Coppy VFR.py in to Maya scripts folder (ex. C:\Users\user_name\Documents\maya\2017\prefs\scripts)
2. In Maya Script Editor (Python tab) use command:
```python
import VFR
VFR.initUI()
```

3. Save Script to Shelf...
4. Watch video instruction how to use this script - [link](https://www.youtube.com/watch?v=I17AOtr-5D4)


For Maya 2016 and old: 
copy VFR_old.py and use command
```python
import VFR_old as vfr
reload(vfr)
vfr.initUI()
```
*VFR_old tested in Maya 2016*
