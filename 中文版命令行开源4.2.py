import os
import sys
import subprocess
import platform
import traceback
import locale
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
                             QPlainTextEdit, QLineEdit, QMenuBar, QMenu, QAction, QMessageBox, QPushButton)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QShortcut

def trim_string(s: str) -> str:
    return s.strip() if s else ''

class TerminalTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_dir = os.getcwd()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.output_edit = QPlainTextEdit()
        self.output_edit.setReadOnly(False)

        font = self.output_edit.font()
        font.setFamily("Consolas")
        font.setPointSize(10)
        self.output_edit.setFont(font)

        self.output_edit.setStyleSheet("""
            QPlainTextEdit {
                background-color: #000000;
                color: #ffffff;
                selection-background-color: #0047ab;
                border: none;
                padding: 5px;
            }
        """)

        self.output_edit.installEventFilter(self)

        self.output_edit.setLineWrapMode(QPlainTextEdit.NoWrap)
        layout.addWidget(self.output_edit)
        self.setLayout(layout)

        self.output_edit.appendPlainText("中文版命令行开源版 [版本4.2.26216.2048]")
        self.output_edit.appendPlainText("(c) LemonXC。保留所有权利。输入[帮助]查看完整指令列表。")
        self.show_prompt()

    def eventFilter(self, obj, event):
        from PyQt5.QtCore import QEvent, Qt
        if obj == self.output_edit and event.type() == QEvent.KeyPress:
            cursor = self.output_edit.textCursor()

            if cursor.blockNumber() != self.output_edit.document().blockCount() - 1:

                cursor.movePosition(cursor.End)
                self.output_edit.setTextCursor(cursor)
                return True

            prompt = f"{self.current_dir}>"
            last_block = self.output_edit.document().lastBlock()
            if event.key() == Qt.Key_Backspace:
                if cursor.positionInBlock() <= len(prompt):

                    return True

            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                self.process_command()
                return True

            if event.key() in [Qt.Key_Up, Qt.Key_Down]:
                return True
        return super().eventFilter(obj, event)

    def show_prompt(self):
        prompt = f"{self.current_dir}>"
        self.output_edit.appendPlainText(prompt)
        cursor = self.output_edit.textCursor()
        cursor.movePosition(cursor.End)
        self.output_edit.setTextCursor(cursor)
        self.output_edit.ensureCursorVisible()

    def process_command(self):

        doc = self.output_edit.document()
        last_block = doc.lastBlock()
        line_text = last_block.text().strip()
        prompt = f"{self.current_dir}>"

        if line_text.startswith(prompt):
            command = line_text[len(prompt):].strip()
        else:

            self.output_edit.clear()
            self.output_edit.appendPlainText("中文版命令行开源版 [版本4.2.26216.2048]")
            self.output_edit.appendPlainText("(c) LemonXC。保留所有权利。输入[帮助]查看完整指令列表。")
            self.show_prompt()
            return

        if not command:
            self.show_prompt()
            return

        self.output_edit.appendPlainText("")
        try:
            if command in ["帮助", "/?"]:
                self.show_global_help()
                self.show_prompt()
                return
            if command.startswith("帮助 "):
                cmd_name = trim_string(command[2:])
                self.show_single_help(cmd_name)
                self.show_prompt()
                return

            if command == "查看目录":
                self.run_cmd("dir")
                self.show_prompt()
                return
            if command.startswith("查看目录 "):
                param = trim_string(command[4:])
                self.run_cmd(f"dir {param}")
                self.show_prompt()
                return
            if command == "切换目录":
                self.output_edit.appendPlainText("[提示] 切换目录用法：切换目录 目标路径（如：切换目录 D:\文档 或 切换目录 ..）")
                self.output_edit.appendPlainText("输入【帮助 切换目录】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("切换目录 "):
                param = trim_string(command[4:])
                try:
                    if param.startswith("/d"):
                        os.chdir(trim_string(param[2:]))
                    else:
                        os.chdir(param)
                    self.current_dir = os.getcwd()
                    self.output_edit.appendPlainText(f"当前目录已切换为：{self.current_dir}")
                except Exception as e:
                    self.output_edit.appendPlainText(f"[错误] 切换目录失败：{str(e)}")
                self.show_prompt()
                return
            if len(command) == 2 and command[0].isalpha() and command[1] == ":":
                try:
                    os.chdir(command)
                    self.current_dir = os.getcwd()
                    self.output_edit.appendPlainText(f"盘符已切换为：{command}")
                except Exception as e:
                    self.output_edit.appendPlainText(f"[错误] 盘符切换失败：{str(e)}")
                self.show_prompt()
                return
            if command == "新建目录":
                self.output_edit.appendPlainText("[提示] 新建目录用法：新建目录 文件夹名（如：新建目录 我的文件夹）")
                self.output_edit.appendPlainText("输入【帮助 新建目录】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("新建目录 "):
                param = trim_string(command[4:])
                ret = self.run_cmd(f"md {param}")
                if ret == 0:
                    self.output_edit.appendPlainText(f"目录「{param}」创建成功！")
                self.show_prompt()
                return
            if command == "删除目录":
                self.output_edit.appendPlainText("[提示] 删除目录用法：删除目录 文件夹名（如：删除目录 空文件夹）")
                self.output_edit.appendPlainText("输入【帮助 删除目录】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("删除目录 "):
                param = trim_string(command[4:])
                self.run_cmd(f"rd {param}")
                self.show_prompt()
                return
            if command == "目录树显示":
                self.run_cmd("tree")
                self.show_prompt()
                return
            if command.startswith("目录树显示 "):
                param = trim_string(command[5:])
                self.run_cmd(f"tree {param}")
                self.show_prompt()
                return

            if command == "复制文件":
                self.output_edit.appendPlainText("[提示] 复制文件用法：复制文件 源文件 目标路径（如：复制文件 1.txt D:\数据）")
                self.output_edit.appendPlainText("输入【帮助 复制文件】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("复制文件 "):
                param = trim_string(command[4:])
                self.run_cmd(f"copy {param}")
                self.show_prompt()
                return
            if command == "移动文件":
                self.output_edit.appendPlainText("[提示] 移动文件用法：移动文件 源文件 目标路径（如：移动文件 1.txt D:\数据）")
                self.output_edit.appendPlainText("输入【帮助 移动文件】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("移动文件 "):
                param = trim_string(command[4:])
                self.run_cmd(f"move {param}")
                self.show_prompt()
                return
            if command == "删除文件":
                self.output_edit.appendPlainText("[提示] 删除文件用法：删除文件 文件名（如：删除文件 1.txt）")
                self.output_edit.appendPlainText("输入【帮助 删除文件】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("删除文件 "):
                param = trim_string(command[4:])
                self.run_cmd(f"del {param}")
                self.show_prompt()
                return
            if command == "重命名文件":
                self.output_edit.appendPlainText("[提示] 重命名文件用法：重命名文件 旧文件名 新文件名（如：重命名文件 1.txt 2.txt）")
                self.output_edit.appendPlainText("输入【帮助 重命名文件】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("重命名文件 "):
                param = trim_string(command[6:])
                self.run_cmd(f"ren {param}")
                self.show_prompt()
                return
            if command == "复制目录树":
                self.output_edit.appendPlainText("[提示] 复制目录树用法：复制目录树 源路径 目标路径（如：复制目录树 D:\文档 E:\备份）")
                self.output_edit.appendPlainText("输入【帮助 复制目录树】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("复制目录树 "):
                param = trim_string(command[5:])
                self.run_cmd(f"xcopy {param}")
                self.show_prompt()
                return
            if command == "高级复制":
                self.output_edit.appendPlainText("[提示] 高级复制用法：高级复制 源路径 目标路径（如：高级复制 D:\文档 E:\备份）")
                self.output_edit.appendPlainText("输入【帮助 高级复制】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("高级复制 "):
                param = trim_string(command[4:])
                self.run_cmd(f"robocopy {param}")
                self.show_prompt()
                return
            if command == "替换文件":
                self.output_edit.appendPlainText("[提示] 替换文件用法：替换文件 源文件 目标路径（如：替换文件 1.txt D:\数据）")
                self.output_edit.appendPlainText("输入【帮助 替换文件】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("替换文件 "):
                param = trim_string(command[4:])
                self.run_cmd(f"replace {param}")
                self.show_prompt()
                return
            if command == "查看文件内容":
                self.output_edit.appendPlainText("[提示] 查看文件内容用法：查看文件内容 文件名（如：查看文件内容 文档.txt）")
                self.output_edit.appendPlainText("输入【帮助 查看文件内容】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("查看文件内容 "):
                param = trim_string(command[6:])
                self.run_cmd(f"type {param}")
                self.show_prompt()
                return
            if command == "恢复文件":
                self.output_edit.appendPlainText("[提示] 恢复文件用法：恢复文件 文件名（如：恢复文件 损坏.txt）")
                self.output_edit.appendPlainText("输入【帮助 恢复文件】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("恢复文件 "):
                param = trim_string(command[4:])
                self.run_cmd(f"recover {param}")
                self.show_prompt()
                return

            if command == "文件关联":
                self.run_cmd("assoc")
                self.show_prompt()
                return
            if command.startswith("文件关联 "):
                param = trim_string(command[4:])
                self.run_cmd(f"assoc {param}")
                self.show_prompt()
                return
            if command == "文件属性":
                self.run_cmd("attrib")
                self.show_prompt()
                return
            if command.startswith("文件属性 "):
                param = trim_string(command[4:])
                self.run_cmd(f"attrib {param}")
                self.show_prompt()
                return
            if command == "比较文件":
                self.output_edit.appendPlainText("[提示] 比较文件用法：比较文件 文件1 文件2（如：比较文件 1.txt 2.txt）")
                self.output_edit.appendPlainText("输入【帮助 比较文件】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("比较文件 "):
                param = trim_string(command[4:])
                self.run_cmd(f"comp {param}")
                self.show_prompt()
                return
            if command == "文件比较":
                self.output_edit.appendPlainText("[提示] 文件比较用法：文件比较 文件1 文件2（如：文件比较 1.txt 2.txt）")
                self.output_edit.appendPlainText("输入【帮助 文件比较】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("文件比较 "):
                param = trim_string(command[4:])
                self.run_cmd(f"fc {param}")
                self.show_prompt()
                return
            if command == "NTFS压缩":
                self.run_cmd("compact")
                self.show_prompt()
                return
            if command.startswith("NTFS压缩 "):
                param = trim_string(command[5:])
                self.run_cmd(f"compact {param}")
                self.show_prompt()
                return
            if command == "转换分区格式":
                self.output_edit.appendPlainText("[提示] 转换分区格式用法：转换分区格式 盘符: /fs:ntfs（如：转换分区格式 D: /fs:ntfs）")
                self.output_edit.appendPlainText("输入【帮助 转换分区格式】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("转换分区格式 "):
                param = trim_string(command[6:])
                self.run_cmd(f"convert {param}")
                self.show_prompt()
                return
            if command == "查找文本":
                self.output_edit.appendPlainText("[提示] 查找文本用法：查找文本 \"字符串\" 文件名（如：查找文本 \"测试\" 1.txt）")
                self.output_edit.appendPlainText("输入【帮助 查找文本】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("查找文本 "):
                param = trim_string(command[4:])
                self.run_cmd(f"find {param}")
                self.show_prompt()
                return
            if command == "查找字符串":
                self.output_edit.appendPlainText("[提示] 查找字符串用法：查找字符串 \"字符串\" 文件名（如：查找字符串 \"测试\" 1.txt）")
                self.output_edit.appendPlainText("输入【帮助 查找字符串】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("查找字符串 "):
                param = trim_string(command[5:])
                self.run_cmd(f"findstr {param}")
                self.show_prompt()
                return
            if command == "格式化磁盘":
                self.output_edit.appendPlainText("[提示] 格式化磁盘用法：格式化磁盘 盘符:（如：格式化磁盘 D:），谨慎使用！")
                self.output_edit.appendPlainText("输入【帮助 格式化磁盘】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("格式化磁盘 "):
                param = trim_string(command[5:])
                self.run_cmd(f"format {param}")
                self.show_prompt()
                return
            if command == "文件系统配置":
                self.output_edit.appendPlainText("[提示] 文件系统配置用法：文件系统配置 fsinfo drives（显示所有驱动器）")
                self.output_edit.appendPlainText("输入【帮助 文件系统配置】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("文件系统配置 "):
                param = trim_string(command[6:])
                self.run_cmd(f"fsutil {param}")
                self.show_prompt()
                return
            if command == "文件类型关联":
                self.run_cmd("ftype")
                self.show_prompt()
                return
            if command.startswith("文件类型关联 "):
                param = trim_string(command[6:])
                self.run_cmd(f"ftype {param}")
                self.show_prompt()
                return
            if command == "磁盘卷标":
                self.output_edit.appendPlainText("[提示] 磁盘卷标用法：磁盘卷标 盘符: 卷标名（如：磁盘卷标 D: 数据盘）")
                self.output_edit.appendPlainText("输入【帮助 磁盘卷标】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("磁盘卷标 "):
                param = trim_string(command[4:])
                self.run_cmd(f"label {param}")
                self.show_prompt()
                return
            if command == "创建链接":
                self.output_edit.appendPlainText("[提示] 创建链接用法：创建链接 链接名 目标路径（如：创建链接 文档链接 D:\文档）")
                self.output_edit.appendPlainText("输入【帮助 创建链接】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("创建链接 "):
                param = trim_string(command[4:])
                self.run_cmd(f"mklink {param}")
                self.show_prompt()
                return
            if command == "打开文件查询":
                self.run_cmd("openfiles /query")
                self.show_prompt()
                return
            if command.startswith("打开文件查询 "):
                param = trim_string(command[5:])
                self.run_cmd(f"openfiles {param}")
                self.show_prompt()
                return

            if command == "中断检查":
                self.run_cmd("break")
                self.show_prompt()
                return
            if command.startswith("中断检查 "):
                param = trim_string(command[4:])
                self.run_cmd(f"break {param}")
                self.show_prompt()
                return
            if command == "启动配置":
                self.output_edit.appendPlainText("[提示] 启动配置需管理员权限运行，输入【帮助 启动配置】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("启动配置 "):
                param = trim_string(command[4:])
                self.run_cmd(f"bcdedit {param}")
                self.show_prompt()
                return
            if command == "访问控制列表":
                self.output_edit.appendPlainText("[提示] 访问控制列表用法：访问控制列表 文件名（如：访问控制列表 1.txt）")
                self.output_edit.appendPlainText("输入【帮助 访问控制列表】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("访问控制列表 "):
                param = trim_string(command[6:])
                self.run_cmd(f"icacls {param}")
                self.show_prompt()
                return
            if command == "代码页设置":
                self.run_cmd("chcp")
                self.show_prompt()
                return
            if command.startswith("代码页设置 "):
                param = trim_string(command[5:])
                self.run_cmd(f"chcp {param}")
                self.show_prompt()
                return
            if command == "打开命令窗口":
                self.run_cmd("cmd", wait=False)
                self.show_prompt()
                return
            if command.startswith("打开命令窗口 "):
                param = trim_string(command[5:])
                self.run_cmd(f"cmd {param}", wait=False)
                self.show_prompt()
                return
            if command == "驱动查询":
                self.run_cmd("driverquery")
                self.show_prompt()
                return
            if command.startswith("驱动查询 "):
                param = trim_string(command[4:])
                self.run_cmd(f"driverquery {param}")
                self.show_prompt()
                return
            if command == "设备配置":
                self.output_edit.appendPlainText("[提示] 设备配置用法：设备配置 con: cols=80 lines=25（设置控制台大小）")
                self.output_edit.appendPlainText("输入【帮助 设备配置】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("设备配置 "):
                param = trim_string(command[4:])
                self.run_cmd(f"mode {param}")
                self.show_prompt()
                return
            if command == "命令提示设置":
                self.run_cmd("prompt")
                self.show_prompt()
                return
            if command.startswith("命令提示设置 "):
                param = trim_string(command[5:])
                self.run_cmd(f"prompt {param}")
                self.show_prompt()
                return
            if command == "服务配置":
                self.output_edit.appendPlainText("[提示] 服务配置需管理员权限运行，输入【帮助 服务配置】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("服务配置 "):
                param = trim_string(command[4:])
                self.run_cmd(f"sc {param}")
                self.show_prompt()
                return
            if command == "任务计划":
                self.run_cmd("schtasks /query")
                self.show_prompt()
                return
            if command.startswith("任务计划 "):
                param = trim_string(command[4:])
                self.run_cmd(f"schtasks {param}")
                self.show_prompt()
                return
            if command == "关闭计算机":
                self.output_edit.appendPlainText("[提示] 关闭计算机用法：关闭计算机 /s（关闭本地计算机）")
                self.output_edit.appendPlainText("输入【帮助 关闭计算机】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("关闭计算机 "):
                param = trim_string(command[5:])
                self.run_cmd(f"shutdown {param}")
                self.show_prompt()
                return
            if command == "排序输入":
                self.output_edit.appendPlainText("[提示] 排序输入用法：sort < 文件名（如：sort < 1.txt）")
                self.output_edit.appendPlainText("输入【帮助 排序输入】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("排序输入 "):
                param = trim_string(command[4:])
                self.run_cmd(f"sort {param}")
                self.show_prompt()
                return
            if command == "启动程序":
                self.output_edit.appendPlainText("[提示] 启动程序用法：启动程序 程序名（如：启动程序 notepad）")
                self.output_edit.appendPlainText("输入【帮助 启动程序】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("启动程序 "):
                param = trim_string(command[4:])
                self.run_cmd(f"start {param}", wait=False)
                self.show_prompt()
                return
            if command == "时间设置":
                self.run_cmd("time")
                self.show_prompt()
                return
            if command.startswith("时间设置 "):
                param = trim_string(command[4:])
                self.run_cmd(f"time {param}")
                self.show_prompt()
                return
            if command == "窗口标题设置":
                self.output_edit.appendPlainText("[提示] 窗口标题设置用法：窗口标题设置 标题名（如：窗口标题设置 我的终端）")
                self.output_edit.appendPlainText("输入【帮助 窗口标题设置】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("窗口标题设置 "):
                param = trim_string(command[6:])
                self.window().setWindowTitle(param)
                self.show_prompt()
                return
            if command == "查看Windows版本":
                self.run_cmd("ver")
                self.show_prompt()
                return
            if command == "文件写入验证":
                self.run_cmd("verify")
                self.show_prompt()
                return
            if command.startswith("文件写入验证 "):
                param = trim_string(command[6:])
                self.run_cmd(f"verify {param}")
                self.show_prompt()
                return
            if command == "磁盘卷标查看":
                self.run_cmd("vol")
                self.show_prompt()
                return
            if command.startswith("磁盘卷标查看 "):
                param = trim_string(command[5:])
                self.run_cmd(f"vol {param}")
                self.show_prompt()
                return
            if command == "WMI信息查询":
                self.output_edit.appendPlainText("[提示] WMI信息查询用法：WMI信息查询 cpu get name（查看CPU名称）")
                self.output_edit.appendPlainText("输入【帮助 WMI信息查询】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("WMI信息查询 "):
                param = trim_string(command[5:])
                self.run_cmd(f"wmic {param}")
                self.show_prompt()
                return

            if command == "清屏":
                self.output_edit.clear()
                self.output_edit.appendPlainText("中文版命令行开源版 [版本3.6.26213.1632]")
                self.output_edit.appendPlainText("(c) LemonXC。保留所有权利。输入[帮助]查看完整指令列表。\n")
                self.show_prompt()
                return
            if command == "查看进程":
                self.run_cmd("tasklist")
                self.show_prompt()
                return
            if command.startswith("查看进程 "):
                param = trim_string(command[4:])
                self.run_cmd(f"tasklist {param}")
                self.show_prompt()
                return
            if command == "结束进程":
                self.output_edit.appendPlainText("[提示] 结束进程用法：结束进程 进程名/PID（如：结束进程 notepad.exe 或 结束进程 /pid 1234）")
                self.output_edit.appendPlainText("输入【帮助 结束进程】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("结束进程 "):
                param = trim_string(command[4:])
                self.run_cmd(f"taskkill /f /im {param} || taskkill /f {param}")
                self.show_prompt()
                return
            if command == "系统信息":
                self.run_cmd("systeminfo")
                self.show_prompt()
                return
            if command.startswith("系统信息 "):
                param = trim_string(command[4:])
                self.run_cmd(f"systeminfo {param}")
                self.show_prompt()
                return
            if command == "查看IP":
                self.run_cmd("ipconfig /all")
                self.show_prompt()
                return
            if command.startswith("查看IP "):
                param = trim_string(command[4:])
                self.run_cmd(f"ipconfig {param}")
                self.show_prompt()
                return
            if command == "环境变量":
                self.run_cmd("set")
                self.show_prompt()
                return
            if command.startswith("环境变量 "):
                param = trim_string(command[4:])
                self.run_cmd(f"set {param}")
                self.show_prompt()
                return
            if command == "查看路径":
                self.run_cmd("path")
                self.show_prompt()
                return
            if command.startswith("查看路径 "):
                param = trim_string(command[4:])
                self.run_cmd(f"path {param}")
                self.show_prompt()
                return
            if command == "磁盘分区管理":
                self.output_edit.appendPlainText("[提示] 磁盘分区管理需管理员权限运行，输入【帮助 磁盘分区管理】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("磁盘分区管理 "):
                param = trim_string(command[5:])
                self.run_cmd(f"diskpart {param}")
                self.show_prompt()
                return
            if command == "查看映像":
                self.run_cmd("subst")
                self.show_prompt()
                return
            if command == "挂载映像":
                self.output_edit.appendPlainText("[提示] 挂载映像用法：挂载映像 盘符: 目标路径（如：挂载映像 Z: D:\镜像文件.iso）")
                self.output_edit.appendPlainText("输入【帮助 挂载映像】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("挂载映像 "):
                param = trim_string(command[4:])
                self.run_cmd(f"subst {param}")
                self.show_prompt()
                return
            if command == "卸载映像":
                self.output_edit.appendPlainText("[提示] 卸载映像用法：卸载映像 盘符:（如：卸载映像 Z:）")
                self.output_edit.appendPlainText("输入【帮助 卸载映像】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("卸载映像 "):
                param = trim_string(command[4:])
                self.run_cmd(f"subst {param} /d")
                self.show_prompt()
                return

            if command == "打开记事本":
                self.run_cmd("notepad", wait=False)
                self.show_prompt()
                return
            if command == "打开计算器":
                self.run_cmd("calc", wait=False)
                self.show_prompt()
                return
            if command == "打开注册表":
                self.run_cmd("regedit", wait=False)
                self.show_prompt()
                return
            if command == "打开任务管理器":
                self.run_cmd("taskmgr", wait=False)
                self.show_prompt()
                return
            if command == "分屏显示":
                self.output_edit.appendPlainText("[提示] 分屏显示用法：more < 文件名（如：more < 1.txt）")
                self.output_edit.appendPlainText("输入【帮助 分屏显示】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("分屏显示 "):
                param = trim_string(command[4:])
                self.run_cmd(f"more {param}")
                self.show_prompt()
                return
            if command == "暂停批处理":
                self.output_edit.appendPlainText("请按任意键继续...")
                QMessageBox.information(self, "暂停", "请按确定继续...")
                self.show_prompt()
                return

            if command == "调用批处理":
                self.output_edit.appendPlainText("[提示] 调用批处理用法：调用批处理 批处理文件名（如：调用批处理 1.bat）")
                self.output_edit.appendPlainText("输入【帮助 调用批处理】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("调用批处理 "):
                param = trim_string(command[5:])
                self.run_cmd(f"call {param}")
                self.show_prompt()
                return
            if command == "回显":
                self.run_cmd("echo")
                self.show_prompt()
                return
            if command.startswith("回显 "):
                param = trim_string(command[4:])
                self.run_cmd(f"echo {param}")
                self.show_prompt()
                return
            if command == "结束本地环境":
                self.output_edit.appendPlainText("[提示] 结束本地环境用于批处理文件中，输入【帮助 结束本地环境】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("结束本地环境 "):
                param = trim_string(command[6:])
                self.run_cmd(f"endlocal {param}")
                self.show_prompt()
                return
            if command == "批处理循环":
                self.output_edit.appendPlainText("[提示] 批处理循环用法：for %i in (*.txt) do 命令 %i（如：for %i in (*.txt) do type %i）")
                self.output_edit.appendPlainText("输入【帮助 批处理循环】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("批处理循环 "):
                param = trim_string(command[5:])
                self.run_cmd(f"for {param}")
                self.show_prompt()
                return
            if command == "批处理跳转":
                self.output_edit.appendPlainText("[提示] 批处理跳转用于批处理文件中，输入【帮助 批处理跳转】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("批处理跳转 "):
                param = trim_string(command[5:])
                self.run_cmd(f"goto {param}")
                self.show_prompt()
                return
            if command == "组策略信息":
                self.run_cmd("gpresult /r")
                self.show_prompt()
                return
            if command.startswith("组策略信息 "):
                param = trim_string(command[5:])
                self.run_cmd(f"gpresult {param}")
                self.show_prompt()
                return
            if command == "扩展字符集":
                self.output_edit.appendPlainText("[提示] 扩展字符集用法：扩展字符集 代码页号（如：扩展字符集 936）")
                self.output_edit.appendPlainText("输入【帮助 扩展字符集】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("扩展字符集 "):
                param = trim_string(command[5:])
                self.run_cmd(f"graftabl {param}")
                self.show_prompt()
                return
            if command == "批处理条件":
                self.output_edit.appendPlainText("[提示] 批处理条件用于批处理文件中，输入【帮助 批处理条件】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("批处理条件 "):
                param = trim_string(command[5:])
                self.run_cmd(f"if {param}")
                self.show_prompt()
                return
            if command == "恢复目录":
                self.output_edit.appendPlainText("[提示] 恢复目录用于批处理文件中，输入【帮助 恢复目录】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("恢复目录 "):
                param = trim_string(command[4:])
                self.run_cmd(f"popd {param}")
                self.show_prompt()
                return
            if command == "保存目录":
                self.output_edit.appendPlainText("[提示] 保存目录用法：保存目录 目标路径（如：保存目录 D:\文档）")
                self.output_edit.appendPlainText("输入【帮助 保存目录】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("保存目录 "):
                param = trim_string(command[4:])
                self.run_cmd(f"pushd {param}")
                self.show_prompt()
                return
            if command == "开始本地环境":
                self.output_edit.appendPlainText("[提示] 开始本地环境用于批处理文件中，输入【帮助 开始本地环境】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("开始本地环境 "):
                param = trim_string(command[6:])
                self.run_cmd(f"setlocal {param}")
                self.show_prompt()
                return
            if command == "批处理参数调整":
                self.output_edit.appendPlainText("[提示] 批处理参数调整用于批处理文件中，输入【帮助 批处理参数调整】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("批处理参数调整 "):
                param = trim_string(command[6:])
                self.run_cmd(f"shift {param}")
                self.show_prompt()
                return
            if command == "计算":
                self.output_edit.appendPlainText("[提示] 计算用法：计算 算式（如：计算 1+2*3），或直接输入算式（如：1+2*3）")
                self.output_edit.appendPlainText("输入【帮助 计算】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("计算 "):
                expr = trim_string(command[2:])
                try:
                    result = eval(expr)
                    self.output_edit.appendPlainText(f"计算结果：{expr} = {result}")
                except Exception as e:
                    self.output_edit.appendPlainText(f"[计算错误] 算式无效：{str(e)}")
                self.show_prompt()
                return

            has_operator = any(op in command for op in ["+", "-", "*", "/", "//", "%", "**", "(", ")"])
            if has_operator:
                try:
                    result = eval(command)
                    self.output_edit.appendPlainText(f"计算结果：{command} = {result}")
                    self.show_prompt()
                    return
                except Exception as e:
                    self.output_edit.appendPlainText(f"[计算错误] 算式无效：{str(e)}")
                    self.show_prompt()
                    return
            if command == "打印":
                self.output_edit.appendPlainText("[提示] 打印用法：打印 文件名（如：打印 文档.txt），或打印 /d:打印机名 文件名")
                self.output_edit.appendPlainText("输入【帮助 打印】查看详细用法")
                self.show_prompt()
                return
            if command.startswith("打印 "):
                param = trim_string(command[2:])
                self.run_cmd(f"print {param}")
                self.show_prompt()
                return
            if command == "自定义命令":
                self.run_cmd("doskey /macros")
                self.show_prompt()
                return
            if command.startswith("自定义命令 "):
                param = trim_string(command[4:])
                if param.startswith("/d "):
                    alias = trim_string(param[3:])
                    self.run_cmd(f"doskey {alias}= ")
                elif param.startswith("/s "):
                    filename = trim_string(param[3:])
                    self.run_cmd(f"doskey /macros > {filename}")
                    self.output_edit.appendPlainText(f"别名已保存到文件「{filename}」")
                elif param.startswith("/r "):
                    filename = trim_string(param[3:])
                    self.run_cmd(f"doskey /macros:<{filename}")
                    self.output_edit.appendPlainText(f"已从文件「{filename}」加载别名")
                else:
                    self.run_cmd(f"doskey {param}")
                self.show_prompt()
                return

            if command == "退出":
                tab_widget = self.parent().parent()
                index = tab_widget.indexOf(self)
                tab_widget.removeTab(index)
                return

            self.run_cmd(command)
            self.show_prompt()
        except Exception as e:
            self.output_edit.appendPlainText(f"[错误] 执行命令失败：{str(e)}")
            self.output_edit.appendPlainText(traceback.format_exc())
            self.show_prompt()

    def run_cmd(self, command: str, wait: bool = True):
        try:
            encoding = locale.getpreferredencoding()
            if wait:
                result = subprocess.run(
                    command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    encoding=encoding, errors='replace', cwd=self.current_dir
                )
                if result.stdout:
                    self.output_edit.appendPlainText(result.stdout)
                if result.stderr:
                    self.output_edit.appendPlainText(f"错误：{result.stderr}")
                return result.returncode
            else:
                subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                cwd=self.current_dir, encoding=encoding, errors='replace')
                return 0
        except Exception as e:
            self.output_edit.appendPlainText(f"[执行失败] {str(e)}")
            return -1

    def show_global_help(self):
        help_text = """有关某个命令的详细信息，请键入 帮助 命令名
【目录操作类】
  查看目录      - 列出当前/指定目录下的文件和文件夹（对应dir）
  切换目录      - 切换当前工作目录（对应cd/chdir）
  新建目录      - 创建文件夹，支持多级目录（对应md/mkdir）
  删除目录      - 删除空/非空文件夹（对应rd/rmdir）
  目录树显示    - 以图形方式显示驱动程序或路径的目录结构（对应tree）
【文件操作类】
  复制文件      - 复制文件/批量文件到指定路径（对应copy）
  移动文件      - 移动/重命名文件（对应move）
  删除文件      - 删除文件/批量文件（对应del/erase）
  重命名文件    - 重命名文件/批量文件（对应ren/rename）
  复制目录树    - 复制文件和目录树（对应xcopy）
  高级复制      - 复制文件和目录树的高级实用工具（对应robocopy）
  替换文件      - 替换文件（对应replace）
  查看文件内容  - 显示文本文件的内容（对应type）
  恢复文件      - 从损坏的或有缺陷的磁盘中恢复可读信息（对应recover）
【文件管理类】
  文件关联      - 显示或修改文件扩展名关联（对应assoc）
  文件属性      - 显示或更改文件属性（对应attrib）
  比较文件      - 比较两个或两套文件的内容（对应comp）
  文件比较      - 比较两个文件或两个文件集并显示它们之间的不同（对应fc）
  NTFS压缩      - 显示或更改NTFS分区上文件的压缩（对应compact）
  转换分区格式  - 将FAT卷转换成NTFS（对应convert）
  查找文本      - 在一个或多个文件中搜索一个文本字符串（对应find）
  查找字符串    - 在多个文件中搜索字符串（对应findstr）
  格式化磁盘    - 格式化磁盘，以便用于Windows（对应format）
  文件系统配置  - 显示或配置文件系统属性（对应fsutil）
  文件类型关联  - 显示或修改在文件扩展名关联中使用的文件类型（对应ftype）
  磁盘卷标      - 创建、更改或删除磁盘的卷标（对应label）
  创建链接      - 创建符号链接和硬链接（对应mklink）
  打开文件查询  - 显示远程用户为了文件共享而打开的文件（对应openfiles）
  批处理注释    - 记录批处理文件或CONFIG.SYS中的注释(批注)（对应rem）
【系统配置类】
  中断检查      - 设置或清除扩展式CTRL+C检查（对应break）
  启动配置      - 设置启动数据库中的属性以控制启动加载（对应bcdedit）
  访问控制列表  - 显示或修改文件的访问控制列表(ACL)（对应cacls/icacls）
  代码页设置    - 显示或设置活动代码页数（对应chcp）
  打开命令窗口  - 打开另一个Windows命令解释程序窗口（对应cmd）
  驱动查询      - 显示当前设备驱动程序状态和属性（对应driverquery）
  设备配置      - 配置系统设备（对应mode）
  命令提示设置  - 更改Windows命令提示（对应prompt）
  服务配置      - 显示或配置服务(后台进程)（对应sc）
  任务计划      - 安排在一台计算机上运行命令和程序（对应schtasks）
  关闭计算机    - 允许通过本地或远程方式正确关闭计算机（对应shutdown）
  排序输入      - 对输入排序（对应sort）
  启动程序      - 启动单独的窗口以运行指定的程序或命令（对应start）
  时间设置      - 显示或设置系统时间（对应time）
  窗口标题设置  - 设置CMD.EXE会话的窗口标题（对应title）
  查看Windows版本 - 显示Windows的版本（对应ver）
  文件写入验证  - 告诉Windows是否进行验证，以确保文件正确写入磁盘（对应verify）
  磁盘卷标查看  - 显示磁盘卷标和序列号（对应vol）
  WMI信息查询    - 在交互式命令shell中显示WMI信息（对应wmic）
【系统高级类】
  清屏          - 清空终端输出（对应cls）
  查看进程      - 列出系统所有进程（对应tasklist）
  结束进程      - 终止指定进程（对应taskkill）
  系统信息      - 查看系统详细信息（对应systeminfo）
  查看IP        - 查看网络IP/释放/重新获取IP（对应ipconfig）
  环境变量      - 查看/修改/删除环境变量（对应set）
  查看路径      - 查看/修改系统执行路径（对应path）
  磁盘分区管理  - 显示或配置磁盘分区属性（对应diskpart）
  挂载映像      - 将文件/目录挂载为虚拟磁盘（对应subst）
  卸载映像      - 卸载指定虚拟磁盘（对应subst /d）
  查看映像      - 查看所有已挂载的虚拟磁盘（对应subst）
【常用工具类】
  打开记事本    - 启动Windows记事本（对应notepad）
  打开计算器    - 启动Windows计算器（对应calc）
  打开注册表    - 启动注册表编辑器（对应regedit）
  打开任务管理器- 启动Windows任务管理器（对应taskmgr）
  分屏显示      - 逐屏显示输出（对应more）
  暂停批处理    - 暂停批处理文件的处理并显示消息（对应pause）
【批处理类】
  调用批处理    - 从另一个批处理程序调用这一个（对应call）
  回显      - 显示消息，或将命令回显打开或关闭（对应echo）
  结束本地环境  - 结束批文件中环境更改的本地化（对应endlocal）
  批处理循环    - 为一组文件中的每个文件运行一个指定的命令（对应for）
  批处理跳转    - 将Windows命令解释程序定向到批处理程序中某个带标签的行（对应goto）
  组策略信息    - 显示计算机或用户的组策略信息（对应gpresult）
  扩展字符集    - 使Windows在图形模式下显示扩展字符集（对应graftabl）
  批处理条件    - 在批处理程序中执行有条件的处理操作（对应if）
  恢复目录      - 还原通过PUSHD保存的当前目录的上一个值（对应popd）
  保存目录      - 保存当前目录，然后对其进行更改（对应pushd）
  开始本地环境  - 开始本地化批处理文件中的环境更改（对应setlocal）
  批处理参数调整 - 调整批处理文件中可替换参数的位置（对应shift）
【计算与打印类】
  计算          - 计算数学算式并打印结果
  打印          - 打印文件（对应print）
【自定义设置类】
  自定义命令      - 设置/查看/删除/保存/加载自定义命令别名（对应doskey）
【系统映像维护类】
  系统映像管理    - 系统映像维护、修复（对应dism）
【使用说明类】
  退出          - 关闭当前终端标签页（对应exit）
【高级用法】
  1. 支持原生CMD所有功能
  2. 支持执行.bat/.cmd脚本（输入完整路径即可）
======================================================="""
        self.output_edit.appendPlainText(help_text)

    def show_single_help(self, cmd_name: str):
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
=======================================================""",
            "切换目录": """========================================================
  指令：切换目录（对应英文指令：cd/chdir）
========================================================
功能：切换当前工作目录，支持盘符切换、上级目录跳转
用法：
  1. 切换目录 ..              - 跳转到上级目录
  2. 切换目录 目标路径       - 跳转到指定路径（如：切换目录 D:\Program Files）
  3. 切换目录 /d 盘符\路径    - 跨盘符切换（如：切换目录 /d E:\数据）
  4. 直接输入 盘符:           - 切换盘符（如：D:、E:）
=======================================================""",
            "新建目录": """========================================================
  指令：新建目录（对应英文指令：md/mkdir）
========================================================
功能：创建文件夹，支持一次性创建多级目录
用法：
  1. 新建目录 文件夹名        - 创建单层目录（如：新建目录 我的文档）
  2. 新建目录 路径\文件夹名    - 指定路径创建（如：新建目录 D:\备份\2026）
  3. 新建目录 文件夹1\文件夹2  - 多级目录（如：新建目录 a\b\c）
=======================================================""",
            "删除目录": """========================================================
  指令：删除目录（对应英文指令：rd/rmdir）
========================================================
功能：删除空/非空文件夹，谨慎使用！
用法：
  1. 删除目录 文件夹名        - 删除空文件夹（如：删除目录 空文件夹）
  2. 删除目录 文件夹名 /s      - 删除非空文件夹（含子目录/文件）
  3. 删除目录 文件夹名 /s /q   - 静默删除非空文件夹（无确认提示）
=======================================================""",
            "复制文件": """========================================================
  指令：复制文件（对应英文指令：copy）
========================================================
功能：复制单个/批量文件到指定路径
用法：
  1. 复制文件 源文件 目标路径  - 复制单个文件（如：复制文件 1.txt D:\数据）
  2. 复制文件 *.txt 目标路径   - 批量复制（如：复制文件 *.txt D:\备份）
  3. 复制文件 源文件 新文件名  - 复制并重命名（如：复制文件 1.txt D:\2.txt）
=======================================================""",
            "移动文件": """========================================================
  指令：移动文件（对应英文指令：move）
========================================================
功能：移动文件/批量文件，也可用于文件重命名
用法：
  1. 移动文件 源文件 目标路径  - 移动单个文件（如：移动文件 1.txt D:\数据）
  2. 移动文件 *.txt 目标路径   - 批量移动（如：移动文件 *.txt D:\备份）
  3. 移动文件 旧文件名 新文件名 - 重命名（如：移动文件 1.txt 2.txt）
=======================================================""",
            "删除文件": """========================================================
  指令：删除文件（对应英文指令：del/erase）
========================================================
功能：删除单个/批量文件，谨慎使用！
用法：
  1. 删除文件 文件名          - 删除单个文件（如：删除文件 1.txt）
  2. 删除文件 *.txt           - 批量删除（如：删除文件 *.txt）
  3. 删除文件 /f              - 强制删除只读文件
  4. 删除文件 /s              - 递归删除所有子目录的对应文件
=======================================================""",
            "重命名文件": """========================================================
  指令：重命名文件（对应英文指令：ren/rename）
========================================================
功能：重命名单个/批量文件
用法：
  1. 重命名文件 旧文件名 新文件名  - 单个文件重命名（如：重命名文件 1.txt 2.txt）
  2. 重命名文件 *.txt *.bak        - 批量重命名（如：所有.txt改为.bak）
=======================================================""",
            "查看进程": """========================================================
  指令：查看进程（对应英文指令：tasklist）
========================================================
功能：列出系统所有进程，包含PID、内存占用等信息
用法：
  1. 查看进程                - 列出所有进程
  2. 查看进程 /fi "PID eq 1234" - 筛选指定PID的进程
  3. 查看进程 /fi "IMAGENAME eq notepad.exe" - 筛选指定名称的进程
=======================================================""",
            "结束进程": """========================================================
  指令：结束进程（对应英文指令：taskkill）
========================================================
功能：终止指定进程，谨慎使用！
用法：
  1. 结束进程 notepad.exe     - 终止所有记事本进程
  2. 结束进程 /pid 1234       - 终止指定PID的进程
  3. 结束进程 /im notepad.exe /f - 强制终止记事本进程
=======================================================""",
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
=======================================================""",
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
=======================================================""",
            "目录树显示": """========================================================
  指令：目录树显示（对应英文指令：tree）
========================================================
功能：以图形方式显示驱动程序或路径的目录结构
用法：
  1. 目录树显示                - 显示当前目录的目录树
  2. 目录树显示 目标路径       - 显示指定路径的目录树
  3. 目录树显示 /f              - 显示每个文件夹中文件的名称
  4. 目录树显示 /a              - 使用ASCII字符，而不使用扩展字符
=======================================================""",
            "复制目录树": """========================================================
  指令：复制目录树（对应英文指令：xcopy）
========================================================
功能：复制文件和目录树
用法：
  1. 复制目录树 源路径 目标路径   - 复制目录树（如：复制目录树 D:\文档 E:\备份）
  2. 复制目录树 源路径 目标路径 /s - 复制非空目录和子目录
  3. 复制目录树 源路径 目标路径 /e - 复制所有目录和子目录，包括空目录
  4. 复制目录树 源路径 目标路径 /h - 复制隐藏和系统文件
=======================================================""",
            "高级复制": """========================================================
  指令：高级复制（对应英文指令：robocopy）
========================================================
功能：复制文件和目录树的高级实用工具
用法：
  1. 高级复制 源路径 目标路径       - 复制目录树（如：高级复制 D:\文档 E:\备份）
  2. 高级复制 源路径 目标路径 /s     - 复制非空目录和子目录
  3. 高级复制 源路径 目标路径 /e     - 复制所有目录和子目录，包括空目录
  4. 高级复制 源路径 目标路径 /mir   - 镜像复制（完全匹配源目录）
=======================================================""",
            "替换文件": """========================================================
  指令：替换文件（对应英文指令：replace）
========================================================
功能：替换文件
用法：
  1. 替换文件 源文件 目标路径       - 替换目标路径中的文件
  2. 替换文件 源文件 目标路径 /a     - 添加文件而不是替换文件
  3. 替换文件 源文件 目标路径 /p     - 替换前提示确认
  4. 替换文件 源文件 目标路径 /r     - 替换只读文件
=======================================================""",
            "查看文件内容": """========================================================
  指令：查看文件内容（对应英文指令：type）
========================================================
功能：显示文本文件的内容
用法：
  1. 查看文件内容 文件名                - 显示指定文本文件的内容
  2. 查看文件内容 文件名 | more         - 分屏显示文件内容
=======================================================""",
            "恢复文件": """========================================================
  指令：恢复文件（对应英文指令：recover）
========================================================
功能：从损坏的或有缺陷的磁盘中恢复可读信息
用法：
  1. 恢复文件 文件名                - 恢复指定文件
  2. 恢复文件 盘符:\路径\文件名      - 恢复指定路径的文件
=======================================================""",
            "文件关联": """========================================================
  指令：文件关联（对应英文指令：assoc）
========================================================
功能：显示或修改文件扩展名关联
用法：
  1. 文件关联                - 显示所有文件扩展名关联
  2. 文件关联 .ext           - 显示指定扩展名的关联
  3. 文件关联 .ext=文件类型    - 设置指定扩展名的关联（如：文件关联 .txt=txtfile）
=======================================================""",
            "文件属性": """========================================================
  指令：文件属性（对应英文指令：attrib）
========================================================
功能：显示或更改文件属性
用法：
  1. 文件属性                - 显示当前目录所有文件的属性
  2. 文件属性 文件名          - 显示指定文件的属性
  3. 文件属性 +R 文件名       - 设置文件为只读属性
  4. 文件属性 -R 文件名       - 取消文件的只读属性
  5. 文件属性 +H 文件名       - 设置文件为隐藏属性
  6. 文件属性 -H 文件名       - 取消文件的隐藏属性
  7. 文件属性 +S 文件名       - 设置文件为系统属性
  8. 文件属性 -S 文件名       - 取消文件的系统属性
  9. 文件属性 +A 文件名       - 设置文件为存档属性
  10. 文件属性 -A 文件名      - 取消文件的存档属性
=======================================================""",
            "比较文件": """========================================================
  指令：比较文件（对应英文指令：comp）
========================================================
功能：比较两个或两套文件的内容
用法：
  1. 比较文件 文件1 文件2                - 比较两个文件
  2. 比较文件 文件1 文件2 /a              - 以ASCII模式比较
  3. 比较文件 文件1 文件2 /b              - 以二进制模式比较
  4. 比较文件 *.txt *.bak                 - 批量比较文件
=======================================================""",
            "文件比较": """========================================================
  指令：文件比较（对应英文指令：fc）
========================================================
功能：比较两个文件或两个文件集并显示它们之间的不同
用法：
  1. 文件比较 文件1 文件2                - 比较两个文件
  2. 文件比较 文件1 文件2 /a              - 只显示每个不同处的第一行和最后一行
  3. 文件比较 文件1 文件2 /b              - 以二进制模式比较
  4. 文件比较 *.txt *.bak                 - 批量比较文件
=======================================================""",
            "NTFS压缩": """========================================================
  指令：NTFS压缩（对应英文指令：compact）
========================================================
功能：显示或更改NTFS分区上文件的压缩
用法：
  1. NTFS压缩                - 显示当前目录所有文件的压缩状态
  2. NTFS压缩 文件名          - 显示指定文件的压缩状态
  3. NTFS压缩 /c 文件名       - 压缩指定文件
  4. NTFS压缩 /u 文件名       - 解压缩指定文件
=======================================================""",
            "转换分区格式": """========================================================
  指令：转换分区格式（对应英文指令：convert）
========================================================
功能：将FAT卷转换成NTFS，不能转换当前驱动器
用法：
  1. 转换分区格式 盘符: /fs:ntfs    - 将指定盘符转换为NTFS格式（如：转换分区格式 D: /fs:ntfs）
=======================================================""",
            "查找文本": """========================================================
  指令：查找文本（对应英文指令：find）
========================================================
功能：在一个或多个文件中搜索一个文本字符串
用法：
  1. 查找文本 "字符串" 文件名                - 在指定文件中搜索字符串
  2. 查找文本 "字符串" *.txt                 - 在批量文件中搜索字符串
  3. 查找文本 /v "字符串" 文件名              - 显示不包含指定字符串的行
  4. 查找文本 /c "字符串" 文件名              - 显示包含指定字符串的行数
=======================================================""",
            "查找字符串": """========================================================
  指令：查找字符串（对应英文指令：findstr）
========================================================
功能：在多个文件中搜索字符串
用法：
  1. 查找字符串 "字符串" 文件名                - 在指定文件中搜索字符串
  2. 查找字符串 "字符串" *.txt                 - 在批量文件中搜索字符串
  3. 查找字符串 /r "正则表达式" 文件名          - 使用正则表达式搜索
  4. 查找字符串 /i "字符串" 文件名              - 不区分大小写搜索
=======================================================""",
            "格式化磁盘": """========================================================
  指令：格式化磁盘（对应英文指令：format）
========================================================
功能：格式化磁盘，以便用于Windows，谨慎使用！
用法：
  1. 格式化磁盘 盘符:                - 格式化指定盘符（如：格式化磁盘 D:）
  2. 格式化磁盘 盘符: /fs:ntfs       - 格式化指定盘符为NTFS格式
  3. 格式化磁盘 盘符: /q              - 快速格式化
=======================================================""",
            "文件系统配置": """========================================================
  指令：文件系统配置（对应英文指令：fsutil）
========================================================
功能：显示或配置文件系统属性
用法：
  1. 文件系统配置 fsinfo drives                - 显示所有驱动器
  2. 文件系统配置 fsinfo ntfsinfo 盘符:        - 显示指定盘符的NTFS信息
  3. 文件系统配置 file createnew 文件名 大小    - 创建指定大小的文件
=======================================================""",
            "文件类型关联": """========================================================
  指令：文件类型关联（对应英文指令：ftype）
========================================================
功能：显示或修改在文件扩展名关联中使用的文件类型
用法：
  1. 文件类型关联                - 显示所有文件类型关联
  2. 文件类型关联 文件类型        - 显示指定文件类型的关联
  3. 文件类型关联 文件类型=命令    - 设置指定文件类型的关联命令
=======================================================""",
            "磁盘卷标": """========================================================
  指令：磁盘卷标（对应英文指令：label）
========================================================
功能：创建、更改或删除磁盘的卷标
用法：
  1. 磁盘卷标 盘符:                - 显示指定盘符的卷标
  2. 磁盘卷标 盘符: 卷标名          - 设置指定盘符的卷标
  3. 磁盘卷标 盘符: /d              - 删除指定盘符的卷标
=======================================================""",
            "创建链接": """========================================================
  指令：创建链接（对应英文指令：mklink）
========================================================
功能：创建符号链接和硬链接
用法：
  1. 创建链接 链接名 目标路径                - 创建符号链接
  2. 创建链接 /d 链接名 目标路径              - 创建目录符号链接
  3. 创建链接 /h 链接名 目标路径              - 创建硬链接
=======================================================""",
            "打开文件查询": """========================================================
  指令：打开文件查询（对应英文指令：openfiles）
========================================================
功能：显示远程用户为了文件共享而打开的文件
用法：
  1. 打开文件查询 /query                - 显示所有打开的文件
  2. 打开文件查询 /disconnect /id 会话ID    - 断开指定会话的打开文件
=======================================================""",
            "批处理注释": """========================================================
  指令：批处理注释（对应英文指令：rem）
========================================================
功能：记录批处理文件或CONFIG.SYS中的注释(批注)
用法：
  1. 在批处理文件中使用 rem 注释内容        - 添加注释
=======================================================""",
            "中断检查": """========================================================
  指令：中断检查（对应英文指令：break）
========================================================
功能：设置或清除扩展式CTRL+C检查
用法：
  1. 中断检查                - 显示当前中断检查设置
  2. 中断检查 on              - 启用扩展式CTRL+C检查
  3. 中断检查 off             - 禁用扩展式CTRL+C检查
=======================================================""",
            "启动配置": """========================================================
  指令：启动配置（对应英文指令：bcdedit）
========================================================
功能：设置启动数据库中的属性以控制启动加载，需管理员权限运行
用法：
  1. 启动配置                - 显示启动配置信息
  2. 启动配置 /set {default} bootmenupolicy legacy - 设置传统启动菜单
=======================================================""",
            "访问控制列表": """========================================================
  指令：访问控制列表（对应英文指令：cacls/icacls）
========================================================
功能：显示或修改文件的访问控制列表(ACL)
用法：
  1. 访问控制列表 文件名                - 显示指定文件的ACL
  2. 访问控制列表 文件名 /g 用户名:权限    - 授予用户指定权限
  3. 访问控制列表 文件名 /r 用户名        - 撤销用户的权限
=======================================================""",
            "代码页设置": """========================================================
  指令：代码页设置（对应英文指令：chcp）
========================================================
功能：显示或设置活动代码页数
用法：
  1. 代码页设置                - 显示当前活动代码页
  2. 代码页设置 代码页号          - 设置活动代码页（如：代码页设置 936）
=======================================================""",
            "打开命令窗口": """========================================================
  指令：打开命令窗口（对应英文指令：cmd）
========================================================
功能：打开另一个Windows命令解释程序窗口
用法：
  1. 打开命令窗口                - 打开新的命令窗口
  2. 打开命令窗口 /k 命令          - 打开新窗口并执行指定命令
  3. 打开命令窗口 /c 命令          - 打开新窗口执行指定命令后关闭
=======================================================""",
            "驱动查询": """========================================================
  指令：驱动查询（对应英文指令：driverquery）
========================================================
功能：显示当前设备驱动程序状态和属性
用法：
  1. 驱动查询                - 显示所有驱动程序
  2. 驱动查询 /v              - 显示详细驱动信息
  3. 驱动查询 /si             - 显示已签名的驱动程序
=======================================================""",
            "设备配置": """========================================================
  指令：设备配置（对应英文指令：mode）
========================================================
功能：配置系统设备
用法：
  1. 设备配置 con: cols=80 lines=25    - 设置控制台窗口大小
  2. 设备配置 串口: baud=9600          - 配置串口参数
  3. 设备配置 /status                - 显示所有设备状态
=======================================================""",
            "命令提示设置": """========================================================
  指令：命令提示设置（对应英文指令：prompt）
========================================================
功能：更改Windows命令提示
用法：
  1. 命令提示设置                - 显示当前命令提示
  2. 命令提示设置 $p$g          - 设置命令提示为当前目录>
  3. 命令提示设置 $t            - 设置命令提示为当前时间
=======================================================""",
            "服务配置": """========================================================
  指令：服务配置（对应英文指令：sc）
========================================================
功能：显示或配置服务(后台进程)，需管理员权限运行
用法：
  1. 服务配置 query                - 显示所有服务
  2. 服务配置 query 服务名          - 显示指定服务的状态
  3. 服务配置 start 服务名          - 启动指定服务
  4. 服务配置 stop 服务名           - 停止指定服务
=======================================================""",
            "任务计划": """========================================================
  指令：任务计划（对应英文指令：schtasks）
========================================================
功能：安排在一台计算机上运行命令和程序
用法：
  1. 任务计划 /query                - 显示所有任务计划
  2. 任务计划 /create /tn 任务名 /tr 命令 /sc daily - 创建每日执行的任务
  3. 任务计划 /run /tn 任务名          - 运行指定任务
  4. 任务计划 /delete /tn 任务名       - 删除指定任务
=======================================================""",
            "关闭计算机": """========================================================
  指令：关闭计算机（对应英文指令：shutdown）
========================================================
功能：允许通过本地或远程方式正确关闭计算机
用法：
  1. 关闭计算机 /s                - 关闭本地计算机
  2. 关闭计算机 /r                - 重启本地计算机
  3. 关闭计算机 /l                - 注销当前用户
  4. 关闭计算机 /m \\计算机名 /s    - 关闭远程计算机
=======================================================""",
            "排序输入": """========================================================
  指令：排序输入（对应英文指令：sort）
========================================================
功能：对输入排序
用法：
  1. sort < 文件名                - 对文件内容排序并显示
  2. sort /r < 文件名              - 对文件内容反向排序
  3. sort /+n < 文件名             - 从第n列开始排序
=======================================================""",
            "启动程序": """========================================================
  指令：启动程序（对应英文指令：start）
========================================================
功能：启动单独的窗口以运行指定的程序或命令
用法：
  1. 启动程序 程序名                - 启动指定程序
  2. 启动程序 程序名 文件名          - 用指定程序打开文件
  3. 启动程序 /max 程序名            - 最大化窗口启动程序
  4. 启动程序 /min 程序名            - 最小化窗口启动程序
=======================================================""",
            "时间设置": """========================================================
  指令：时间设置（对应英文指令：time）
========================================================
功能：显示或设置系统时间
用法：
  1. 时间设置                - 显示当前系统时间并提示设置新时间
  2. 时间设置 时:分:秒          - 设置系统时间（如：时间设置 12:30:00）
=======================================================""",
            "窗口标题设置": """========================================================
  指令：窗口标题设置（对应英文指令：title）
========================================================
功能：设置CMD.EXE会话的窗口标题
用法：
  1. 窗口标题设置 标题名                - 设置窗口标题为指定名称
=======================================================""",
            "查看Windows版本": """========================================================
  指令：查看Windows版本（对应英文指令：ver）
========================================================
功能：显示Windows的版本
用法：
  1. 查看Windows版本                - 显示当前Windows版本
=======================================================""",
            "文件写入验证": """========================================================
  指令：文件写入验证（对应英文指令：verify）
========================================================
功能：告诉Windows是否进行验证，以确保文件正确写入磁盘
用法：
  1. 文件写入验证                - 显示当前验证设置
  2. 文件写入验证 on              - 启用文件写入验证
  3. 文件写入验证 off             - 禁用文件写入验证
=======================================================""",
            "磁盘卷标查看": """========================================================
  指令：磁盘卷标查看（对应英文指令：vol）
========================================================
功能：显示磁盘卷标和序列号
用法：
  1. 磁盘卷标查看                - 显示当前驱动器的卷标和序列号
  2. 磁盘卷标查看 盘符:          - 显示指定驱动器的卷标和序列号
=======================================================""",
            "WMI信息查询": """========================================================
  指令：WMI信息查询（对应英文指令：wmic）
========================================================
功能：在交互式命令shell中显示WMI信息
用法：
  1. WMI信息查询                - 启动WMI交互式shell
  2. WMI信息查询 cpu get name    - 显示CPU名称
  3. WMI信息查询 diskdrive get size - 显示磁盘大小
=======================================================""",
            "磁盘分区管理": """========================================================
  指令：磁盘分区管理（对应英文指令：diskpart）
========================================================
功能：显示或配置磁盘分区属性，需管理员权限运行
用法：
  1. 磁盘分区管理                - 启动磁盘分区管理工具
=======================================================""",
            "分屏显示": """========================================================
  指令：分屏显示（对应英文指令：more）
========================================================
功能：逐屏显示输出
用法：
  1. more < 文件名                - 分屏显示文件内容
  2. 命令 | more                  - 分屏显示命令输出
=======================================================""",
            "暂停批处理": """========================================================
  指令：暂停批处理（对应英文指令：pause）
========================================================
功能：暂停批处理文件的处理并显示消息
用法：
  1. 在批处理文件中使用 pause        - 暂停批处理并显示"请按任意键继续..."
=======================================================""",
            "调用批处理": """========================================================
  指令：调用批处理（对应英文指令：call）
========================================================
功能：从另一个批处理程序调用这一个
用法：
  1. 调用批处理 批处理文件名                - 调用指定批处理文件
=======================================================""",
            "回显": """========================================================
  指令：回显（对应英文指令：echo）
========================================================
功能：显示消息，或将命令回显打开或关闭
用法：
  1. 回显 消息内容                - 显示指定消息
  2. 回显 on                      - 启用命令回显
  3. 回显 off                     - 禁用命令回显
=======================================================""",
            "结束本地环境": """========================================================
  指令：结束本地环境（对应英文指令：endlocal）
========================================================
功能：结束批文件中环境更改的本地化
用法：
  1. 在批处理文件中使用 endlocal        - 结束本地环境设置
=======================================================""",
            "批处理循环": """========================================================
  指令：批处理循环（对应英文指令：for）
========================================================
功能：为一组文件中的每个文件运行一个指定的命令
用法：
  1. for %i in (*.txt) do 命令 %i                - 对每个txt文件执行指定命令
=======================================================""",
            "批处理跳转": """========================================================
  指令：批处理跳转（对应英文指令：goto）
========================================================
功能：将Windows命令解释程序定向到批处理程序中某个带标签的行
用法：
  1. 在批处理文件中使用 goto 标签名        - 跳转到指定标签
=======================================================""",
            "组策略信息": """========================================================
  指令：组策略信息（对应英文指令：gpresult）
========================================================
功能：显示计算机或用户的组策略信息
用法：
  1. gpresult /r                - 显示组策略结果集
  2. gpresult /v                - 显示详细组策略信息
=======================================================""",
            "扩展字符集": """========================================================
  指令：扩展字符集（对应英文指令：graftabl）
========================================================
功能：使Windows在图形模式下显示扩展字符集
用法：
  1. graftabl 代码页号                - 加载指定代码页的扩展字符集
=======================================================""",
            "批处理条件": """========================================================
  指令：批处理条件（对应英文指令：if）
========================================================
功能：在批处理程序中执行有条件的处理操作
用法：
  1. if exist 文件名 命令                - 如果文件存在则执行命令
  2. if %errorlevel% == 0 命令          - 如果错误级别为0则执行命令
=======================================================""",
            "恢复目录": """========================================================
  指令：恢复目录（对应英文指令：popd）
========================================================
功能：还原通过PUSHD保存的当前目录的上一个值
用法：
  1. 在批处理文件中使用 popd        - 恢复之前保存的目录
=======================================================""",
            "保存目录": """========================================================
  指令：保存目录（对应英文指令：pushd）
========================================================
功能：保存当前目录，然后对其进行更改
用法：
  1. pushd 目标路径                - 保存当前目录并切换到目标路径
=======================================================""",
            "开始本地环境": """========================================================
  指令：开始本地环境（对应英文指令：setlocal）
========================================================
功能：开始本地化批处理文件中的环境更改
用法：
  1. 在批处理文件中使用 setlocal        - 开始本地环境设置
=======================================================""",
            "批处理参数调整": """========================================================
  指令：批处理参数调整（对应英文指令：shift）
========================================================
功能：调整批处理文件中可替换参数的位置
用法：
  1. 在批处理文件中使用 shift        - 调整参数位置
======================================================="""
        }
        help_text = help_mapping.get(cmd_name, f"""========================================================
[错误] 未找到「{cmd_name}」的帮助信息，请输入【帮助】查看有效指令列表
=======================================================""")
        self.output_edit.appendPlainText(help_text)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowTitle("CMD-Zh")
        self.setGeometry(100, 100, 1366, 768)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000000;
            }
            QWidget {
                background-color: #000000;
            }
        """)
        self.drag_position = None
        self.min_btn = QPushButton("—")
        self.max_btn = QPushButton("□")
        self.close_btn = QPushButton("×")
        self.min_btn.setFixedSize(30, 20)
        self.max_btn.setFixedSize(30, 20)
        self.close_btn.setFixedSize(30, 20)
        self.min_btn.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                color: #ffffff;
                border: none;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #444444;
            }
        """)
        self.max_btn.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                color: #ffffff;
                border: none;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #444444;
            }
        """)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #e81123;
                color: #ffffff;
                border: none;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #f1707a;
            }
        """)

        self.min_btn.clicked.connect(self.showMinimized)
        self.max_btn.clicked.connect(self.toggle_maximize)
        self.close_btn.clicked.connect(self.close)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.min_btn)
        btn_layout.addWidget(self.max_btn)
        btn_layout.addWidget(self.close_btn)
        btn_layout.setAlignment(Qt.AlignTop | Qt.AlignRight)

        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #333333;
                background-color: #000000;
            }
            QTabBar::tab {
                background-color: #333333;
                color: #ffffff;
                padding: 5px 10px;
                margin-right: 2px;
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
            }
            QTabBar::tab:selected {
                background-color: #000000;
                color: #ffffff;
                border: 1px solid #333333;
                border-bottom: none;
            }
            QTabBar::tab:hover {
                background-color: #444444;
            }
        """)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.tab_widget.removeTab)
        self.add_tab_btn = QPushButton("+")
        self.add_tab_btn.setFixedSize(20, 20)
        self.add_tab_btn.clicked.connect(self.add_new_tab)
        self.tab_widget.setCornerWidget(self.add_tab_btn, Qt.TopRightCorner)
        main_layout = QVBoxLayout()
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(self.tab_widget)
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        self.shortcut = QShortcut(Qt.Key_F11, self)
        self.shortcut.activated.connect(self.toggle_maximize)

        self.add_new_tab()

    def add_new_tab(self):
        terminal_tab = TerminalTab()
        tab_index = self.tab_widget.addTab(terminal_tab, f"CMD-Zh 标签{self.tab_widget.count() + 1}")
        self.tab_widget.setCurrentIndex(tab_index)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_position = None
        event.accept()

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
        self.max_btn.setText("🗗" if self.isMaximized() else "□")

    def show_context_menu(self, pos):
        menu = QMenu(self)
        if self.isMaximized():
            menu.addAction("恢复窗口", self.showNormal)
        else:
            menu.addAction("最大化", self.showMaximized)
        menu.addAction("关闭", self.close)
        menu.exec_(self.mapToGlobal(pos))



    def resizeEvent(self, event):
        self.max_btn.setText("🗗" if self.isMaximized() else "□")
        super().resizeEvent(event)

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()