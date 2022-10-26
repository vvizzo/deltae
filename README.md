# deltae.py
Analyze dE in text files and images 

Popular go-to page for checking dE in images is deltae.picturae.com ( https://deltae.picturae.com/ ; later d.p.c).
Sadly, while it is working it was not updated in several years. While new features are not always welcome
it is working with old reference values for X-Rite Colorchecker as for before November 2014:

https://www.xrite.com/pl-pl/service-support/new_color_specifications_for_colorchecker_sg_and_classic_charts

Difference between values for Colorchecker before and after November 2014 is 1.09 dE so while it is not 
distinguishable for human eye it matters when trying to get 4 stars on FADGI scale which require total dE of less
than 3.

Another issue with d.p.c is Lab values of patches. Tested on the same file in Adobe Photoshop 
and in deltae.py script patches have very similar values. Values I got from d.p.c site are different. These 
errors accumulate and in images in difficult lightning conditions final dE differs up to 4 between d.p.c and deltae.py.

## Usage
```
usage: deltae.py [-h] [--checker [{cc24,halfcc,nanocc,gt20,gt10,gt05}]] [--color COLOR] [--coordinates COORDINATES] testfile

Test color data

positional arguments:
  testfile              File to test

optional arguments:
  -h, --help            show this help message and exit
  --checker [{cc24,halfcc,nanocc,gt20,gt10,gt05}], -c [{cc24,halfcc,nanocc,gt20,gt10,gt05}]
                        Name of checker: supported ATM cc24 classic and mini, lower half of them (grays and BGRYMC. Default is cc24.
  --color COLOR         L*a*b* data in file a la CTAGS
  --coordinates COORDINATES, -x COORDINATES
                        File with coordinates of fields in percentages of file (must be in tune with color data)
```

### Text files

  
Program recognizes csv and txt as text files. Expects file in format used by d.p.c.: first 4 lines set-up (ignored by program),
CSV header with 7 fields and later patch fields:
```
cc.jpg
Collected targets/patches

Targettype: CC
Patch,R,G,B,L,a,b
A1,112.3,69.3,51.2,33.53,24.12,22
...
F4,112.3,69.3,51.2,33.53,24.12,22
```
Now program doesn't do format checking so it will exit immediately.

### Image files
```
deltae.py image.jpg
```
Program recognizes JPG, TIFF, PNG files. To prepare image for analysis user must have:

1. Crop down to corner white marks in colorchecker. In case of half of checker use + as mark for top border.
2. Rotate so grey row is at the bottom of file.

