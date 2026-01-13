# deltae.py
Analyze dE in text files and images 

## Usage
```
usage: deltae.py [-h] [--checker [{cc24,halfcc,nanocc,halfnanocc,gtdl,gt20,gt10,gt05}]] [--orientation [{S,W,N,E}]] [--deltae [{2k,76}]] [--color COLOR] [--coordinates COORDINATES]
                 testfile

Test color data

positional arguments:
  testfile              File to test

optional arguments:
  -h, --help            show this help message and exit
  --checker [{cc24,halfcc,nanocc,halfnanocc,gtdl,gt20,gt10,gt05}], -c [{cc24,halfcc,nanocc,halfnanocc,gtdl,gt20,gt10,gt05}]
                        Name of checker, supported values: - c24 (classic and mini) - default, - halfcc (lower half of them - grays and BGRYMC), - nanocc (nano version of classic CC), -
                        halfnanocc (lower half - grays and BGRYMC), - gtdl (GoldenThread Device Level), - gt20 (GoldenThread Big), - gt10 (GoldenThread Regular), - gt05 (GoldenThread
                        Small)
  --orientation [{S,W,N,E}], -o [{S,W,N,E}]
                        Orientation of checker: possible values are S, W, N, E (default S) S - in case of CC family greys are at the bottom, in case of GT you can read text normally, W -
                        greys are on the left, N - greys are on the top, E - greys are on the left
  --deltae [{2k,76}], -d [{2k,76}]
                        DeltaE difference according to: - 2k (default) deltaE 2000 (ass. with FADGI) - 76 deltaE 1976 (ass. with Metamorfoze)
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
deltae.py [image]
```
Program recognizes JPG, TIFF, PNG files. By default `deltae.py` verifies against cc24 geometry and values.

Supported checkers are:

- ColorChecker Classic and Mini (+ half, with only 2 rows - greys and BGRYCM)
- ColorChecker Nano (+ half, with only 2 rows - greys and BGRYCM)
- GoldenThread Object Level Big (2.0)
- GoldenThread Object Level Regular (1.0)
- GoldenThread Object Level Mini (0.5)
- GoldenThread Device Level

To prepare image for analysis user must have:

1. Rotate so grey row is at the bottom of file.

2. Crop down files quite precisely:

   - ColorCheckers Classic and Mini: down to crop marks in the corners
   - in case of half versions cut at the + in the middle
   - ColorChecker Nano: crop along physical edges of checker
   - in case of half version cut down along patches with minimal border
   - GoldenThread Big (gt20) and Regular (gt10) crop along outside of yellow border
   - GoldenThread Mini (gt05) and GoldenThread DeviceLevel (gtdl) crop down to black border

