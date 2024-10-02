import numpy as np
from fractions import Fraction
'''
由于该代码用于化学方程式的配平，最后不定方程的解分数解可以直接通分
'''
# 输入方程组的系数和常数项
num_equations = int(input("请输入方程的数量: "))
A = []  # 初始化A为一个空列表
for i in range(num_equations):
    eq_input = input(f"请输入方程 {i+1} 的系数（用空格分隔）: ")
    eq_coeffs = list(map(int, eq_input.split()))
    A.append(eq_coeffs)  # 将新的方程系数作为列表添加到A中


B = np.zeros((num_equations,), dtype=int)  
for i in range(num_equations):
    const_input = input(f"请输入方程 {i+1} 的常数项: ")
    B[i] = int(const_input)  # 将常数项添加到B中

# 将A,B转换为NumPy数组
A = np.array(A)
B = np.array(B)

# 打印结果以验证
print("系数矩阵A为：\n", A)
print("常数项向量B为：", B)

# 使用lstsq函数计算最小二乘解
solution, residuals, rank, s = np.linalg.lstsq(A, B, rcond=None)

# 打印最小二乘解
print("方程组的一个解为：", solution)
print("残差为：", residuals)

# 将解向量转换为分数形式
solutionplus = [Fraction(x).limit_denominator() for x in solution]
print("方程组的一个解为：", solutionplus)

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

# 打印结果
print(integers_list)
