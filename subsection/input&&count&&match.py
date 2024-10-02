import re

# 定义元素符号的正则表达式
element_pattern = re.compile(r'([A-Z][a-z]?)(\d*)')

# 用户输入一个化学方程式
chemical_equation = input("请输入一个化学方程式：")

# 分割方程式为反应物和生成物
sides = chemical_equation.split('=')
reactants = sides[0].strip().split('+')
products = sides[1].strip().split('+') if len(sides) > 1 else []

# 函数用于解析一个化学式并返回元素计数
def parse_compound(compound):
    counts = {}
    for element, number in element_pattern.findall(compound):
        number = int(number) if number else 1
        counts[element] = counts.get(element, 0) + number
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

# 构建矩阵
matrix = []
for element in all_elements:
    row = []
    reactant_values = [reactant.get(element, 0) for reactant in reactant_counts]
    product_values = [-product.get(element, 0) for product in product_counts]
    row.extend(reactant_values + product_values)
    matrix.append(row)

# 移除全为0的行
matrix = [row for row in matrix if any(x != 0 for x in row)]

# 输出矩阵
for row in matrix:
    print(row)