import random
import numpy as np


def T1_movement_seq_gen(input_list: list, N: int):
    """Generates a sequence of instructions for body movement, repeated N times and shuffled.
    Args:
        input_list (list): A list containing the indices of the instructions
        N (int): The number of times the list is repeated (before shuffling).
    Output:
        The sequence of instructions.
    """

    result = []

    # Repeat each element in the input list N times
    for item in input_list:
        result.extend([item] * N)

    # Shuffle the resulting list
    random.shuffle(result)

    return result





def T2_generate_colors(colors, num_tests=10, congruent_rate=0.0):
    """Function to generate +10 different lists"""

    if num_tests < 10:
        raise ValueError(
            "Number of generated pairs of colors must be 10 or greater to ensure all colors are covered at least once.")

    else:

        # Generate a random number between 0 and 1
        lists = []
        for _ in range(num_tests):
            color_pairs = create_color_pairs(colors[:], congruent_rate=congruent_rate)  # Create a copy of colors list
            lists.extend(color_pairs)

        lists = lists[:num_tests]

    return lists

def create_color_pairs(colors, congruent_rate):
    # Shuffle the list to ensure random pairs
    random.shuffle(colors)

    # Create pairs
    pairs = []

    for i in range(0, len(colors), 2):

        if i + 1 < len(colors):

            # [first color, first color-code],
            # [second color, second color-code],
            # Congruent (False), Non-Congruent (True)
            # Side allocation / correct side: original to the left (0), original to the right (1)
            rn_1 = random.random()
            rn_2 = random.random()

            if rn_1 < congruent_rate:
                congruency = True
            else:
                congruency = False

            if rn_2 < 0.5:
                correct_side = 0
            else:
                correct_side = 1

            pairs.append([colors[i], colors[i + 1], congruency, correct_side])

        else:
            pairs.append([colors[i], ["", ""]])  # Handle odd number of colors

    return pairs

def T3_generate_maths_test(D: int, N, operator, M=1, digit_order='shuffle'):

    """Generates D x N x M mathematical operations with random numbers.
    Args:
        - D (int): Number of test types/digits. A test with D digits covers math operations like 1 + 1, 11 + 11, 1...(N) + 1...(N).
        - N: Number of repetitions per type/digits. If N is integer, then all types/digits are all repeated N times. If N is list, then each type/digit is repeated N[d] times.
        - M (int): Number of times the test is repeated overall.

    """
    result = []

    for _ in range(M):
        for d in range(D):

            if isinstance(N, int):
                N_as_int = N
            elif isinstance(N, list):
                N_as_int = N[d]

            for n in range(N_as_int):

                rn_1 = random.randint(10 ** d, (10 ** (d + 1)) - 1)
                rn_2 = random.randint(10 ** d, (10 ** (d + 1)) - 1)

                operation_result = np.round(operator((rn_1, rn_2)))
                result.append([operation_result, rn_1, rn_2])



        if digit_order == 'shuffle':
            random.shuffle(result)

        elif digit_order == 'incremental':
            pass

        else:
            raise ValueError('Invalid digit order')

    return result

def T1_movement_seq_gen(input_list: list, N: int):
    """Generates a sequence of instructions for body movement, repeated N times and shuffled.
    Args:
        input_list (list): A list containing the indices of the instructions
        N (int): The number of times the list is repeated (before shuffling).
    Output:
        The sequence of instructions.
    """

    result = []

    # Repeat each element in the input list N times
    for item in input_list:
        result.extend([item] * N)

    # Shuffle the resulting list
    random.shuffle(result)

    return result





def T2_generate_colors(colors, num_tests=10, congruent_rate=0.0):
    """Function to generate +10 different lists"""

    if num_tests < 10:
        raise ValueError(
            "Number of generated pairs of colors must be 10 or greater to ensure all colors are covered at least once.")

    else:

        # Generate a random number between 0 and 1
        lists = []
        for _ in range(num_tests):
            color_pairs = create_color_pairs(colors[:], congruent_rate=congruent_rate)  # Create a copy of colors list
            lists.extend(color_pairs)

        lists = lists[:num_tests]

    return lists

def create_color_pairs(colors, congruent_rate):
    # Shuffle the list to ensure random pairs
    random.shuffle(colors)

    # Create pairs
    pairs = []

    for i in range(0, len(colors), 2):

        if i + 1 < len(colors):

            # [first color, first color-code],
            # [second color, second color-code],
            # Congruent (False), Non-Congruent (True)
            # Side allocation / correct side: original to the left (0), original to the right (1)
            rn_1 = random.random()
            rn_2 = random.random()

            if rn_1 < congruent_rate:
                congruency = True
            else:
                congruency = False

            if rn_2 < 0.5:
                correct_side = 0
            else:
                correct_side = 1

            pairs.append([colors[i], colors[i + 1], congruency, correct_side])

        else:
            pairs.append([colors[i], ["", ""]])  # Handle odd number of colors

    return pairs

def T3_generate_maths_test(D: int, N, operator, M=1, digit_order='shuffle'):

    """Generates D x N x M mathematical operations with random numbers.
    Args:
        - D (int): Number of test types/digits. A test with D digits covers math operations like 1 + 1, 11 + 11, 1...(N) + 1...(N).
        - N: Number of repetitions per type/digits. If N is integer, then all types/digits are all repeated N times. If N is list, then each type/digit is repeated N[d] times.
        - M (int): Number of times the test is repeated overall.

    """
    result = []

    for _ in range(M):
        for d in range(D):

            if isinstance(N, int):
                N_as_int = N
            elif isinstance(N, list):
                N_as_int = N[d]

            for n in range(N_as_int):

                rn_1 = random.randint(10 ** d, (10 ** (d + 1)) - 1)
                rn_2 = random.randint(10 ** d, (10 ** (d + 1)) - 1)

                operation_result = np.round(operator((rn_1, rn_2)))
                result.append([operation_result, rn_1, rn_2])



        if digit_order == 'shuffle':
            random.shuffle(result)

        elif digit_order == 'incremental':
            pass

        else:
            raise ValueError('Invalid digit order')

    return result



    # return new_value.isdigit() or new_value == ""
# result = T3_generate_maths_test(3, 3, np.sum, digit_order='incremental')
# print(result)
#
# result = T3_generate_maths_test(3, [6, 4, 2], np.sum, M=2, digit_order='incremental')
# print(result)
