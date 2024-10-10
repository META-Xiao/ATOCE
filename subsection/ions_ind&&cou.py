import re

def parse_compound(compound):
    ''' 解析化学式，返回元素及其数量的字典 '''
    counts = {'e': 0}  # 初始化电子数为0
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

# 测试程序
compound1 = "(SO4)2{2-}"
compound2 = "Fe{3+}"
compound3 = "O{2-}"
compound4 = "H{1+}"
print(parse_compound(compound1)) 
print(parse_compound(compound2))  
print(parse_compound(compound3))  
print(parse_compound(compound4))  