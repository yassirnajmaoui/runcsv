# runcsv
A library allowing you to use an array of strings as runnable code, opening the door for a fully-featured and hackable spreadsheet software. This means that you can use a CSV file as a dynamic spreadsheet. The example `runcsv-minimal  `  is an example of using a CSV file as input and the output will be the resulting values after running the spreadsheet.

## Structure

The structure of the spreadsheet is divided in 4 layers:

* `s`: This layer is the source, the user input
* `p`: This is the result after parsing the cell in the source layer `s` to generate the runnable python code.
* `o`: This is the resulting object after evaluating the cell in the `p` layer using ``eval`` 
* `f`: This layer is the resulting string after changing the object in `o` into a string using the object's `__str__` function.

Every step from one layer to another is very straight-forward. Any cell is either:

* A String cell (normal cells), which has no "`=`" in the beginning of the cell content
  * The parsed (`p`) layer will contain exactly what the source layer contains
  * The object (`o`) layer will contain the string python object identical to the `p`
  * The final (`f`) layer will also be identical to the `o` layer.
  * This means that all the cells will be unchanged by the spreadsheet
* A command cell, which has a "`=`" in the beginning of the cell.
  * The parsed (`p`) layer will contain the generated python command after replacing the specified references, if given:
    * `*{i,j}` : This will be replaced by the `p` layer of the referenced cell  `i,j` 
    * `{i,j}`: This will be replaced by the `f` layer of the referenced cell `i,j`
  * The object (`o`) layer will contain the python object after running the generated python code in the `p` layer.
  * The final (`f`) layer will contain the string (`__str__`) of the object in the `o` layer

The example driver provided parses the CSV file as source (`s`) layer and outputs the final (`f`) layer as a CSV file.

## User interface

This was designed as the engine for a spreadsheet software in development here

