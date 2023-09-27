# pathxf

Pathxf is a minimally viable tool for renaming large numbers of files based on a flexible yaml schema. As of now, the schema is provisional and could be changed. In it's current state, the tool only makes symlinks from dest to source files, and takes only minimal precautions for failure modes (e.g. it doesn't expect the filesystem to change via outside sources while it's running, and it's probably not robust to interruptions and restarts). No checks are made for multiple files given the same name. Loops, swaps, and chains are not supported. In other words, all input and output files must have unique names. 

Those stumbling across this library will not find it in a ready-to-use state, but feel free to adapt the source to your own needs.