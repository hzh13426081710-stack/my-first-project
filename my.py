total_A_count=0
total_B_count=0
total_C_count=0
total_D_count=0
n=int(input("请输入一个整数班级人数 "))
for _ in range(n):
    name=str(input("请输入一个名字: "))
    chinese_score=float(input("请输入一个语文分数: "))
    math_score=float(input("请输入一个数学分数: "))
    english_score=float(input("请输入一个英语分数: "))
    if chinese_score<0 or chinese_score>100 or math_score<0 or math_score>100 or english_score<0 or english_score>100:
        print("请输入一个0-100之间的分数,程序退出")
        break
    if chinese_score+math_score+english_score>=270:
        grade='A'
        total_A_count+=1
    elif chinese_score+math_score+english_score>=240:
        grade='B'
        total_B_count+=1
    elif chinese_score+math_score+english_score>=210:
        grade='C'
        total_C_count+=1
    else:
        grade='D'
        total_D_count+=1
    print(name,f'总分{chinese_score+math_score+english_score}',f'平均分{(chinese_score+math_score+english_score)/3:.2f}',grade)
else:
    print(f"班级总人数为{n}",f'A级人数为{total_A_count}',f'B级人数为{total_B_count}',f'C级人数为{total_C_count}',f'D级人数为{total_D_count}')