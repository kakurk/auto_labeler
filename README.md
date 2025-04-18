# xnatqa

A workflow built on top of the BOLDQC, ANATQC, yaxil, and xnattager packages from Harvard.

The goal of this workflow is to automatically tag all scans in a newly created scanning session within an XNAT instance as BOLD or ANAT and then automatically launching the BOLDQC and ANATQC routines for the respective scan types.

Please see BOLDQC, ANATQC, yaxil, and xnattager for more information.

BOLDQC and ANATQC are implemented as singularity containers that are housed as modules on the SCC. Recipies for building those containers can be found here and here.