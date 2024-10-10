import re
import numpy as np
from fractions import Fraction

def parse_compound(compound):
    ''' 解析化学式，返回元素及其数量的字典 '''
    counts = {'e': 0}   
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
            element_match = re.match(r'([A-Z][a-z]?)(\{\d+[+-]?\})?(\d*)', compound[i:])
            if element_match:
                element, charge, number_str = element_match.groups()
                number = int(number_str) if number_str else 1 
                if charge:  # 如果有电荷符号
                    ion_charge = int(charge[1:-2]) 
                    if charge[-2] == '-':  # 如果电荷是负的
                        counts['e'] += ion_charge * number  # 更新电子数
                    else:
                        counts['e'] -= ion_charge * number 
                counts[element] = counts.get(element, 0) + number 
                i += element_match.end()
            else:
                i += 1
    return counts


def find_lcm(numbers):
    '''计算一组数字的最小公倍数 '''
    def lcm(a, b):
        return abs(a*b) // np.gcd(a, b)
    result = numbers[0]
    for number in numbers[1:]:
        result = lcm(result, number)
    return result

def insert_coefficients(reactants, products, coefficients):
    ''' 将系数插入到化学方程式中 '''
    new_reactants = [f"{coeff} {reactant}" if coeff != 1 else reactant for reactant, coeff in zip(reactants, coefficients)]
    new_products = [f"{coeff} {product}" if coeff != 1 else product for product, coeff in zip(products, coefficients[len(reactants):])]
    chemical_equation = ' + '.join(new_reactants) + ' = ' + ' + '.join(new_products)
    return chemical_equation

def check_equation_format(equation):
    ''' 检查化学方程式是否含有+或= '''
    if '=' not in equation:
        return False, "╰（‵□′）╯方程式没有等号（=），请检查输入。"
    if '+' not in equation:
        return False, "╰（‵□′）╯方程式没有加号（+），请检查输入。"
    return True, ""

def check_and_reduce_matrix(A):
    ''' 检查矩阵是否可以化简 '''
    if len(A.shape) == 2:
        while A.shape[0] > A.shape[1] - 1:
            # 计算每行0的个数
            zero_counts = np.sum(A == 0, axis=1)
            # 找到0最多的行索引
            row_to_remove = np.argmax(zero_counts)
            # 删除这一行
            A = np.delete(A, row_to_remove, axis=0)
    else: pass
    return A

def analyze_chemical_equation(equation):
    ''' 解析化学方程式 '''
    # 检查方程式格式
    is_valid, error_message = check_equation_format(equation)
    if not is_valid:
        return None, error_message

    # 解析化学方程式
    sides = re.split(r'(?<!\{)\=(?!\})', equation)
    reactants = re.split(r'(?<!\{)\+(?!\})', sides[0].strip())
    products = re.split(r'(?<!\{)\+(?!\})', sides[1].strip())
    reactant_counts = [parse_compound(reactant) for reactant in reactants]
    product_counts = [parse_compound(product) for product in products]

    all_elements = set()
    for reactant in reactant_counts:
        all_elements.update(reactant.keys())
    for product in product_counts:
        all_elements.update(product.keys())

    return reactants, products, reactant_counts, product_counts, all_elements


def balance_chemical_equation(equation):
    ''' 配平化学方程式，返回配平后的化学方程式  '''
    reactants, products, reactant_counts, product_counts, all_elements = analyze_chemical_equation(equation)
    if reactants is None:
        return None, products  

    # 检查元素是否在两边都有出现
    #如果counts['e'] != 0:则执行以下代码
    reactant_elements = set()
    product_elements = set()
    for reactant in reactant_counts:
        reactant_elements.update(reactant.keys())
    for product in product_counts:
        product_elements.update(product.keys())

    for counts in [reactant_counts, product_counts]:
        for count in counts:
            if count.get('e') != 0:
                pass
            else:
                    if reactant_elements != product_elements:
                        return None, "(´。＿。｀)方程式左右两边元素不守恒，请检查元素是否在两边都有出现。"

    # 构建系数矩阵
    A = []
    for element in all_elements:
        row = [reactant.get(element, 0) for reactant in reactant_counts] + [-product.get(element, 0) for product in product_counts]
        A.append(row)

    A = [row for row in A if any(x != 0 for x in row)]
    A = np.array(A)
        # 检查A矩阵是否可逆
    A = check_and_reduce_matrix(A)
    try:
        fixed_point = np.argmax(np.count_nonzero(A, axis=0))
        A_new = np.delete(A, fixed_point, axis=1)
        B_new = np.array([-A[i, fixed_point] for i in range(len(A))])
        solution, residuals, rank, s = np.linalg.lstsq(A_new, B_new, rcond=None)
        solution = np.insert(solution, fixed_point, 1)
        solution = [abs(x) for x in solution]
        solutionplus = [Fraction(x).limit_denominator() for x in solution]
        lcm_value = find_lcm([frac.denominator for frac in solutionplus])
        integers = [frac * lcm_value for frac in solutionplus]
        coefficients = [int(Fraction) for Fraction in integers]
        balanced_equation = insert_coefficients(reactants, products, coefficients)
        return coefficients, balanced_equation
    except Exception as e:
        return None, '无法配平方程式。可能是因为提供的方程式格式不正确或者方程式本身无法配平。'


def main():
    balanced_equations = []
    print("欢迎使用化学方程式配平工具(｡･∀･)ﾉﾞ例如输入：H2O+H2SO4+[Cu(NH3)4]SO4=(NH4)2SO4+[Cu(H2O)4]SO4。")
    print("如果是要输入离子方程式，离子用{}括起来，例如：Fe+H{1+}=H2+Fe{2+} ")

    while True:  # 检查输入是否为整数
        num_equations = input("你想配平多少个化学方程式？请输入个数：")
        try:
            num_equations = int(num_equations)
            break
        except ValueError:
            print("请输入一个有效的整数。")

    for i in range(num_equations):
        while True:
            chemical_equation = input("请输入：")
            valid, error_message = check_equation_format(chemical_equation)
            if not valid:
                print(f"错误：{error_message}\n请重新输入ヾ(≧へ≦)〃 ：")
                continue
            coefficients, balanced_equation_or_error = balance_chemical_equation(chemical_equation)
            if coefficients is None:
                print(f"错误：{balanced_equation_or_error}\n请重新输入♪(´▽｀) ：")
                continue
            balanced_equations.append(balanced_equation_or_error)
            break

    print("\n所有配平的化学方程式如下＜（＾－＾）＞ ：")
    for eq in balanced_equations:
        print(eq)
    
    input("\n按回车键退出程序( ﾟдﾟ)つBye")

if __name__ == "__main__":
    main()