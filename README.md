CSCI 716 Programming Assignment 3
===
By: Alex Monachino, Anjan Maharjan, & Nick Kocela

Usage
---
`python3 main.py <input_file> <x> <y>;`

Step-by-Step
---
When `main.py` is run (as shown in 'Usage'), an input file as well as an `(x, y)` coordinate should be provided.

The `<input_file>` can be `alex.txt` or any other similarly-structured file.

The program will calculate an adjacency matrix and output it to a file. 
The name of this output file mimics the name of the given input file.

`{input-file-name}_output.txt`

Additionally, a traversal path will be printed to standard output, based on the generated rooted directed acyclic graph as well as the provided `(x, y)` coordinate. The traversal path is encoded with letter prefixes and unique integers. `P` represents a left-point, `Q` represents a right-point, `S` represents a line-segment, and `T` represents a trapezoid.

`P1 Q1 S1 P4 T9`

Dependencies
---
Core Python libraries / packages are used. No external libraries or packages are required.