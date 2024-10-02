import re
import numpy as np
from fractions import Fraction
'''
此代码用于平衡化学方程式，并输出平衡后的系数和方程式。
用户需要输入一个化学方程式，例如：Fe2(SO4)3+NH4OH=Fe(OH)3+(NH4)2SO4。
代码将解析方程式，并使用线性代数方法找到平衡系数。
最后，代码将输出平衡后的化学方程式。
'''
###1.1版本更新：增加了对化学式括号的支持，例如Fe2(SO4)3+NH4OH=Fe(OH)3+(NH4)2SO4。

def parse_compound(compound):
    ''' 解析化学式，返回元素及其数量的字典 '''
    counts = {}
    i = 0
    while i < len(compound):
        match = re.match(r'\(([^()]*)\)(\d*)', compound[i:])
        if match:
            group, number = match.groups()
            number = int(number) if number else 1
            sub_counts = parse_compound(group)
            for element, sub_number in sub_counts.items():
                counts[element] = counts.get(element, 0) + sub_number * number
            i += match.end()
        else:
            element_match = re.match(r'([A-Z][a-z]?)(\d*)', compound[i:])
            if element_match:
                element, number = element_match.groups()
                number = int(number) if number else 1
                counts[element] = counts.get(element, 0) + number
                i += element_match.end()
            else:
                i += 1
    return counts

def find_lcm(numbers):
    ''' 找到一组数的最大公约数 '''
    def lcm(a, b):
        return abs(a*b) // np.gcd(a, b)
    result = numbers[0]
    for number in numbers[1:]:
        result = lcm(result, number)
    return result


def insert_coefficients(reactants, products, coefficients):
    ''' 插入系数到化学方程式 '''
    new_reactants = [f"{coeff} {reactant}" if coeff != 1 else reactant for reactant, coeff in zip(reactants, coefficients)]
    new_products = [f"{coeff} {product}" if coeff != 1 else product for product, coeff in zip(products, coefficients[len(reactants):])]
    chemical_equation = ' + '.join(new_reactants) + ' = ' + ' + '.join(new_products)
    return chemical_equation


def balance_chemical_equation(equation):
    '''
    配平化学方程式
    '''
    # 解析化学方程式
    sides = equation.split('=')
    reactants = sides[0].strip().split('+')
    products = sides[1].strip().split('+') if len(sides) > 1 else []
    reactant_counts = [parse_compound(reactant) for reactant in reactants]
    product_counts = [parse_compound(product) for product in products]

    # 构建系数矩阵
    all_elements = set()
    for reactant in reactant_counts:
        all_elements.update(reactant.keys())
    for product in product_counts:
        all_elements.update(product.keys())

    A = []
    for element in all_elements:
        row = [reactant.get(element, 0) for reactant in reactant_counts] + [-product.get(element, 0) for product in product_counts]
        A.append(row)

    A = [row for row in A if any(x != 0 for x in row)]
    A = np.array(A)

    non_zero_counts = np.count_nonzero(A, axis=0)
    fixed_point = np.argmax(non_zero_counts)

    A_new = np.delete(A, fixed_point, axis=1)
    B_new = np.array([A[i, fixed_point] for i in range(len(A))])

    # 求解线性方程组(不定方程组)
    solution, residuals, rank, s = np.linalg.lstsq(A_new, B_new, rcond=None)
    solution = np.insert(solution, fixed_point, 1)
    solution = [abs(x) for x in solution]

    # 化简分数
    solutionplus = [Fraction(x).limit_denominator() for x in solution]
    lcm_value = find_lcm([frac.denominator for frac in solutionplus])
    integers = [frac * lcm_value for frac in solutionplus]
    integers_list = [int(Fraction) for Fraction in integers]

    # 插入系数到化学方程式
    coefficients = integers_list
    balanced_equation = insert_coefficients(reactants, products, coefficients)

    return coefficients, balanced_equation

# 输入化学方程式并输出结果
chemical_equation = input("请输入一个化学方程式：")
coefficients, balanced_equation = balance_chemical_equation(chemical_equation)
print(f"配平后的系数为：{coefficients}\n配平后方程式为：{balanced_equation}")
