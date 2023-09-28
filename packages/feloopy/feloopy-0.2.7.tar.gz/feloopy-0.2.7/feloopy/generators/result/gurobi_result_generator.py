'''
+---------------------------------------------------------+
|  Project: FelooPy (0.2.7)                               |
|  Modified: Wednesday, 27th September 2023 11:30:23 pm   |
|  Modified By: Keivan Tafakkori                          |
|  Project: https://github.com/ktafakkori/feloopy         |
|  Contact: https://www.linkedin.com/in/keivan-tafakkori/ |
|  Copyright 2022 - 2023 Keivan Tafakkori, FELOOP         |
+---------------------------------------------------------+
'''

import sys

import gurobipy as gurobi_interface

gurobi_status_dict = {
    gurobi_interface.GRB.LOADED: 'loaded',
    gurobi_interface.GRB.OPTIMAL: 'optimal',
    gurobi_interface.GRB.INFEASIBLE: 'infeasible',
    gurobi_interface.GRB.INF_OR_UNBD: 'infeasible or unbounded',
    gurobi_interface.GRB.UNBOUNDED: 'unbounded',
    gurobi_interface.GRB.CUTOFF: 'cutoff',
    gurobi_interface.GRB.ITERATION_LIMIT: 'iteration limit',
    gurobi_interface.GRB.NODE_LIMIT: 'node limit',
    gurobi_interface.GRB.TIME_LIMIT: 'time limit',
    gurobi_interface.GRB.SOLUTION_LIMIT: 'solution limit',
    gurobi_interface.GRB.INTERRUPTED: 'interrupted',
    gurobi_interface.GRB.NUMERIC: 'numerical',
    gurobi_interface.GRB.SUBOPTIMAL: 'suboptimal',
    gurobi_interface.GRB.INPROGRESS: 'inprogress'
}


def Get(model_object, result, input1, input2=None):
    input1 = input1[0]

    match input1:
        case 'variable':
            return input2.X

        case 'status':
            return gurobi_status_dict[model_object.status]

        case 'objective':
            return model_object.ObjVal

        case 'time':
            return (result[1][1] - result[1][0])

        case 'dual':
            return model_object.getConstrByName(input2).Pi

        case 'slack':
            return model_object.getConstrByName(input2).Slack

        case 'rc':
            return input2.rc
         
        case 'iis':
            model_object.computeIIS()
            for c in model_object.getConstrs():
                if c.IISConstr:
                    print("│" + " " + str(f"con: {c.constrName}").ljust(80-2) + " " + "│")
            for v in model_object.getVars():
                if v.IISLB > 0 or v.IISUB > 0:
                    print("│" + " " + str(f"var: {v.varName}").ljust(80-2) + " " + "│")
