import os
import sys
import subprocess
import platform
def trim_string(s: str) -> str:
    return s.strip() if s else ''
def get_current_dir() -> str:
    return os.getcwd()
def clear_screen():
    os.system('cls' if platform.system() == 'Windows' else 'clear')
def show_global_help():
    help_text = """========================================================
                中文命令终端
      2024-2025 powered by LemonXC - 全局帮助说明
========================================================
【目录操作类】
  查看目录      - 列出当前/指定目录下的文件和文件夹（对应dir）
  切换目录      - 切换当前工作目录（对应cd）
  新建目录      - 创建文件夹，支持多级目录（对应md）
  删除目录      - 删除空/非空文件夹（对应rd）
【文件操作类】
  复制文件      - 复制文件/批量文件到指定路径（对应copy）
  移动文件      - 移动/重命名文件（对应move）
  删除文件      - 删除文件/批量文件（对应del）
  重命名文件    - 重命名文件/批量文件（对应ren）
【系统高级类】
  清屏          - 清空终端输出（对应cls）
  查看进程      - 列出系统所有进程（对应tasklist）
  结束进程      - 终止指定进程（对应taskkill）
  系统信息      - 查看系统详细信息（对应systeminfo）
  查看IP        - 查看网络IP/释放/重新获取IP（对应ipconfig）
  环境变量      - 查看/修改/删除环境变量（对应set）
  查看路径      - 查看/修改系统执行路径（对应path）
【常用工具类】
  打开记事本    - 启动Windows记事本（对应notepad）
  打开计算器    - 启动Windows计算器（对应calc）
  打开注册表    - 启动注册表编辑器（对应regedit）
  打开任务管理器- 启动Windows任务管理器（对应taskmgr）
【自定义设置类】
  自定义命令      - 设置/查看/删除/保存自定义命令别名（对应doskey）
【系统映像维护类】
  系统映像管理    - 系统映像维护、修复（对应dism）
【计算与打印类】
  计算          - 计算数学算式并打印结果
  打印          - 打印文件（对应print）
【使用说明类】
  帮助 指令名   - 查看指定指令的详细用法（如：帮助 查看目录）
  退出          - 关闭中文命令终端（对应exit）
【高级用法】
  1. 支持原生CMD参数（如：查看目录 D:\文档 /s /a）
  2. 可直接执行原生CMD英文指令（如dir/cd/ipconfig）
  3. 支持执行.bat/.cmd/.py脚本（输入完整路径即可）
========================================================"""
    print(help_text)
def show_single_help(cmd_name: str):
    help_mapping = {
        "查看目录": """========================================================
  指令：查看目录（对应英文指令：dir）
========================================================
功能：列出指定目录下的文件/文件夹，包含大小、修改时间等信息
用法：
  1. 查看目录                - 列出当前目录所有内容
  2. 查看目录 目标路径       - 列出指定路径内容（如：查看目录 D:\文档）
  3. 查看目录 /w              - 宽格式显示（仅文件名/文件夹名）
  4. 查看目录 /s              - 递归列出所有子目录内容
  5. 查看目录 /a              - 显示隐藏/系统文件
  6. 查看目录 > 目录.txt      - 将结果保存到文件
========================================================""",
        "切换目录": """========================================================
  指令：切换目录（对应英文指令：cd）
========================================================
功能：切换当前工作目录，支持盘符切换、上级目录跳转
用法：
  1. 切换目录 ..              - 跳转到上级目录
  2. 切换目录 目标路径       - 跳转到指定路径（如：切换目录 D:\Program Files）
  3. 切换目录 /d 盘符\路径    - 跨盘符切换（如：切换目录 /d E:\数据）
  4. 直接输入 盘符:           - 切换盘符（如：D:、E:）
========================================================""",
        "新建目录": """========================================================
  指令：新建目录（对应英文指令：md/mkdir）
========================================================
功能：创建文件夹，支持一次性创建多级目录
用法：
  1. 新建目录 文件夹名        - 创建单层目录（如：新建目录 我的文档）
  2. 新建目录 路径\文件夹名    - 指定路径创建（如：新建目录 D:\备份\2026）
  3. 新建目录 文件夹1\文件夹2  - 多级目录（如：新建目录 a\b\c）
========================================================""",
        "删除目录": """========================================================
  指令：删除目录（对应英文指令：rd/rmdir）
========================================================
功能：删除空/非空文件夹，谨慎使用！
用法：
  1. 删除目录 文件夹名        - 删除空文件夹（如：删除目录 空文件夹）
  2. 删除目录 文件夹名 /s      - 删除非空文件夹（含子目录/文件）
  3. 删除目录 文件夹名 /s /q   - 静默删除非空文件夹（无确认提示）
========================================================""",
        "复制文件": """========================================================
  指令：复制文件（对应英文指令：copy）
========================================================
功能：复制单个/批量文件到指定路径
用法：
  1. 复制文件 源文件 目标路径  - 复制单个文件（如：复制文件 1.txt D:\数据）
  2. 复制文件 *.txt 目标路径   - 批量复制（如：复制文件 *.txt D:\备份）
  3. 复制文件 源文件 新文件名  - 复制并重命名（如：复制文件 1.txt D:\2.txt）
========================================================""",
        "移动文件": """========================================================
  指令：移动文件（对应英文指令：move）
========================================================
功能：移动文件/批量文件，也可用于文件重命名
用法：
  1. 移动文件 源文件 目标路径  - 移动单个文件（如：移动文件 1.txt D:\数据）
  2. 移动文件 *.txt 目标路径   - 批量移动（如：移动文件 *.txt D:\备份）
  3. 移动文件 旧文件名 新文件名 - 重命名（如：移动文件 1.txt 2.txt）
========================================================""",
        "删除文件": """========================================================
  指令：删除文件（对应英文指令：del）
========================================================
功能：删除单个/批量文件，谨慎使用！
用法：
  1. 删除文件 文件名          - 删除单个文件（如：删除文件 1.txt）
  2. 删除文件 *.txt           - 批量删除（如：删除文件 *.txt）
  3. 删除文件 /f              - 强制删除只读文件
  4. 删除文件 /s              - 递归删除所有子目录的对应文件
========================================================""",
        "重命名文件": """========================================================
  指令：重命名文件（对应英文指令：ren/rename）
========================================================
功能：重命名单个/批量文件
用法：
  1. 重命名文件 旧文件名 新文件名  - 单个文件重命名（如：重命名文件 1.txt 2.txt）
  2. 重命名文件 *.txt *.bak        - 批量重命名（如：所有.txt改为.bak）
========================================================""",
        "查看进程": """========================================================
  指令：查看进程（对应英文指令：tasklist）
========================================================
功能：列出系统所有进程，包含PID、内存占用等信息
用法：
  1. 查看进程                - 列出所有进程
  2. 查看进程 /fi "PID eq 1234" - 筛选指定PID的进程
  3. 查看进程 /fi "IMAGENAME eq notepad.exe" - 筛选指定名称的进程
========================================================""",
        "结束进程": """========================================================
  指令：结束进程（对应英文指令：taskkill）
========================================================
功能：终止指定进程，谨慎使用！
用法：
  1. 结束进程 notepad.exe     - 终止所有记事本进程
  2. 结束进程 /pid 1234       - 终止指定PID的进程
  3. 结束进程 /im notepad.exe /f - 强制终止记事本进程
========================================================""",
        "查看IP": """========================================================
  指令：查看IP（对应英文指令：ipconfig）
========================================================
功能：查看网络IP信息，支持释放/重新获取IP
用法：
  1. 查看IP                  - 查看核心IP信息
  2. 查看IP /all              - 查看详细信息（MAC地址、DNS等）
  3. 查看IP /release          - 释放当前IP（仅动态IP有效）
  4. 查看IP /renew            - 重新获取IP（仅动态IP有效）
=======================================================""",
        "自定义命令": """========================================================
  指令：自定义命令（对应英文指令：doskey）
========================================================
功能：设置、查看、删除、保存/加载自定义命令别名，方便快速执行常用指令
用法：
  1. 自定义命令                - 查看所有已设置的自定义命令别名
  2. 自定义命令 别名=指令        - 设置自定义命令（如：自定义命令 清=清屏）
  3. 自定义命令 /d 别名          - 删除指定自定义命令（如：自定义命令 /d 清）
  4. 自定义命令 /s 文件名        - 将别名保存到指定文件（如：自定义命令 /s 别名.txt）
  5. 自定义命令 /r 文件名        - 从指定文件加载别名（如：自定义命令 /r 别名.txt）
========================================================""",
        "系统映像管理": """========================================================
  指令：系统映像管理（对应英文指令：dism）
========================================================
功能：系统映像维护、修复、检查，需管理员权限运行
用法：
  1. 系统映像管理 /online /cleanup-image /scanhealth - 扫描系统映像健康状态
  2. 系统映像管理 /online /cleanup-image /restorehealth - 修复系统映像
  3. 系统映像管理 /online /get-packages - 查看已安装的更新包
  4. 系统映像管理 /mount-wim /wimfile:文件路径 /index:1 /mountdir:挂载路径 - 挂载WIM映像
  5. 系统映像管理 /unmount-wim /mountdir:挂载路径 /commit - 卸载并保存WIM映像修改
=======================================================""",
        "计算": """========================================================
  指令：计算
========================================================
功能：计算数学算式并打印结果
用法：
  1. 计算 算式                - 计算指定数学算式（如：计算 1+2*3）
  2. 直接输入算式（如：1+2*3）- 直接计算结果
支持的运算符：+、-、*、/、//、%、**（幂运算）、()（括号）
=======================================================""",
        "打印": """========================================================
  指令：打印（对应英文指令：print）
========================================================
功能：打印指定文件
用法：
  1. 打印 文件名                - 打印指定文件（如：打印 文档.txt）
  2. 打印 /d:打印机名 文件名    - 指定打印机打印文件（如：打印 /d:HP打印机 文档.txt）
  3. 打印 /?                    - 查看打印命令详细参数
======================================================="""
    }
    print(help_mapping.get(cmd_name, f"""========================================================
[错误] 未找到「{cmd_name}」的帮助信息，请输入【帮助】查看有效指令列表
======================================================="""))
def run_cmd(command: str, wait: bool = True):
    try:
        if wait:
            result = subprocess.run(
                command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='ANSI'
            )
            print(result.stdout)
            if result.stderr:
                print(f"[错误] {result.stderr}")
            return result.returncode
        else:
            subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return 0
    except Exception as e:
        print(f"[执行失败] {str(e)}")
        return -1
def main():
    print("中文版命令提示符 [版本2.3.260201.2054]")
    print("(c) LemonXC。保留所有权利。输入[帮助]查看完整指令列表。\n")
    while True:
        current_dir = get_current_dir()
        prompt = f"{current_dir}\\"
        try:
            user_input = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print("\n终端已退出")
            break
        user_input_trim = trim_string(user_input)
        if not user_input_trim:
            continue
        if user_input_trim in ["帮助", "/?"]:
            show_global_help()
            continue
        if user_input_trim.startswith("帮助 "):
            cmd_name = trim_string(user_input_trim[2:])
            show_single_help(cmd_name)
            continue
        if user_input_trim == "查看目录":
            run_cmd("dir")
            continue
        if user_input_trim.startswith("查看目录 "):
            param = trim_string(user_input_trim[4:])
            run_cmd(f"dir {param}")
            continue
        if user_input_trim == "切换目录":
            print("[提示] 切换目录用法：切换目录 目标路径（如：切换目录 D:\文档 或 切换目录 ..）")
            print("输入【帮助 切换目录】查看详细用法")
            continue
        if user_input_trim.startswith("切换目录 "):
            param = trim_string(user_input_trim[4:])
            try:
                if param.startswith("/d"):
                    os.chdir(trim_string(param[2:]))
                else:
                    os.chdir(param)
                print(f"当前目录已切换为：{os.getcwd()}")
            except Exception as e:
                print(f"[错误] 切换目录失败：{str(e)}")
            continue
        if len(user_input_trim) == 2 and user_input_trim[0].isalpha() and user_input_trim[1] == ":":
            try:
                os.chdir(user_input_trim)
                print(f"盘符已切换为：{user_input_trim}")
            except Exception as e:
                print(f"[错误] 盘符切换失败：{str(e)}")
            continue
        if user_input_trim == "新建目录":
            print("[提示] 新建目录用法：新建目录 文件夹名（如：新建目录 我的文件夹）")
            print("输入【帮助 新建目录】查看详细用法")
            continue
        if user_input_trim.startswith("新建目录 "):
            param = trim_string(user_input_trim[4:])
            ret = run_cmd(f"md {param}")
            if ret == 0:
                print(f"目录「{param}」创建成功！")
            continue
        if user_input_trim == "删除目录":
            print("[提示] 删除目录用法：删除目录 文件夹名（如：删除目录 空文件夹）")
            print("输入【帮助 删除目录】查看详细用法")
            continue
        if user_input_trim.startswith("删除目录 "):
            param = trim_string(user_input_trim[4:])
            run_cmd(f"rd {param}")
            continue
        if user_input_trim == "复制文件":
            print("[提示] 复制文件用法：复制文件 源文件 目标路径（如：复制文件 1.txt D:\数据）")
            print("输入【帮助 复制文件】查看详细用法")
            continue
        if user_input_trim.startswith("复制文件 "):
            param = trim_string(user_input_trim[4:])
            run_cmd(f"copy {param}")
            continue
        if user_input_trim == "移动文件":
            print("[提示] 移动文件用法：移动文件 源文件 目标路径（如：移动文件 1.txt D:\数据）")
            print("输入【帮助 移动文件】查看详细用法")
            continue
        if user_input_trim.startswith("移动文件 "):
            param = trim_string(user_input_trim[4:])
            run_cmd(f"move {param}")
            continue
        if user_input_trim == "删除文件":
            print("[提示] 删除文件用法：删除文件 文件名（如：删除文件 1.txt）")
            print("输入【帮助 删除文件】查看详细用法")
            continue
        if user_input_trim.startswith("删除文件 "):
            param = trim_string(user_input_trim[4:])
            run_cmd(f"del {param}")
            continue
        if user_input_trim == "重命名文件":
            print("[提示] 重命名文件用法：重命名文件 旧文件名 新文件名（如：重命名文件 1.txt 2.txt）")
            print("输入【帮助 重命名文件】查看详细用法")
            continue
        if user_input_trim.startswith("重命名文件 "):
            param = trim_string(user_input_trim[6:])
            run_cmd(f"ren {param}")
            continue
        if user_input_trim == "清屏":
            clear_screen()
            continue
        if user_input_trim == "查看进程":
            run_cmd("tasklist")
            continue
        if user_input_trim.startswith("查看进程 "):
            param = trim_string(user_input_trim[4:])
            run_cmd(f"tasklist {param}")
            continue
        if user_input_trim == "结束进程":
            print("[提示] 结束进程用法：结束进程 进程名/PID（如：结束进程 notepad.exe 或 结束进程 /pid 1234）")
            print("输入【帮助 结束进程】查看详细用法")
            continue
        if user_input_trim.startswith("结束进程 "):
            param = trim_string(user_input_trim[4:])
            run_cmd(f"taskkill /f /im {param} || taskkill /f {param}")
            continue
        if user_input_trim == "系统信息":
            run_cmd("systeminfo")
            continue
        if user_input_trim.startswith("系统信息 "):
            param = trim_string(user_input_trim[4:])
            run_cmd(f"systeminfo {param}")
            continue
        if user_input_trim == "查看IP":
            run_cmd("ipconfig /all")
            continue
        if user_input_trim.startswith("查看IP "):
            param = trim_string(user_input_trim[4:])
            run_cmd(f"ipconfig {param}")
            continue
        if user_input_trim == "环境变量":
            run_cmd("set")
            continue
        if user_input_trim.startswith("环境变量 "):
            param = trim_string(user_input_trim[4:])
            run_cmd(f"set {param}")
            continue
        if user_input_trim == "查看路径":
            run_cmd("path")
            continue
        if user_input_trim.startswith("查看路径 "):
            param = trim_string(user_input_trim[4:])
            run_cmd(f"path {param}")
            continue
        if user_input_trim == "打开记事本":
            run_cmd("notepad", wait=False)
            continue
        if user_input_trim == "打开计算器":
            run_cmd("calc", wait=False)
            continue
        if user_input_trim == "打开注册表":
            run_cmd("regedit", wait=False)
            continue
        if user_input_trim == "打开任务管理器":
            run_cmd("taskmgr", wait=False)
            continue
        if user_input_trim == "自定义命令":
            run_cmd("doskey /macros")
            continue
        if user_input_trim.startswith("自定义命令 "):
            param = trim_string(user_input_trim[4:])
            if param.startswith("/d "):
                alias = trim_string(param[3:])
                run_cmd(f"doskey {alias}= ")
            elif param.startswith("/s "):
                filename = trim_string(param[3:])
                run_cmd(f"doskey /macros > {filename}")
                print(f"别名已保存到文件「{filename}」")
            elif param.startswith("/r "):
                filename = trim_string(param[3:])
                run_cmd(f"doskey /macros:<{filename}")
                print(f"已从文件「{filename}」加载别名")
            else:
                run_cmd(f"doskey {param}")
            continue
        if user_input_trim == "系统映像管理":
            print("[提示] 系统映像管理需管理员权限运行，用法：系统映像管理 参数（如：系统映像管理 /online /cleanup-image /scanhealth）")
            print("输入【帮助 系统映像管理】查看详细用法")
            continue
        if user_input_trim.startswith("系统映像管理 "):
            param = trim_string(user_input_trim[5:])
            run_cmd(f"dism {param}")
            continue
        # 计算功能处理
        if user_input_trim == "计算":
            print("[提示] 计算用法：计算 算式（如：计算 1+2*3），或直接输入算式（如：1+2*3）")
            print("输入【帮助 计算】查看详细用法")
            continue
        if user_input_trim.startswith("计算 "):
            expr = trim_string(user_input_trim[2:])
            try:
                result = eval(expr)
                print(f"计算结果：{expr} = {result}")
            except Exception as e:
                print(f"[计算错误] 算式无效：{str(e)}")
            continue
        # 尝试直接处理输入的算式
        has_operator = any(op in user_input_trim for op in ["+", "-", "*", "/", "//", "%", "**", "(", ")"])
        if has_operator:
            try:
                result = eval(user_input_trim)
                print(f"计算结果：{user_input_trim} = {result}")
                continue
            except:
                # 计算失败，当作普通CMD命令执行
                pass
        # 打印功能处理
        if user_input_trim == "打印":
            print("[提示] 打印用法：打印 文件名（如：打印 文档.txt），或打印 /d:打印机名 文件名")
            print("输入【帮助 打印】查看详细用法")
            continue
        if user_input_trim.startswith("打印 "):
            param = trim_string(user_input_trim[2:])
            run_cmd(f"print {param}")
            continue
        if user_input_trim == "退出":
            print("终端已退出")
            break
        ret = run_cmd(user_input_trim)
        if ret != 0:
            print(f"[错误] 指令执行失败或不存在，请输入【帮助】查看可用指令")
if __name__ == "__main__":
    main()