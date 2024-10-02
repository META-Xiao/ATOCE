def balance_chemical_equation(vector, equation):
    # 分割方程式为反应物和生成物
    parts = equation.split('=')
    reactants = parts[0].strip()
    products = parts[1].strip()

    # 应用向量中的数字
    balanced_reactants = f"{vector[0]}{reactants}"
    balanced_products = products.split('+')
    balanced_products = '+'.join([f"{vector[i+1]}{prod}" for i, prod in enumerate(balanced_products)])

    # 组合配平后的方程式
    balanced_equation = f"{balanced_reactants} = {balanced_products}"

    return balanced_equation

# 向量和原始方程式
vector = [2, 1, 2]
equation = "H2O = H2 + O2"

# 调用函数并打印结果
balanced_equation = balance_chemical_equation(vector, equation)
print(balanced_equation)