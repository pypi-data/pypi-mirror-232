import nbformat as nbf
import os
import ast

###################################Vistitor class################################################
class Visitor(ast.NodeVisitor): #helps to walk throug the tree and visit all nodes
    '''
    In this class, a visitor is defined for each method in Python.
    Each visitor only visits those nodes that are needed. For example:
    visit_For only visits those nodes that contain a for argument.
    '''
    def visit_For(self, node: ast.AST):
        '''
        Visits all nodes in the AST. If a visited node contains a for argument, 
        then that node is added to the for_child list. The function returns the list for_child.

        Parameters
        ----------
        self
        node : ast.AST 
             contains the code to be checked as a string.
        
        Returns
        -------
            list
                all for nodes of the tree are in this list.
        '''
        for_child = []
        for child in node.body:
            if isinstance(child,(ast.For)):
                for_child.append(child)
        return for_child
    
    def visit_If(self, node: ast.AST):
        '''
        Visits all nodes in the AST. If a visited node contains a if argument, 
        then that node is added to the if_child list. The function returns the list if_child.

        Parameters
        ----------
        self
        node : ast.AST 
             contains the code to be checked as a string.
        
        Returns
        -------
            list
                all if nodes of the tree are in this list.
        '''
        if_child = []
        for child in node.body:
            if isinstance(child,(ast.If)):
                if_child.append(child)
        return if_child
    
    def visit_Assign(self, node: ast.AST):
        '''
        Visits all nodes in the AST. If a visited node contains a assign argument, 
        then that node is added to the assign_child list. The function returns the list assign_child.

        An assign node is always linked to a variable name. This visitor can be used for variable names, 
        slicing, split and functions such as range, len or np.mean.

        Parameters
        ----------
        self
        node : ast.AST 
             contains the code to be checked as a string.
        
        Returns
        -------
            list
                all assign nodes of the tree are in this list.
        '''
        assign_child = []
        for child in node.body:
            if isinstance(child,(ast.Assign)):
                assign_child.append(child)
        return assign_child

    def visit_Expr(self, node: ast.AST):
        '''
        Visits all nodes in the AST. If a visited node contains a expretion argument, 
        then that node is added to the expr_child list. The function returns the list expr_child.

        Expretion
        ---------
            print()
            append()
            insert()
            remove()

        Parameters
        ----------
        self
        node : ast.AST 
             contains the code to be checked as a string.
        
        Returns
        -------
            list
                all expretion nodes of the tree are in this list.
        '''
        expr_child = []
        for child in node.body:
            if isinstance(child,(ast.Expr)):
                expr_child.append(child)
        return expr_child

    def visit_Import(self, node: ast.AST):
        '''
        Visits all nodes in the AST. If a visited node contains a import argument, 
        then that node is added to the import_child list. The function returns the list import_child.

        Parameters
        ----------
        self
        node : ast.AST 
             contains the code to be checked as a string.
        
        Returns
        -------
            list
                all import nodes of the tree are in this list.
        '''
        import_child = []
        for child in node.body:
            if isinstance(child,(ast.Import)):
                import_child.append(child)
        return import_child
    
    def visit_ImportFrom(self,node:ast.AST):
        '''
        Visits all nodes in the AST. If a visited node contains a import-from argument, 
        which represent the submodules of a module then that node is added to the
        import_from_child list. The function returns the list import_from_child.

        Parameters
        ----------
        self
        node : ast.AST 
             contains the code to be checked as a string.
        
        Returns
        -------
            list
                all submodules of a module in this tree are in this list.
        '''
        import_from_child = []
        for child in node.body:
            if isinstance(child,(ast.ImportFrom)):
                import_from_child.append(child)
        return import_from_child

    def visit_FunctionDef(self, node:ast.AST):
        '''
        Visits all nodes in the AST. If a visited node contains a functiondef argument, 
        then that node is added to the func_child list. The function returns the list func_child.

        Parameters
        ----------
        self
        node : ast.AST 
             contains the code to be checked as a string.
        
        Returns
        -------
            list
                all ifunctiondef nodes of the tree are in this list.
        '''
        func_child = []
        for child in node.body:
            if isinstance(child,(ast.FunctionDef)):
                func_child.append(child)
        return func_child

#############################################Hint####################################################
class Checks():  
    '''
    This class contains checks that check the code from the respective cell. 
    The check consists of checking whether certain requirements are contained in the code.
    '''
    def __init__(self, code_str): 
        '''
        Adopts the code that is to be checked as a string. The code is passed to the AST using ast.parse.
        And is stored in the self.node variable.

        Parameters
        ----------
        self
        code_str : str
            contains the code as a string
        '''
        self.node = ast.parse(code_str)
        self.code = code_str
    
    def __str__(self, ):
        return self.code
    
    def check_for(self):
        '''
        Checks whether a for node exists in the passed code. This is done with check_state. 
        In check_state, all for nodes are stored in a list. It is then checked whether there is 
        at least one entry in this list. If this is the case, the function is terminated and 
        the code is considered correct. If there is no element in the check_state list, a print statement 
        is executed, which indicates that the respective task can be solved using a for loop.

        Parameters
        ----------
        self
        '''
        check_state = Visitor().visit_For(self.node)
        if len(check_state) > 0:
            pass
        else:
            print('Deine Lösung scheint von der Syntax korrekt zu sein!\nAllerdings sieht es so aus als würde der For-Loop fehlen.Schaue dir dazu am besten noch einmal die Theorie an!')

    def check_if(self, only_if = True, with_else = False, with_elif = False):
        '''
        Checks whether an if, else or elif exists in the passed code. What should be checked 
        is specified using the parameters only_if, with_else and with_elif. If only an if statement is checked, 
        then the check_state list has an entry. If this is the case, the method is terminated. 
        If there is no entry in the check_state list, a print statement is used to indicate that this task should be solved using if.
        If an if-esle statement is to be checked, it is checked whether there is an entry in the check_state list. 
        If the check_state list is empty, a print statement is used to indicate that this task can be solved with an if-else statement. 
        If the check_state list is not empty, a query is made for each entry as to whether the orelse list is empty. If this is empty, this entry will be skipped. 
        If the orelse list is not empty, it is appended to the check_else list. If the check_else list is empty, 
        in this case it is pointed out that the checked code contains an if statement but no else statement.
        The checking of an if-elif statement is identical to that of an if-else statement. The difference is that there must be an if node in the orelse list. 
        This is why the visitor is called repeatedly for an if statement (Visitor().visit_if()) to get only the if nodes. If there are no if nodes in the orelse list, 
        a print statement returns that an if statement is defined in the code, but the elif argument is missing.

        It is not possible to check more than one if, else or elif.

        Parameters
        ----------
            self
            only_if : Bool
                Default : False
            with_else : Bool
                Default : False
            with_elif : Bool 
                Default : False
        '''
        check_state = Visitor().visit_If(self.node)
        if only_if == True and (with_else and with_elif) == False:
            if len(check_state) > 0:
                pass
            else: 
                print('Deine Lösung scheint von der Syntax korrekt zu sein!\nAllerdings sieht es so aus als würde die If-Anweisung fehlen.\nSchaue dir dazu am besten noch einmal die Theorie an!')    
        
        elif with_else == True and with_elif == False:
            if len(check_state) > 0:
                check_else = []
                for node in check_state:
                    if node.orelse == []:
                        continue
                    else:
                        check_else.append(node.orelse)
                if len(check_else) == 1 or isinstance(check_else,(ast.If)):
                    pass
                else:
                    print('Deine Lösung scheint von der Syntax korrekt zu sein!\nAllerdings sieht es so aus als verwendest du die If-Anweisung korrekt, allerdings ohne else-Statement.\nSchaue dir dazu am besten noch einmal die Theorie an!')  
            else: 
                print('Deine Lösung scheint von der Syntax korrekt zu sein!\nAllerdings sieht es so aus als würde die If-else-Anweisung fehlen.\nSchaue dir dazu am besten noch einmal die Theorie an!')  
        
        elif with_else == False and with_elif == True:
            if len(check_state) > 0:
                check_elif = []
                for node in check_state:
                    check_elif.append(node.orelse)
                if len(check_elif) == 1:
                    elif_if_node = []
                    for node in check_elif[0]:
                        check_state_elif = Visitor().visit_If(node)
                        elif_if_node.append(check_state_elif)
                    if len(elif_if_node) > 0:
                        pass
                    else: 
                       print('Deine Lösung scheint von der Syntax korrekt zu sein!\nAllerdings sieht es so aus als verwendest du die If-Anweisung korrekt, allerdings ohne elif-Statement.\nSchaue dir dazu am besten noch einmal die Theorie an!')  
                else:
                     print('Deine Lösung scheint von der Syntax korrekt zu sein!\nAllerdings sieht es so aus als verwendest du die If-Anweisung korrekt, allerdings ohne elif-Statement.\nSchaue dir dazu am besten noch einmal die Theorie an!')  
            else:
                print('Deine Lösung scheint von der Syntax korrekt zu sein!\nAllerdings sieht es so aus als würde die If-elif-Anweisung fehlen.\nSchaue dir dazu am besten noch einmal die Theorie an!') 

    def check_varnames(self, var_names:list):
        '''
        Checks whether all variables required for the respective task are included in the code. The check_varnames method is passed 
        a list containing the variable names to be checked as strings. check_state contains all nodes of the AST that contain a variable name. 
        The id (=assigned name of the variable) of each of these nodes is added to the var_list list. 
        This list is compared with the one passed to the method. If all variable names in the varnames list are contained in the var_list list, 
        the function is terminated. If a deviation occurs, a print output will be used to indicate that one or 
        more variables that are required in the specification are missing.

        Parameters
        ----------
        self
        var_names : list
            Contains the variablenames which should be checked as strings.
        '''
        check_state = Visitor().visit_Assign(self.node)
        var_list = []
        for node in check_state:
            var_list.append(node.targets[0].id)
        check = all(item in var_list for item in var_names)
        if check == True:
            pass
        else:
            print('Deine Lösung scheint von der Syntax korrekt zu sein!\nAllerdings sieht es so aus als würde die gefragte Variable aus der Angabe fehlen.\nLies dir die Angabe nocheinmal genau durch, und überprüfe ob du deinen Variablen\ndie korrekten Namen gegeben hast!') 
    
    def check_slicing(self):
        '''
        Checks whether the slicing method was applied. The slicing method occurs in combination with a variable definition. 
        For this reason, all nodes that have a variable name from the AST are required for checking. Each node is checked to see
        whether it has the 'slice' attribute in node.value._fields. If so, that node is added to the slicing list. If 'slice' does not exist, 
        then the respective node is skipped. When all nodes have been checked, the slicing list should have at least one entry.
        If this is not the case, it is pointed out that the slicing method is not used.

        Parameters
        ----------
        self
        '''
        check_state = Visitor().visit_Assign(self.node)
        slicing = []
        for node in check_state:
            if 'slice' in node.value._fields:
                slicing.append(node)
            else:
                continue
        if len(slicing) < 1:
            print('Deine Lösung scheint von der Syntax korrekt zu sein!\nAllerdings sieht es so aus als würde die Slicing-Methode nicht angewandt.\nSchaue dir dazu am besten noch einmal die Theorie an!')

    def check_expr(self,expr:list):
        '''
        Checks whether certain already integrated functions are included in the code. Functions that can be checked with
        this method are: print(), append(), insert() and remove(). The check_expr method is given a list of all the functions that should be checked. 
        The check_state list contains all nodes of the AST that have expressions. Each node is then checked individually. 
        If 'id' exists in node.value.func._fields and matches 'print' then this id will be added to the list expr_list. If 'id' is not contained in node.value.func._fields, 
        then it checks whether node.value.func.attr exists in the node. If this is the case, then the attr is added to the expr_list list.
        When all nodes have been checked, the difference between the expr and expr_list lists is checked. 
        If a difference arises, a print statement will indicate that one or more functions were not used. It also shows which functions these are.

        Parameters
        ----------
        self
        expr : list
            Contains the expretions which should be checked as strings.
        '''
        check_state = Visitor().visit_Expr(self.node)
        expr_list = []
        for node in check_state:
            if 'id' not in node.value.func._fields:
                if node.value.func.attr in expr:#'append' or 'insert' or 'remove':
                    expr_list.append(node.value.func.attr)
                else:
                    pass
            elif (node.value.func.id == 'print'):#and ('id' in node.value.func._fields):
                expr_list.append(node.value.func.id)
        diff = list(set(expr).difference(set(expr_list)))
        if diff != []:
            print('Deine Lösung schein von der Syntax korrekt zu sein!\nAllerdings sieht es so aus als würdest du die Funktion/Funktionen {func} nicht verwenden.\nLies dir die Angabe nocheinmal genau durch und schau dir die Theorie nocheinmal an!'.format(func = diff))
        
    def check_split(self):
        '''
        Checks whether the split method was applied. Split occurs in combination with a variable assignment. 
        Therefore, every node that has a variable is added to the check_state list. It is then checked whether the respective node 
        has 'attr' in node.value.func._fields and whether node.Value.func.attr is equal to 'split'. 
        If so, the node is added to the split_list list. If after checking all nodes the split_list is empty, 
        a print output indicates that the split function was not applied.

        Parameters
        ----------
        self
        '''
        check_state = Visitor().visit_Assign(self.node)
        split_list = []
        for node in check_state:
            if 'func' in node.value._fields:
                if 'attr' in node.value.func._fields and node.value.func.attr == 'split':
                    split_list.append(node)
            else:
                continue
        if len(split_list) == 0:
            print('Deine Lösung scheint von der Syntax korrekt zu sein!\nAllerdings sieht es so aus als würde die Split-Funktion nicht angewandt.\nSchaue dir dazu am besten noch einmal die Theorie an!')
        else:
            pass
 
    def check_assign_func(self, allowed:list, not_allowed:list):
        '''
        Checks whether integrated functions such as range or len appear in the code. Two lists can be passed to the method. 
        One list contains all the functions that are allowed and the other list contains all the functions that are not allowed. 
        Check_state contains all nodes of the AST that could have such a function. Every node is checked whether it 
        has 'func' in node.value._fields and 'id' in node.value.func._fields. The allowed list is then compared with every 
        list that contains the function names of the nodes. If there are any deviations, a print statement is used to indicate 
        that one or more functions are missing in the code. In addition, it also shows which functions they are.
        The same thing happens with the not_allowed list.

        Parameters
        ----------
        self
        allowed : list
            Contains the implemented functions which are allowed as strings.
        not_allowed : list
            Contains the implemented functions which are not allowed as strings.
        '''
        check_state = Visitor().visit_Assign(self.node)
        func_id = []
        for node in check_state:
            if 'func' in node.value._fields and 'id' in node.value.func._fields:
                func_id.append(node.value.func.id)
            elif 'func' in node.value._fields and node.value.func.attr in allowed:
                func_id.append(node.value.func.attr)
            else:
                continue
        check_allowed = list(set(allowed).difference(set(func_id)))
        check_not_allowed = list(set(func_id) & set(not_allowed))
        if len(check_allowed) != 0:
            print('Deine Lösung schein von der Syntax korrekt zu sein!\nAllerdings sieht es so aus als würdest du die Funktion/Funktionen {func} nicht verwenden.\nLies dir die Angabe nocheinmal genau durch und schau dir die Theorie nocheinmal an!'.format(func = check_allowed))
        if len(check_not_allowed) != 0:
            print('Deine Lösung schein von der Syntax korrekt zu sein!\nAllerdings sieht es so aus als würdest du die Funktion/Funktionen {func} verwenden.\nVersuche die Aufgabe ohne dieser Funktion/ diesen Funktionen zu lösen'.format(func = check_not_allowed))

    def check_import(self, allowed:list, not_allowed:list):
        '''
        Checks whether imports exist in the code to be checked or not. The method takes two lists as arguments. 
        One list for those imports that are allowed and the other list for all those imports that are not allowed.
        The check_state list contains all nodes that have an Import or an Import_From. At the beginning it is checked, if the 
        allowed list is empty and the check_state list has at least one entry, a print output indicates that no imports are allowed 
        for this task. However, if there are entries in the allowed list, every node in the check_state list is checked. 
        And added the name of the imported module to the import_list list. If it is a submodule, the name is split at the dot 
        and both parts of the submodule are added to the import_list list. When all nodes have been checked, 
        the difference between allowed and import_list, as well as not_allowed and import_list is taken. If differences occur, 
        a print output will indicate that a module that should have been imported is missing, or that a module that is not allowed 
        to be imported has been imported. This also shows which module it is.

        Parameter
        ---------
        self
        allowed : list
            Contains the imports which are allowed as strings.
        not_allowed : list
            Contains the imports which are not allowed as strings.
        '''
        check_state_import = Visitor().visit_Import(self.node)
        check_state_import_from = Visitor().visit_ImportFrom(self.node)
        check_state = check_state_import + check_state_import_from
        import_list = []
        if allowed == [] and len(check_state) > 0:
            print('Deine Lösung schein von der Syntax korrekt zu sein!\nAllerdings sieht es so aus als würdest du Imports verwenden.\nFür diese Aufgabe sind keine Imports erlaubt. Lies dir die Angabe nocheinmal genau durch und schau dir die Theorie nocheinmal an!')
        elif allowed != []:
            for node in check_state:
                if node.names[0].name in allowed:
                    import_list.append(node.names[0].name)
                elif 'module' in node._fields: 
                    sub_import = node.module.split('.')
                    for i in range(len(sub_import)):
                        import_list.append(sub_import[i])
        check_allowed = list(set(allowed).difference(set(import_list)))
        check_not_allowed = list(set(import_list) & set(not_allowed))
        if len(check_allowed) != 0:
            print('Deine Lösung schein von der Syntax korrekt zu sein!\nAllerdings sieht es so aus als würde einer oder mehrer Imports fehlen.\nLies dir die Angabe nocheinmal genau durch und schau dir die Theorie nocheinmal an!')
        if len(check_not_allowed) != 0:
            print('Deine Lösung schein von der Syntax korrekt zu sein!\nAllerdings sieht es so aus als würdest du die Imports {func} verwenden.\nVersuche die Aufgabe ohne diesen Imports/ diesen Imports zu lösen'.format(func = check_not_allowed))

    def check_function(self,args:list, with_return = False):
        '''
        Checks whether a function has been defined in the code being checked. The method takes as arguments a list
        which contains the names of the arguments of the function to be checked as strings. And the boolean argument
        with_return, which determines whether the function must have a return statement or not. Check_state contains all 
        nodes that have a function. The arguments of the function contained in each node are filtered out and added to 
        the arg_list list. Furthermore, if a return is included, it is added to the return_list. To check whether the 
        correct arguments were used, the difference between the list args and the list arg_list is taken. If there is a difference, 
        it is pointed out that the arguments used are not the ones asked for. It is also checked whether a return statement exists or not. 
        If it should exist but the return_list is empty, it is indicated that the function is still missing a return statement. However, 
        if it was previously defined that no return should be used but the return_list has an entry, it is pointed out that the function must not contain a return.

        Parameter
        ---------
        self
        args : list
            Contains the arguments which should be checked as strings
        with_return : Bool
            Default: with_return = False
        '''
        check_state = Visitor().visit_FunctionDef(self.node)
        arg_list, return_list = [], []
        #Überprüfun ob eine Funktion überhaupt definiert wird
        if len(check_state) > 0:
            pass
        else:
            print('Deine Lösung scheint von der Syntax korrekt zu sein!\nAllerdings sieht es so aus als würdest du keine Funktion zu definieren.Schaue dir dazu am besten noch einmal die Theorie an!')
        for node in check_state:
            #Überprüfung der erforderlichen Argumente:
            if node.args.args[0].arg in args:
                arg_list.append(node.args.args[0].arg)
            #Überprüfung des Return-Statements
            for i in range(len(node.body)):
                if isinstance(node.body[i],(ast.Return)):
                    return_list.append(node.body[i])
        if with_return == True and len(return_list) == 0:
            print('Deine Lösung scheint von der Syntax korrekt zu sein!\nAllerdings sieht es so aus als würdest du eine Funktion ohne return-Statement definieren.\nSchaue dir deinen Code noch einmal genau an und lies noch einmal die Theorie durch!')
        elif with_return == False and len(return_list) > 0:
            print('Deine Lösung scheint von der Syntax korrekt zu sein!\nAllerdings sieht es so aus als würdest du eine Funktion mit return-Statement definieren.\nLies dir die Angabe noch einmal genau durch und schaue dir Theorie nocheinmal an!')
        check_args = list(set(args).difference(set(arg_list)))
        if len(check_args ) != 0:
            print('Deine Lösung scheint von der Syntax korrekt zu sein!\nAllerdings sieht es so aus als würde deine Funktion nicht alle erforderlichen Argummente enthalten.\nSchaue dir die Angabe nocheinmal genau an und lies noch einmal die Theorie durch!')

###########################Gets all the cell contents#######################################
class Parser(): #NBCells
    '''
    Class that extracts the written code from the solution cells.
    '''
    def __init__(self,nb_path=None):
        '''
        Accepts the path and file name. In the self.cells dictionary, 
        all solution cells are. The keys are the cell ids and the values
        are the code as a string.

        Parameter
        ---------
        self
        nb_path : str
            Contains the path as a string
        '''
        self.nb_path = nb_path
        self.get_all_cell_solutions() 
    
    def __str__(self):
        return ",".join(self.cells.keys())
    
#Fügt den Code aller Lösungszellen in dem dict self.cells hinzu. Dabei wird als key die jeweilige grade_id und als value eine Liste der Lösung übergeben. 
#Ein Eintrag der Liste entspricht einer Codezeile der Lösung (erster Eintrag = erste Code Zeile)
    def get_all_cell_solutions(self):
        '''
        Filters out the solution cells from all cells 
        and passes the contents as a string into a dictionary (self.cells) 
        where the key is the respective cell id.

        Parameter
        ---------
        self
        '''
        self.cells = {} 
        
        ntbk = nbf.read(self.nb_path, nbf.NO_CONVERT)
        
        for cell in ntbk.cells:
            if 'nbgrader' not in cell['metadata']: 
                continue
            elif cell['metadata']['nbgrader']['solution'] == True:
                solution_id = cell['metadata']['nbgrader']['grade_id']
                solution = cell['source']
                self.cells[solution_id] = Checks(solution)

    def get_cell_by_id(self, cid):
        '''
        Takes the cell ID as an argument as a string. Is the respective code that is in this cell.

        Parameter
        ---------
        self
        grade_id : str
            Contains the cell id as a string

        Return
        ------
            self.cells[cid] : str
                Contains the code of the cell as a string
        '''
        return self.cells[cid]