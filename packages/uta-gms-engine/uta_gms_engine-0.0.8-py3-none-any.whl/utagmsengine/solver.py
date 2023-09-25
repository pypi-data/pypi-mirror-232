from typing import List, Dict

from pulp import LpProblem

from .utils.solver_utils import SolverUtils


class Solver:

    def __init__(self):
        self.name = 'UTA GMS Solver'

    def __str__(self):
        return self.name

    def get_hasse_diagram_dict(
            self,
            performance_table_list: List[List[float]],
            alternatives_id_list: List[str],
            preferences: List[List[int]],
            indifferences: List[List[int]],
            weights: List[float],
            criteria: List[int]
    ) -> Dict[str, set]:
        """
        Method for getting hasse diagram dict

        :param performance_table_list:
        :param alternatives_id_list:
        :param preferences:
        :param indifferences:
        :param weights:
        :param criteria:

        :return refined_necessary:
        """
        necessary: List[List[str]] = []
        for i in range(len(performance_table_list)):
            for j in range(len(performance_table_list)):
                if i == j:
                    continue

                problem: LpProblem = SolverUtils.calculate_solved_problem(
                    performance_table_list=performance_table_list,
                    preferences=preferences,
                    indifferences=indifferences,
                    weights=weights,
                    criteria=criteria,
                    alternative_id_1=i,
                    alternative_id_2=j
                )

                if problem.variables()[0].varValue <= 0:
                    necessary.append([alternatives_id_list[i], alternatives_id_list[j]])

        direct_relations: Dict[str, set] = SolverUtils.calculate_direct_relations(necessary)
        return direct_relations

    def get_ranking_dict(
            self,
            performance_table_list: List[List[float]],
            alternatives_id_list: List[str],
            preferences: List[List[int]],
            indifferences: List[List[int]],
            weights: List[float],
            criteria: List[int]
    ) -> Dict[str, float]:
        """
        Method for getting ranking dict

        :param performance_table_list:
        :param alternatives_id_list:
        :param preferences:
        :param indifferences:
        :param weights:
        :param criteria:

        :return refined_necessary:
        """

        problem: LpProblem = SolverUtils.calculate_solved_problem(
            performance_table_list=performance_table_list,
            preferences=preferences,
            indifferences=indifferences,
            weights=weights,
            criteria=criteria
        )

        variables_and_values_dict: Dict[str, float] = {variable.name: variable.varValue for variable in problem.variables()}

        alternatives_and_utilities_dict: Dict[str, float] = SolverUtils.get_alternatives_and_utilities_dict(
            variables_and_values_dict=variables_and_values_dict,
            performance_table_list=performance_table_list,
            alternatives_id_list=alternatives_id_list,
            weights=weights
        )

        return alternatives_and_utilities_dict
