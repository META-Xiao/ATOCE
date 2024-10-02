import re
import numpy as np
from fractions import Fraction

'''
此代码用于平衡化学方程式，并输出平衡后的系数和方程式。
用户需要输入一个化学方程式，例如：Fe2(SO4)3+NH4OH=Fe(OH)3+(NH4)2SO4。
代码将解析方程式，并使用线性代数方法找到平衡系数。
最后，代码将输出平衡后的化学方程式。
当然这个程序也会检查输入的化学方程式是否合规。
'''
###1.2版本更新：支持检查化学式是否合规。
def parse_compound(compound):
    ''' 解析化学式，返回元素及其数量的字典 '''
    counts = {}
    i = 0
    while i < len(compound): #遍历化学式
        match = re.match(r'\(([^()]*)\)(\d*)', compound[i:]) # 匹配括号内的化学式
        if match:
            group, number = match.groups()
            number = int(number) if number else 1
            sub_counts = parse_compound(group)
            for element, sub_number in sub_counts.items():
                counts[element] = counts.get(element, 0) + sub_number * number #    将括号内的元素数量乘以括号外的系数
            i += match.end()
        else:
            element_match = re.match(r'([A-Z][a-z]?)(\d*)', compound[i:]) # 匹配元素及其数量
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
    new_reactants = [f"{coeff} {reactant}" if coeff != 1 else reactant for reactant, coeff in zip(reactants, coefficients)] # 将系数插入到反应物中
    new_products = [f"{coeff} {product}" if coeff != 1 else product for product, coeff in zip(products, coefficients[len(reactants):])] #   将系数插入到生成物中
    chemical_equation = ' + '.join(new_reactants) + ' = ' + ' + '.join(new_products) 
    return chemical_equation

def validate_element(element):
    """验证元素符号是否合规"""
    return re.match(r'^[A-Z][a-z]?$|^D$|^T$', element)

def validate_compound(compound):
    """验证化学式是否合规"""
    stripped_compound = re.sub(r'\([^\(\)]*\)', '', compound)
    if not all(validate_element(e) for e in re.findall(r'[A-Z][a-z]?', stripped_compound)):
        return False

    # 检查化学式是否包含括号
    while '(' in compound:
        # 找到最内层的括号
        inner_parentheses = re.search(r'\([^\(\)]*\)', compound)
        if not inner_parentheses:
            return False
        # 验证括号内的化学式
        inner_compound = inner_parentheses.group(0)[1:-1]  # 移除括号
        if not validate_compound(inner_compound):
            return False
        # 替换括号及其内容为单个字符，以简化后续的验证
        compound = compound[:inner_parentheses.start()] + 'X' + compound[inner_parentheses.end():]

    # 检查剩余的化学式是否只包含合法的元素和数字
    return all(re.match(r'([A-Z][a-z]?)(\d*)', part) for part in re.findall(r'[A-Z][a-z]?\d*', compound))

def validate_equation(equation):
    if '=' not in equation or '+' not in equation:
        return False, "输入的不是一个有效的化学方程式，请确保包含 '=' 和 '+'。"
    
    sides = equation.split('=')
    if len(sides) != 2:
        return False, "方程式两边不平衡，请确保有一个 '=' 符号。"
    
    reactants = sides[0].strip().split('+')
    products = sides[1].strip().split('+')

    for reactant in reactants:
        if not validate_compound(reactant):
            return False, f"反应物 '{reactant}' 是无效的化学式。"
    
    for product in products:
        if not validate_compound(product):
            return False, f"生成物 '{product}' 是无效的化学式。"
    
    reactant_elements = set()
    product_elements = set()
    for reactant in reactants:
        reactant_elements.update(parse_compound(reactant).keys())
    for product in products:
        product_elements.update(parse_compound(product).keys())

    if reactant_elements != product_elements:
        return False, "方程式左右两边元素不守恒，请检查元素是否在两边都有出现。"

    if not all(re.match(r'^[A-Za-z0-9\(\)\+\=]*$', part) for part in equation.split()):
        return False, "输入包含非法字符，请只使用英文大小写字母、数字、括号、加号和等号。"
    
    return True, ""

def balance_chemical_equation(equation):
    ''' 配平化学方程式 '''
    sides = equation.split('=')
    reactants = sides[0].strip().split('+')
    products = sides[1].strip().split('+') if len(sides) > 1 else []
    # 将化学式转换为字典，统计每个元素的数量
    reactant_counts = [parse_compound(reactant) for reactant in reactants]
    product_counts = [parse_compound(product) for product in products]
    # 获取所有元素
    all_elements = set()
    for reactant in reactant_counts:
        all_elements.update(reactant.keys())
    for product in product_counts:
        all_elements.update(product.keys())
    # 构建增广矩阵
    A = []
    for element in all_elements:
        row = [reactant.get(element, 0) for reactant in reactant_counts] + [-product.get(element, 0) for product in product_counts]
        A.append(row)

    # 移除全为0的行
    A = [row for row in A if any(x != 0 for x in row)]
    A = np.array(A)

    # 找出非零整数出现次数最多的列
    non_zero_counts = np.count_nonzero(A, axis=0)
    fixed_point = np.argmax(non_zero_counts)

    # 移除这一列并把这一列的相反数放入B，得到新的矩阵A_new和B_new
    A_new = np.delete(A, fixed_point, axis=1)
    B_new = np.array([A[i, fixed_point] for i in range(len(A))])

    # 使用lstsq函数计算最小二乘解
    solution, residuals, rank, s = np.linalg.lstsq(A_new, B_new, rcond=None)
    solution = np.insert(solution, fixed_point, 1)
    solution = [abs(x) for x in solution]

    # 将解转换为分数形式，后通分取互质整数
    solutionplus = [Fraction(x).limit_denominator() for x in solution]
    lcm_value = find_lcm([frac.denominator for frac in solutionplus])
    integers = [frac * lcm_value for frac in solutionplus]
    integers_list = [int(Fraction) for Fraction in integers]

    coefficients = integers_list
    balanced_equation = insert_coefficients(reactants, products, coefficients)

    return coefficients, balanced_equation

def main():
    while True:
        chemical_equation = input("请输入一个化学方程式：")
        is_valid, error_message = validate_equation(chemical_equation)
        if not is_valid:
            print(f"输入错误：{error_message}\n请重新输入。")
            continue

        coefficients, balanced_equation = balance_chemical_equation(chemical_equation)
        print(f"配平后的系数为：{coefficients}\n配平后方程式为：{balanced_equation}")
        break

if __name__ == "__main__":
    main()