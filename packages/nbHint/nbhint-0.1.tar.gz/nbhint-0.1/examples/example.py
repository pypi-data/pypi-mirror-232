from nbhint import nbhint

nb_path = "H:\\py_projects\\nbHint\\examples\\examples.ipynb"

nb_cells = nbhint.Parser(nb_path=nb_path)
print(nb_cells)

curr_cell = nb_cells.get_cell_by_id('cell-4119246836a38e04')
curr_cell.check_if(only_if=True)


