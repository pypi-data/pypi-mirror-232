from typing import Tuple, List, Dict

from pulp import LpVariable, LpProblem, LpMaximize, lpSum, LpAffineExpression


class SolverUtils:

    @staticmethod
    def calculate_solved_problem(
            performance_table_list: List[List[float]],
            preferences: List[List[int]],
            indifferences: List[List[int]],
            weights: List[float],
            criteria: List[int],
            alternative_id_1: int = -1,
            alternative_id_2: int = -1
    ) -> LpProblem:
        """
        Main calculation method for problem-solving.
        The idea is that this should be a generic method used across different problems

        :param performance_table_list:
        :param preferences:
        :param indifferences:
        :param weights:
        :param criteria:
        :param alternative_id_1:
        :param alternative_id_2:

        :return:
        """
        problem: LpProblem = LpProblem("UTA-GMS", LpMaximize)

        epsilon: LpVariable = LpVariable("epsilon")

        u_list, u_list_dict = SolverUtils.create_variables_list_and_dict(performance_table_list)

        # Normalization constraints
        the_greatest_performance: List[LpVariable] = []
        for i in range(len(u_list)):
            if criteria[i] == 1:
                the_greatest_performance.append(u_list[i][-1])
                problem += u_list[i][-1] == weights[i]
                problem += u_list[i][0] == 0
            else:
                the_greatest_performance.append(u_list[i][0])
                problem += u_list[i][0] == weights[i]
                problem += u_list[i][-1] == 0

        problem += lpSum(the_greatest_performance) == 1

        # Monotonicity constraint
        for i in range(len(u_list)):
            for j in range(1, len(u_list[i])):
                if criteria[i] == 1:
                    problem += u_list[i][j] >= u_list[i][j - 1]
                else:
                    problem += u_list[i][j - 1] >= u_list[i][j]

        # Bounds constraint
        for i in range(len(u_list)):
            for j in range(1, len(u_list[i]) - 1):
                if criteria[i] == 1:
                    problem += u_list[i][-1] >= u_list[i][j]
                    problem += u_list[i][j] >= u_list[i][0]
                else:
                    problem += u_list[i][0] >= u_list[i][j]
                    problem += u_list[i][j] >= u_list[i][-1]

        # Preference constraint
        for preference in preferences:
            left_alternative: List[float] = performance_table_list[preference[0]]
            right_alternative: List[float] = performance_table_list[preference[1]]

            left_side: List[LpVariable] = []
            right_side: List[LpVariable] = []
            for i in range(len(u_list_dict)):
                left_side.append(u_list_dict[i][left_alternative[i]])
                right_side.append(u_list_dict[i][right_alternative[i]])

            weighted_left_side: List[LpAffineExpression] = []
            weighted_right_side: List[LpAffineExpression] = []
            for u in left_side:
                weighted_left_side.append(u)

            for u in right_side:
                weighted_right_side.append(u)

            problem += lpSum(weighted_left_side) >= lpSum(weighted_right_side) + epsilon

        # Indifference constraint
        for indifference in indifferences:
            left_alternative: List[float] = performance_table_list[indifference[0]]
            right_alternative: List[float] = performance_table_list[indifference[1]]

            left_side: List[LpVariable] = []
            right_side: List[LpVariable] = []
            for i in range(len(u_list_dict)):
                left_side.append(u_list_dict[i][left_alternative[i]])
                right_side.append(u_list_dict[i][right_alternative[i]])

            weighted_left_side: List[LpAffineExpression] = []
            weighted_right_side: List[LpAffineExpression] = []
            for u in left_side:
                weighted_left_side.append(u)

            for u in right_side:
                weighted_right_side.append(u)

            problem += lpSum(weighted_left_side) == lpSum(weighted_right_side)

        if alternative_id_1 >= 0 and alternative_id_2 >= 0:
            left_alternative: List[float] = performance_table_list[alternative_id_2]
            right_alternative: List[float] = performance_table_list[alternative_id_1]

            left_side: List[LpVariable] = []
            right_side: List[LpVariable] = []
            for i in range(len(u_list_dict)):
                left_side.append(u_list_dict[i][left_alternative[i]])
                right_side.append(u_list_dict[i][right_alternative[i]])

            weighted_left_side: List[LpAffineExpression] = []
            weighted_right_side: List[LpAffineExpression] = []
            for u in left_side:
                weighted_left_side.append(u)

            for u in right_side:
                weighted_right_side.append(u)

            problem += lpSum(weighted_left_side) >= lpSum(weighted_right_side) + epsilon

        problem += epsilon

        problem.solve()

        return problem

    @staticmethod
    def create_variables_list_and_dict(performance_table: List[list]) -> Tuple[List[list], List[dict]]:
        """
        Method responsible for creating a technical list of variables and a technical dict of variables that are used
        for adding constraints to the problem.

        :param performance_table:

        :return: ex. Tuple([[u_0_0.0, u_0_2.0], [u_1_2.0, u_1_9.0]], [{26.0: u_0_26.0, 2.0: u_0_2.0}, {40.0: u_1_40.0, 2.0: u_1_2.0}])
        """
        u_list: List[List[LpVariable]] = []
        u_list_dict: List[Dict[float, LpVariable]] = []

        for i in range(len(performance_table[0])):
            row: List[LpVariable] = []
            row_dict: Dict[float, LpVariable] = {}

            for j in range(len(performance_table)):
                variable_name: str = f"u_{i}_{performance_table[j][i]}"
                variable: LpVariable = LpVariable(variable_name)

                if performance_table[j][i] not in row_dict:
                    row_dict[performance_table[j][i]] = variable

                flag: int = 1
                for var in row:
                    if str(var) == variable_name:
                        flag: int = 0
                if flag:
                    row.append(variable)

            u_list_dict.append(row_dict)

            row: List[LpVariable] = sorted(row, key=lambda var: float(var.name.split("_")[-1]))
            u_list.append(row)

        return u_list, u_list_dict

    @staticmethod
    def calculate_direct_relations(necessary: List[List[str]]) -> Dict[str, set]:
        """
        Method for getting only direct relations in Hasse Diagram

        :param necessary:

        :return:
        """
        direct_relations: Dict[str, set] = {}

        for relation in necessary:
            node1, node2 = relation
            direct_relations.setdefault(node1, set()).add(node2)

        for node1, related_nodes in direct_relations.items():
            related_nodes_copy: Dict[str] = related_nodes.copy()
            for node2 in related_nodes:
                # Check if node2 is also related to any other node that is related to node1
                for other_node in related_nodes:
                    if other_node != node2 and other_node in direct_relations and node2 in direct_relations[other_node]:
                        # If such a relationship exists, remove the relation between node1 and node2
                        related_nodes_copy.remove(node2)
                        break
            direct_relations[node1]: Dict[str] = related_nodes_copy

        return direct_relations

    @staticmethod
    def get_alternatives_and_utilities_dict(
            variables_and_values_dict,
            performance_table_list,
            alternatives_id_list,
            weights
    ) -> Dict[str, float]:

        utilities: List[float] = []
        for i in range(len(performance_table_list)):
            utility: float = 0.0
            for j in range(len(weights)):
                variable_name: str = f"u_{j}_{performance_table_list[i][j]}"
                utility += round(variables_and_values_dict[variable_name], 4)

            utilities.append(utility)

        utilities_dict: Dict[str, float] = {}
        # TODO: Sorting possibly unnecessary, but for now it's nicer for human eye :)
        for i in range(len(utilities)):
            utilities_dict[alternatives_id_list[i]] = utilities[i]
        sorted_dict: Dict[str, float] = dict(sorted(utilities_dict.items(), key=lambda item: item[1]))

        return sorted_dict
