# -*-coding:utf-8-*-
# Ks_L = list(range(1, 26))
# alpha_L = list(range(1, 26))
# n_L = list(range(25, 86, 2))
# for Ks in Ks_L:
#     for alpha in alpha_L:
#         alpha = int(alpha) * 0.001
#         # print (f"Ks={Ks},alpha={alpha}") #PYTHON 3.6+

# for Ks in Ks_L:
#     for n in n_L:
#         n = int(n) * 0.01 + 1
#         # print (f"Ks={Ks},n={n}") #PYTHON 3.6+
import subprocess


def modify_input():  # not select the 'hit ENTER at end'in  'print information' of HYDRUS
    # global n
    global alpha
    global Ks
    # COPY
    original = open("SELECTOR.IN", "r")
    infile = open('Selector1.txt', 'w')
    for line in original.readlines():
        infile.write(f'{line}')
    original.close()
    infile.close()

    # RE-WRITE-modify but not write in
    infile = open('Selector1.txt', 'r+')  # if use w+, the reading of file can't work.
    line = infile.readlines()
    thr = 0.044
    ths = 0.3182
    # alpha = 0.00431
    n = 1.6321
    # Ks = 7.5
    line[26] = f'  {thr}  {ths} {alpha}  {n}     {Ks}     0.5\n'  # {}为占位符
    original = open('SELECTOR.IN', 'w+')  # if remove this, the modification will be appended to the original.

    # Write in
    original.writelines(line)
    original.close()
    infile.close()


def extract_BF():
    global Ks
    # global n
    global alpha
    T_level = open('T_level.out', "r")
    T_level_copy = open("BF-collect.txt", "a")
    T_level_copy.write("Ks,alpha,time,vBot" + "\n")  # modified
    T_level.seek(0)
    for line in T_level.readlines()[9:]:  # type: string
        line = line.split()  # transfer string to list
        if line[0] != "end":
            time = float(line[0])  # type:string
            BF = float(line[5])  # type: list
            # T_level_copy.write(f'{Ks:.1f},{n:.3f},{time:.3f},{BF:.3f}' + '\n')  # modified
            T_level_copy.write(f'{Ks:.1f},{alpha:.5f},{time:.3f},{BF:.3f}' + '\n')  # modified
    T_level.close()
    T_level_copy.close()


def extract_WC():
    global Ks
    # global n
    global alpha
    Obs_output = open('Obs_Node.out', "r")
    Obs_copy = open("Water Content-collect.txt", "a")  # It will not empty the file first, it should be improved
    # Modify the first line.
    line = Obs_output.readlines()[8]
    # line=line.replace(" ","")# The line in file1 can not be changed, so we should give another variable to store.
    title_list = line.replace(" ", "")
    title_list = title_list.replace("(", "")
    title_list = title_list.split(")")  # due to he irregular format, it takes steps to extract right header.
    title_list.insert(0, "time")
    title_list.pop()
    title_list = ",".join(title_list)
    Obs_copy.write('Ks,alpha,' + title_list + "\n")  # write title

    Obs_output.seek(0)  # point to the beginning again
    for line in Obs_output.readlines()[11:]:  # type: string
        line = line.split()  # transfer string to list
        if line[0] != "end":
            time = float(line[0])  # type:string
            WC = line[2:40:4]
            WC = ",".join(WC)  # transfer list to string, then the [] in copy file will be removed.
            # Obs_copy.write(f'{Ks:.1f},{n:.3f},{time:.3f},{WC}' + '\n')
            Obs_copy.write(f'{Ks:.1f},{alpha:.5f},{time:.3f},{WC}' + '\n')
    Obs_output.close()
    Obs_copy.close()


Ks_L = list(range(1, 26))
alpha_L = list(range(1, 26))
n_L = list(range(25, 86, 2))

# # modify n and Ks,rerun and extract.( 'main ')

# for Ks in Ks_L:
#     for n in n_L:
#         n = int(n) * 0.01 + 1
#         modify_input()
#         subprocess.run('H1D_CALC')  # LEVEL_01.DIR should in the same path with .py file.
#         extract_BF()
#         extract_WC()

# 运行前检查BF-collect.txt和Water Content-collect.txt文件是否存在。
# 由于需要采集每次运行结果，所以用'a'来写入文件。
# 但是采用'a'会造成一个结果：如果多次运行该.py程序，会造成多次的结果也都添加进该文件，所以需要先删除已存在的该文件。
import os

# 防止'a'使得文件结果多次运行多次提取
file_path1 = os.getcwd() + '/' + 'BF-collect.txt'  # 获得该文件路径
file_path2 = os.getcwd() + '/' + 'Water Content-collect.txt'
if os.path.exists(file_path1) or os.path.exists(file_path2):
    os.remove(file_path1)
    os.remove(file_path2)
    for Ks in Ks_L:
        for alpha in alpha_L:
            alpha = int(alpha) * 0.001
            modify_input()
            subprocess.run('H1D_CALC')  # LEVEL_01.DIR文件必须与需执行的.PY文件在相同路径中
            extract_BF()
            extract_WC()
    print('已删除原有含水率和下边界通量的汇总txt文件，并重新运行！')
else:
    for Ks in Ks_L:
        for alpha in alpha_L:
            alpha = int(alpha) * 0.001
            modify_input()
            subprocess.run('H1D_CALC')  # LEVEL_01.DIR文件必须与需执行的.PY文件在相同路径中
            extract_BF()
            extract_WC()
    print('不存在前期的含水率和下边界通量的汇总txt文件，运行成功！')
