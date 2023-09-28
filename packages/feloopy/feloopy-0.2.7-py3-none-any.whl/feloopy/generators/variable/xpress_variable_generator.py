'''
+---------------------------------------------------------+
|  Project: FelooPy (0.2.7)                               |
|  Modified: Wednesday, 27th September 2023 11:36:11 pm   |
|  Modified By: Keivan Tafakkori                          |
|  Project: https://github.com/ktafakkori/feloopy         |
|  Contact: https://www.linkedin.com/in/keivan-tafakkori/ |
|  Copyright 2022 - 2023 Keivan Tafakkori, FELOOP         |
+---------------------------------------------------------+
'''

import xpress as xpress_interface
import itertools as it

sets = it.product

VariableGenerator = xpress_interface.var

INFINITY = xpress_interface.infinity
BINARY = xpress_interface.binary
INTEGER = xpress_interface.integer


def generate_variable(model_object, variable_type, variable_name, variable_bound, variable_dim=0):

    if variable_bound[0] == None:
        variable_bound[0] = -INFINITY

    if variable_bound[1] == None:
        variable_bound[1] = +INFINITY

    match variable_type:

        case 'pvar':

            '''

            Positive Variable Generator


            '''

            if variable_dim == 0:

                GeneratedVariable = VariableGenerator(
                    lb=variable_bound[0], ub=variable_bound[1])

                model_object.addVariable(GeneratedVariable)

            else:

                if len(variable_dim) == 1:

                    GeneratedVariable = [VariableGenerator(
                        lb=variable_bound[0], ub=variable_bound[1]) for key in variable_dim[0]]

                    model_object.addVariable(GeneratedVariable)

                else:

                    GeneratedVariable = {key: VariableGenerator(
                        name=f"{variable_name}{key}", lb=variable_bound[0], ub=variable_bound[1]) for key in sets(*variable_dim)}

                    model_object.addVariable(GeneratedVariable)

        case 'bvar':

            '''

            Binary Variable Generator


            '''

            if variable_dim == 0:

                GeneratedVariable = VariableGenerator(vartype=BINARY)

                model_object.addVariable(GeneratedVariable)

            else:

                if len(variable_dim) == 1:

                    GeneratedVariable = [VariableGenerator(
                        vartype=BINARY) for key in variable_dim[0]]

                    model_object.addVariable(GeneratedVariable)

                else:

                    GeneratedVariable = {key: VariableGenerator(
                        name=f"{variable_name}{key}", lb=variable_bound[0], ub=variable_bound[1], vartype=BINARY) for key in sets(*variable_dim)}

                    model_object.addVariable(GeneratedVariable)

        case 'ivar':

            '''

            Integer Variable Generator


            '''

            if variable_dim == 0:

                GeneratedVariable = VariableGenerator(vartype=INTEGER)

                model_object.addVariable(GeneratedVariable)

            else:

                if len(variable_dim) == 1:

                    GeneratedVariable = {key: VariableGenerator(
                        vartype=INTEGER) for key in variable_dim[0]}

                    model_object.addVariable(GeneratedVariable)

                else:

                    GeneratedVariable = {key: VariableGenerator(
                        name=f"{variable_name}{key}", lb=variable_bound[0], ub=variable_bound[1], vartype=INTEGER) for key in sets(*variable_dim)}

                    model_object.addVariable(GeneratedVariable)

        case 'fvar':

            '''

            Free Variable Generator


            '''

            if variable_dim == 0:

                GeneratedVariable = VariableGenerator(
                    lb=variable_bound[0], ub=variable_bound[1])

                model_object.addVariable(GeneratedVariable)

            else:

                if len(variable_dim) == 1:

                    GeneratedVariable = [VariableGenerator(
                        lb=variable_bound[0], ub=variable_bound[1]) for key in variable_dim[0]]

                    model_object.addVariable(GeneratedVariable)

                else:

                    GeneratedVariable = {key: VariableGenerator(
                        name=f"{variable_name}{key}", lb=variable_bound[0], ub=variable_bound[1]) for key in sets(*variable_dim)}

                    model_object.addVariable(GeneratedVariable)

    return GeneratedVariable
