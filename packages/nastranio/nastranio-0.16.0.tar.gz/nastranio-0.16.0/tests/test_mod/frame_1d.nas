SOL SESTATIC 
CEND
  TITLE = LCID1
  ECHO = NONE
  DISPLACEMENT(PLOT) = ALL
  $ SPC = 1
  $ LOAD = 1
SUBCASE 1
  SUBTITLE = LCID#1
  SPC = 1
  LOAD = 1
BEGIN BULK
PARAM,PRGPST,YES
PARAM,POST,-1
PARAM,OGEOM,NO
PARAM,AUTOSPC,YES
PARAM,K6ROT,100.0
PARAM,GRDPNT,0
PARAM,SKIPMGG,YES
PARAM,CHKGRDS,NO
MAT1           17.0000+6             .33  5000.5      0.      0.
MAT1           28.0000+6             .33  5000.5      0.      0.
PBAR           1       1     50.     18.     18.      .1      0.        +
+             0.      0.      0.      0.      0.      0.      0.      0.+
+             0.      0.      0.
PBUSH          2       K  10000.  10000.  10000.  10000.  10000.  10000.+
+                      B                                                +
+                     GE                                                +
+                    RCV
SPC1           1  123456       1       2       3       4
FORCE          1       8       0      1.    100.      0.      0.
FORCE          1       5       0      1.    100.      0.      0.
FORCE          1       6       0      1.    100.      0.      0.
FORCE          1       7       0      1.    100.      0.      0.
GRID           1       0      0.      0.      0.       0
GRID           2       0    -50.      0.      0.       0
GRID           3       0    -50.     30.      0.       0
GRID           4       0      0.     30.      0.       0
GRID           5       0      0.      0.     10.       0
GRID           6       0    -50.      0.     10.       0
GRID           7       0    -50.     30.     10.       0
GRID           8       0      0.     30.     10.       0
CBAR           9       1       1       2      0.      0.      1.
CBAR          10       1       2       3      0.      0.      1.
CBAR          11       1       3       4      0.      0.      1.
CBAR          12       1       4       1      0.      0.      1.
CBAR          17       1       2       6      1.      0.      0.
CBAR          18       1       1       5      1.      0.      0.
CBAR          19       1       4       8      1.      0.      0.
CBAR          20       1       3       7      1.      0.      0.
CBAR          16       1       8       5      0.      0.      1.
CBAR          13       1       5       6      0.      0.      1.
CBAR          14       1       6       7      0.      0.      1.
CBAR          15       1       7       8      0.      0.      1.
ENDDATA