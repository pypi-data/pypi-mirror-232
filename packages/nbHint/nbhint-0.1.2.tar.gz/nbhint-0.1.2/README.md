# nbHint

## Installation 
nbHint can be installed via pip
```bash 
pip install nbhint
```

## Example

```python 
#import pacakge
from nbHint import nbHint

#parse Jupyter Notebook
nb_path = "PATH/TO/YOUR/NB.ipynb"
nb_cells = nbhint.Parser(nbPath = nb_path)

#exract cell of interest using the unique cell id
curr_cell = nb_cells.get_cell_by_id('cell-4119246836a38e04')

#conduct different checks 
curr_cell.check_for()
curr_cell.check_if(only_if=True)
```
   
For other use cases have a look at the `examples\examples.ipynb`. **Note**: If you change the content of a cell, the notebook hast to be saved before conducting a check.