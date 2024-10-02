from sympy import symbols, Eq, solve, gcd

def get_coefficients(num_equations, num_variables):
    coefficients = []
    for i in range(num_equations):
        eq_input = input(f"请输入方程 {i+1} 的系数（用空格分隔，最后输入常数项）: ")
        eq_coeffs = list(map(int, eq_input.split()))
        coefficients.append(eq_coeffs)
    return coefficients

def find_integer_solution(coefficients, num_variables):
    # 定义变量
    variables = symbols(f'x:{num_variables}')
    
    # 如果只有一个方程，则特殊处理
    if len(coefficients) == 1:
        eq_coeffs = coefficients[0]
        for x0_val in range(-10, 11):
            # 计算第二个变量的值
            x1_val = (eq_coeffs[-1] - eq_coeffs[0] * x0_val) / eq_coeffs[1]
            if x1_val.is_integer():
                return [x0_val, x1_val]
        return None
    
    # 遍历第一个变量的值
    for x0_val in range(-10, 11):
        # 构建方程组，固定第一个变量的值
        equations = [Eq(sum(coeff * var for coeff, var in zip(eq_coeffs, variables)), 0) for eq_coeffs in coefficients]
        equations[0] = Eq(equations[0].lhs.subs(variables[0], x0_val), equations[0].rhs)
        
        # 尝试解出剩余变量的值
        solution = solve(equations[1:], variables[1:])
        
        # 如果找到解，则返回
        if solution:
            full_solution = [x0_val] + [sol.evalf() for sol in solution]
            # 检查解是否都是整数
            if all(isinstance(s, (int, float)) and s.is_integer for s in full_solution):
                return [int(sol) for sol in full_solution]
    
    return None

def make_solution_coprime(solution):
    # 确保每个解分量都是互质的
    coprime_solution = []
    for i in range(len(solution)):
        for j in range(i+1, len(solution)):
            common_gcd = abs(gcd(solution[i], solution[j]))
            while common_gcd != 1:
                solution[i] //= common_gcd
                solution[j] //= common_gcd
                common_gcd = abs(gcd(solution[i], solution[j]))
        coprime_solution.append(solution[i])
    return coprime_solution

def main():
    num_equations = int(input("请输入方程的数量: "))
    num_variables = int(input("请输入变量的数量: "))
    
    if num_variables < num_equations:
        print("变量的数量不能少于方程的数量。")
        return
    
    coefficients = get_coefficients(num_equations, num_variables)
    
    solution = find_integer_solution(coefficients, num_variables)
    
    if solution:
        # 确保解的绝对值互质
        coprime_solution = make_solution_coprime(solution)
        print(f"找到方程组的一个整数解: {dict(zip(f'x:{num_variables}', coprime_solution))}")
    else:
        print("在指定范围内没有找到整数解。")

if __name__ == "__main__":
    main()
