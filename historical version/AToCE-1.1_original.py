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

element_pattern = re.compile(r'([A-Z][a-z]?)(\d*)')
group_pattern = re.compile(r'\(([^()]*)\)(\d*)')
chemical_equation = input("请输入一个化学方程式：")

# 分割方程式为反应物和生成物
sides = chemical_equation.split('=')
reactants = sides[0].strip().split('+')
products = sides[1].strip().split('+') if len(sides) > 1 else []

# 函数用于解析一个化学式并返回元素计数
def parse_compound(compound):
    '''
    写了2h的函数，一定要让以后的我看懂
    解析一个化学式并返回元素计数
    '''
    counts = {}
    i = 0
    while i < len(compound):  # 循环遍历化合物字符串的每个字符
        match = group_pattern.match(compound, i)  # 尝试匹配括号内的化学式
        if match:
            group, number = match.group(1, 2)  # 提取括号内的化学式和后面的数字
            number = int(number) if number else 1  # 如果有数字则转换为整数，否则为1
            sub_counts = parse_compound(group)  # 递归调用parse_compound来解析括号内的化学式
            for element, sub_number in sub_counts.items():  # 更新元素计数
                counts[element] = counts.get(element, 0) + sub_number * number  # 乘以括号外的数字
            i = match.end()  # 更新索引到匹配的结束位置
        else:
            element_match = element_pattern.match(compound, i)  # 尝试匹配元素和数字
            if element_match:
                element, number = element_match.groups()  # 提取元素和数字
                number = int(number) if number else 1  # 如果有数字则转换为整数，否则为1
                counts[element] = counts.get(element, 0) + number  # 更新元素计数
                i = element_match.end()  # 更新索引到匹配的结束位置
            else:
                i += 1  # 如果当前位置既不是括号也不是元素，则移动到下一个字符
    return counts  


# 解析反应物和生成物
reactant_counts = [parse_compound(reactant) for reactant in reactants]
product_counts = [parse_compound(product) for product in products]

# 找出所有元素
all_elements = set()
for reactant in reactant_counts:
    all_elements.update(reactant.keys())
for product in product_counts:
    all_elements.update(product.keys())

# 按照线性方程的形式构建矩阵A
A = []
for element in all_elements:
    row = []
    reactant_values = [reactant.get(element, 0) for reactant in reactant_counts]
    product_values = [-product.get(element, 0) for product in product_counts]
    row.extend(reactant_values + product_values)
    A.append(row)

# 移除全为0的行
A = [row for row in A if any(x != 0 for x in row)]
A = np.array(A)

# 找出非零整数出现次数最多的列
non_zero_counts = np.count_nonzero(A, axis=0)
fixed_point = np.argmax(non_zero_counts)

# 移除这一列，得到新的矩阵A
A_new = np.delete(A, fixed_point, axis=1)

# 创建新的矩阵B，包含A中对应列的相反数
B_new = np.array([A[i, fixed_point] for i in range(len(A))])


# 将A_new,B_new转换为NumPy数组
A = np.array(A_new)
B = np.array(B_new)

# 使用lstsq函数计算最小二乘解
solution, residuals, rank, s = np.linalg.lstsq(A_new, B_new, rcond=None)

#返回不动点
solution=np.insert(solution,fixed_point,1)

#取个项的绝对值
solution=[abs(x) for x in solution]

# 将解向量转换为分数形式
solutionplus = [Fraction(x).limit_denominator() for x in solution]

# 找到分母的最小公倍数（LCM）
def lcm(a, b):
    return abs(a*b) // gcd(a, b)

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def find_lcm(numbers):
    result = numbers[0]
    for number in numbers[1:]:
        result = lcm(result, number)
    return result

# 计算LCM
lcm_value = find_lcm([frac.denominator for frac in solutionplus])

# 将每个分数乘以LCM以得到整数
integers=[frac * lcm_value for frac in solutionplus]

# 将分数转换为整数
integers_list=[int(Fraction) for Fraction in integers]

def insert_coefficients(reactants, products, coefficients):
    # 插入系数到反应物
    new_reactants = []
    for reactant, coeff in zip(reactants, coefficients):
        if coeff != 1:
            new_reactants.append(f"{coeff} {reactant}")
        else:
            new_reactants.append(reactant)
    # 插入系数到生成物
    new_products = []
    for product, coeff in zip(products, coefficients[len(reactants):]):
        if coeff != 1:
            new_products.append(f"{coeff} {product}")
        else:
            new_products.append(product)
    
    # 重新组合方程式
    chemical_equation = ' + '.join(new_reactants) + ' = ' + ' + '.join(new_products)
    return chemical_equation

coefficients = integers_list
balanced_equation = insert_coefficients(reactants, products, coefficients)

#输出
print(f"配平后的系数为：{integers_list}\n配平后方程式为：{balanced_equation}")