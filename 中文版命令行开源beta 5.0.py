import sys
import os
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPlainTextEdit, QLineEdit, QPushButton, QTabWidget, QMenu,
                             QMessageBox, QFileDialog, QProgressDialog, QDialog, QFontDialog,
                             QColorDialog, QLabel, QSpinBox, QDialogButtonBox)
from PyQt6.QtGui import QShortcut, QTextCursor, QFont, QColor
from PyQt6.QtCore import Qt, QUrl, QPoint
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEnginePage
from decimal import Decimal, getcontext
def trim_string(s):
    return s.strip()
class SettingsDialog(QDialog):
    def __init__(self, parent=None, current_font=None, current_bg_color=None, current_font_size=12):
        super().__init__(parent)
        self.setWindowTitle("外观设置")
        self.setModal(True)
        self.setFixedSize(420, 220)
        self.selected_font = current_font or QFont("Consolas", 12)
        self.selected_bg_color = current_bg_color or "#2d2d2d"
        self.selected_font_size = current_font_size
        self.init_ui()
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        font_layout = QHBoxLayout()
        font_label = QLabel("字体：", self)
        font_label.setFixedWidth(60)
        self.font_display = QLabel(f"{self.selected_font.family()} ({self.selected_font_size}pt)", self)
        font_btn = QPushButton("选择字体", self)
        font_btn.clicked.connect(self.choose_font)
        font_layout.addWidget(font_label)
        font_layout.addWidget(self.font_display)
        font_layout.addWidget(font_btn)
        layout.addLayout(font_layout)
        bg_layout = QHBoxLayout()
        bg_label = QLabel("背景色：", self)
        bg_label.setFixedWidth(60)
        self.bg_preview = QLabel(self)
        self.bg_preview.setFixedSize(30, 30)
        self.bg_preview.setStyleSheet(f"background-color: {self.selected_bg_color}; border: 1px solid #ccc;")
        bg_btn = QPushButton("选择颜色", self)
        bg_btn.clicked.connect(self.choose_bg_color)
        bg_layout.addWidget(bg_label)
        bg_layout.addWidget(self.bg_preview)
        bg_layout.addWidget(bg_btn)
        layout.addLayout(bg_layout)
        size_layout = QHBoxLayout()
        size_label = QLabel("字体大小：", self)
        size_label.setFixedWidth(60)
        self.size_spin = QSpinBox(self)
        self.size_spin.setRange(8, 36)
        self.size_spin.setValue(self.selected_font_size)
        self.size_spin.valueChanged.connect(self.update_font_size)
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.size_spin)
        layout.addLayout(size_layout)
        btn_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self
        )
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
    def choose_font(self):
        font, ok = QFontDialog.getFont(self.selected_font, self, "选择字体")
        if ok:
            self.selected_font = font
            self.size_spin.setValue(font.pointSize())
            self.font_display.setText(f"{font.family()} ({font.pointSize()}pt)")
    def choose_bg_color(self):
        color = QColorDialog.getColor(
            QColor(self.selected_bg_color),
            self,
            "选择背景颜色"
        )
        if color.isValid():
            self.selected_bg_color = color.name()
            self.bg_preview.setStyleSheet(f"background-color: {self.selected_bg_color}; border: 1px solid #ccc;")
    def update_font_size(self, size):
        self.selected_font_size = size
        self.selected_font.setPointSize(size)
        self.font_display.setText(f"{self.selected_font.family()} ({size}pt)")
    def get_settings(self):
        return {
            "font": self.selected_font,
            "bg_color": self.selected_bg_color,
            "font_size": self.selected_font_size
        }
class TerminalPlainTextEdit(QPlainTextEdit):
    def __init__(self, parent_tab):
        super().__init__()
        self.parent_tab = parent_tab
    def keyPressEvent(self, event):
        if event.key() in [Qt.Key.Key_Return, Qt.Key.Key_Enter]:
            self.parent_tab.process_command()
            event.ignore()
        else:
            super().keyPressEvent(event)
class TerminalTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bg_color = "#2d2d2d"
        self.font_size = 12
        self.current_font = QFont("Consolas", self.font_size)
        self.current_dir = os.getcwd()
        self.prompt = f"{self.current_dir}>"
        self.init_ui()
        self.show_welcome()
        self.show_prompt()
    def calculate_pi(self, decimal_places):
        try:
            def factorial(n):
                if n == 0:
                    return 1
                result = 1
                for i in range(1, n + 1):
                    result *= i
                return result
            getcontext().prec = decimal_places + 2
            pi = Decimal(0)
            k = 0
            max_iter = decimal_places // 10 + 2
            while k < max_iter:
                numerator = Decimal((-1)**k) * Decimal(factorial(6*k)) * Decimal(13591409 + 545140134*k)
                denominator = Decimal(factorial(3*k)) * Decimal(factorial(k)**3) * Decimal(640320**(3*k))
                pi += numerator / denominator
                k += 1
            pi = pi * Decimal(10005).sqrt() / Decimal(4270934400)
            pi = pi**(-1)
            return f"{pi:.{decimal_places}f}"
        except Exception as e:
            return f"计算失败{str(e)}"
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.terminal_edit = TerminalPlainTextEdit(self)
        self.update_terminal_style()
        self.terminal_edit.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        layout.addWidget(self.terminal_edit)
        self.setLayout(layout)
        self.shortcut_clear = QShortcut("Ctrl+L", self)
        self.shortcut_clear.activated.connect(self.clear_screen)
        self.shortcut_quit = QShortcut("Ctrl+Q", self)
        self.shortcut_quit.activated.connect(self.close)
        self.shortcut_settings = QShortcut("Ctrl+T", self)
        self.shortcut_settings.activated.connect(self.open_settings)
        self.terminal_edit.textChanged.connect(self.handle_text_change)
        self.last_cursor_position = 0
    def update_terminal_style(self):
        style = f"""
            QPlainTextEdit {{
                background-color: {self.bg_color};
                color: #ffffff;
                selection-background-color: #0047ab;
                border: none;
                padding: 5px;
                font-family: "{self.current_font.family()}";
                font-size: {self.font_size}px;
                font-weight: {"bold" if self.current_font.bold() else "normal"};
                font-italic: {"italic" if self.current_font.italic() else "normal"};
            }}
        """
        self.terminal_edit.setStyleSheet(style)
    def open_settings(self):
        dialog = SettingsDialog(
            self,
            current_font=self.current_font,
            current_bg_color=self.bg_color,
            current_font_size=self.font_size
        )
        if dialog.exec():

            settings = dialog.get_settings()
            self.current_font = settings["font"]
            self.bg_color = settings["bg_color"]
            self.font_size = settings["font_size"]

            self.update_terminal_style()
    def show_welcome(self):
        welcome_text = """中文版命令行开源版 [版本beta 5.0.26311.2115]
(c) LemonXC。保留所有权利。输入[帮助]查看完整指令列表。
"""
        self.terminal_edit.appendPlainText(welcome_text)
    def show_prompt(self):
        self.current_dir = os.getcwd()
        self.prompt = f"{self.current_dir}>"
        self.terminal_edit.appendPlainText(self.prompt)

        cursor = self.terminal_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.terminal_edit.setTextCursor(cursor)
        self.last_cursor_position = len(self.terminal_edit.toPlainText())
    def clear_screen(self):
        self.terminal_edit.clear()
        self.show_welcome()
        self.show_prompt()
    def handle_text_change(self):
        current_text = self.terminal_edit.toPlainText()
        current_length = len(current_text)

        if current_length < len(self.prompt) and not current_text.endswith(self.prompt):

            self.terminal_edit.blockSignals(True)
            self.terminal_edit.setPlainText(current_text[:self.last_cursor_position])
            cursor = self.terminal_edit.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.terminal_edit.setTextCursor(cursor)
            self.terminal_edit.blockSignals(False)
            return
        self.last_cursor_position = current_length
    def get_command_from_input(self):
        text = self.terminal_edit.toPlainText()

        prompt_pos = text.rfind(self.prompt)
        if prompt_pos != -1:
            command = text[prompt_pos + len(self.prompt):].strip()
            return command
        return ""
    def run_cmd(self, cmd):
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=self.current_dir)
            if result.stdout:
                self.terminal_edit.appendPlainText(result.stdout)
            if result.stderr:
                self.terminal_edit.appendPlainText(f"{result.stderr}")
        except Exception as e:
            self.terminal_edit.appendPlainText(f"{str(e)}")
    def process_command(self):
        command = self.get_command_from_input()
        if not command:
            self.terminal_edit.appendPlainText("")
            self.show_prompt()
            return

        self.terminal_edit.appendPlainText("")

        try:
            if command == "设置" or command == "外观设置" or command == "字体设置":
                self.open_settings()
                self.show_prompt()
                return

            if command == "清屏" or command == "cls":
                self.clear_screen()
                return

            elif command == "退出" or command == "exit":
                self.close()
                return

            elif command == "帮助" or command == "/?":
                self.show_global_help()
                self.show_prompt()
                return
            elif command.startswith("帮助 "):
                help_topic = command[3:].strip()
                self.show_single_help(help_topic)
                self.show_prompt()
                return

            elif command.startswith("设置背景颜色 "):
                self.set_background_color(command[7:].strip())
                self.show_prompt()
                return

            elif command == "打开浏览器":
                main_window = self.window()
                main_window.add_browser_tab()
                self.show_prompt()
                return

            elif self.is_url(command):
                main_window = self.window()
                browser_tab = BrowserTab()
                tab_index = main_window.tab_widget.addTab(browser_tab, "新标签页")
                main_window.tab_widget.setCurrentIndex(tab_index)
                if not command.startswith("http://") and not command.startswith("https://"):
                    command = "https://" + command
                browser_tab.url_bar.setText(command)
                browser_tab.navigate_to_url()
                self.show_prompt()
                return

            elif command.startswith("计算 "):
                expression = command[3:].strip()
                self.calculate_expression(expression)
                self.show_prompt()
                return
            elif self.is_expression(command):
                self.calculate_expression(command)
                self.show_prompt()
                return

            elif command == "鸣谢名单":
                from PyQt6.QtWidgets import QMessageBox
                msg_box = QMessageBox()
                msg_box.setWindowTitle("鸣谢名单")
                msg_box.setText("作者：LemonXC\n建议反馈与测试者：BrSucfkevin")
                msg_box.exec()
                self.show_prompt()
                return

            elif command == "派运算":
                self.terminal_edit.appendPlainText("派运算用法：派运算 位数（如：派运算 10 表示计算π到小数点后10位）")
                self.terminal_edit.appendPlainText("输入【帮助 派运算】查看详细用法")
                self.show_prompt()
                return
            elif command.startswith("派运算 "):
                param = trim_string(command[4:])
                try:

                    decimal_places = int(param)
                    if decimal_places < 0:
                        self.terminal_edit.appendPlainText("位数不能为负数！")
                    elif decimal_places > 1000:
                        self.terminal_edit.appendPlainText("位数过大可能导致计算缓慢!")
                        pi_result = self.calculate_pi(decimal_places)
                        self.terminal_edit.appendPlainText(f"π={pi_result}")
                    else:
                        pi_result = self.calculate_pi(decimal_places)
                        self.terminal_edit.appendPlainText(f"π={pi_result}")
                except ValueError:
                    self.terminal_edit.appendPlainText("请输入有效的数字（正整数）作为位数！")
                except Exception as e:
                    self.terminal_edit.appendPlainText(f"{str(e)}")
                self.show_prompt()
                return

            elif command == "查看目录":
                if os.name == "nt":
                    self.run_cmd("dir")
                else:
                    self.run_cmd("ls -l")
                self.show_prompt()
                return
            elif command.startswith("查看目录 "):
                param = trim_string(command[4:])
                if os.name == "nt":
                    self.run_cmd(f"dir {param}")
                else:
                    self.run_cmd(f"ls -l {param}")
                self.show_prompt()
                return
            elif command == "切换目录":
                self.terminal_edit.appendPlainText("[提示] 切换目录用法：切换目录 目标路径（如：切换目录 D:\\文档 或 切换目录 ..）")
                self.terminal_edit.appendPlainText("输入【帮助 切换目录】查看详细用法")
                self.show_prompt()
                return
            elif command.startswith("切换目录 "):
                param = trim_string(command[4:])
                try:
                    if param.startswith("/d"):
                        os.chdir(trim_string(param[2:]))
                    else:
                        os.chdir(param)
                    self.current_dir = os.getcwd()
                    self.terminal_edit.appendPlainText(f"当前目录已切换为：{self.current_dir}")
                except Exception as e:
                    self.terminal_edit.appendPlainText(f"[错误] 切换目录失败：{str(e)}")
                self.show_prompt()
                return
            elif command == "新建目录":
                self.terminal_edit.appendPlainText("[提示] 新建目录用法：新建目录 目录名（如：新建目录 我的文件夹）")
                self.terminal_edit.appendPlainText("输入【帮助 新建目录】查看详细用法")
                self.show_prompt()
                return
            elif command.startswith("新建目录 "):
                param = trim_string(command[4:])
                try:
                    os.makedirs(param, exist_ok=True)
                    self.terminal_edit.appendPlainText(f"目录已创建：{param}")
                except Exception as e:
                    self.terminal_edit.appendPlainText(f"[错误] 创建目录失败：{str(e)}")
                self.show_prompt()
                return
            elif command == "删除目录":
                self.terminal_edit.appendPlainText("[提示] 删除目录用法：删除目录 目录名（如：删除目录 空文件夹）")
                self.terminal_edit.appendPlainText("输入【帮助 删除目录】查看详细用法")
                self.show_prompt()
                return
            elif command.startswith("删除目录 "):
                param = trim_string(command[4:])
                try:
                    import shutil
                    shutil.rmtree(param)
                    self.terminal_edit.appendPlainText(f"目录已删除：{param}")
                except Exception as e:
                    self.terminal_edit.appendPlainText(f"[错误] 删除目录失败：{str(e)}")
                self.show_prompt()
                return
            elif command == "复制文件":
                self.terminal_edit.appendPlainText("[提示] 复制文件用法：复制文件 源文件 目标路径（如：复制文件 1.txt D:\\数据）")
                self.terminal_edit.appendPlainText("输入【帮助 复制文件】查看详细用法")
                self.show_prompt()
                return
            elif command.startswith("复制文件 "):
                param = trim_string(command[4:])
                try:
                    import shutil
                    parts = param.split()
                    if len(parts) >= 2:
                        src = parts[0]
                        dst = " ".join(parts[1:])
                        shutil.copy(src, dst)
                        self.terminal_edit.appendPlainText(f"文件已复制：{src} -> {dst}")
                    else:
                        self.terminal_edit.appendPlainText("[提示] 复制文件用法：复制文件 源文件 目标路径（如：复制文件 1.txt 我的文件夹）")
                except Exception as e:
                    self.terminal_edit.appendPlainText(f"[错误] 复制文件失败：{str(e)}")
                self.show_prompt()
                return
            elif command == "移动文件":
                self.terminal_edit.appendPlainText("[提示] 移动文件用法：移动文件 源文件 目标路径（如：移动文件 1.txt D:\\数据）")
                self.terminal_edit.appendPlainText("输入【帮助 移动文件】查看详细用法")
                self.show_prompt()
                return
            elif command.startswith("移动文件 "):
                param = trim_string(command[4:])
                try:
                    import shutil
                    parts = param.split()
                    if len(parts) >= 2:
                        src = parts[0]
                        dst = " ".join(parts[1:])
                        shutil.move(src, dst)
                        self.terminal_edit.appendPlainText(f"文件已移动：{src} -> {dst}")
                    else:
                        self.terminal_edit.appendPlainText("[提示] 移动文件用法：移动文件 源文件 目标路径（如：移动文件 1.txt 我的文件夹）")
                except Exception as e:
                    self.terminal_edit.appendPlainText(f"[错误] 移动文件失败：{str(e)}")
                self.show_prompt()
                return
            elif command == "删除文件":
                self.terminal_edit.appendPlainText("[提示] 删除文件用法：删除文件 文件名（如：删除文件 1.txt）")
                self.terminal_edit.appendPlainText("输入【帮助 删除文件】查看详细用法")
                self.show_prompt()
                return
            elif command.startswith("删除文件 "):
                param = trim_string(command[4:])
                try:
                    os.remove(param)
                    self.terminal_edit.appendPlainText(f"文件已删除：{param}")
                except Exception as e:
                    self.terminal_edit.appendPlainText(f"[错误] 删除文件失败：{str(e)}")
                self.show_prompt()
                return
            elif command == "重命名文件":
                self.terminal_edit.appendPlainText("[提示] 重命名文件用法：重命名文件 旧文件名 新文件名（如：重命名文件 1.txt 2.txt）")
                self.terminal_edit.appendPlainText("输入【帮助 重命名文件】查看详细用法")
                self.show_prompt()
                return
            elif command.startswith("重命名文件 "):
                param = trim_string(command[5:])
                try:
                    parts = param.split()
                    if len(parts) >= 2:
                        old_name = parts[0]
                        new_name = " ".join(parts[1:])
                        os.rename(old_name, new_name)
                        self.terminal_edit.appendPlainText(f"文件已重命名：{old_name} -> {new_name}")
                    else:
                        self.terminal_edit.appendPlainText("[提示] 重命名文件用法：重命名文件 旧文件名 新文件名（如：重命名文件 1.txt 2.txt）")
                except Exception as e:
                    self.terminal_edit.appendPlainText(f"[错误] 重命名文件失败：{str(e)}")
                self.show_prompt()
                return
            elif command == "复制目录树":
                self.terminal_edit.appendPlainText("[提示] 复制目录树用法：复制目录树 源路径 目标路径（如：复制目录树 D:\\文档 E:\\备份）")
                self.terminal_edit.appendPlainText("输入【帮助 复制目录树】查看详细用法")
                self.show_prompt()
                return
            elif command.startswith("复制目录树 "):
                param = trim_string(command[5:])
                self.run_cmd(f"xcopy {param}")
                self.show_prompt()
                return
            elif command == "高级复制":
                self.terminal_edit.appendPlainText("[提示] 高级复制用法：高级复制 源路径 目标路径（如：高级复制 D:\\文档 E:\\备份）")
                self.terminal_edit.appendPlainText("输入【帮助 高级复制】查看详细用法")
                self.show_prompt()
                return
            elif command.startswith("高级复制 "):
                param = trim_string(command[4:])
                self.run_cmd(f"robocopy {param}")
                self.show_prompt()
                return
            elif command == "替换文件":
                self.terminal_edit.appendPlainText("[提示] 替换文件用法：替换文件 源文件 目标路径（如：替换文件 1.txt D:\\数据）")
                self.terminal_edit.appendPlainText("输入【帮助 替换文件】查看详细用法")
                self.show_prompt()
                return
            elif command.startswith("替换文件 "):
                param = trim_string(command[4:])
                self.run_cmd(f"replace {param}")
                self.show_prompt()
                return
            elif command == "查看文件内容":
                self.terminal_edit.appendPlainText("[提示] 查看文件内容用法：查看文件内容 文件名（如：查看文件内容 文档.txt）")
                self.terminal_edit.appendPlainText("输入【帮助 查看文件内容】查看详细用法")
                self.show_prompt()
                return
            elif command.startswith("查看文件内容 "):
                param = trim_string(command[6:])
                self.run_cmd(f"type {param}")
                self.show_prompt()
                return
            elif command == "恢复文件":
                self.terminal_edit.appendPlainText("[提示] 恢复文件用法：恢复文件 文件名（如：恢复文件 损坏.txt）")
                self.terminal_edit.appendPlainText("输入【帮助 恢复文件】查看详细用法")
                self.show_prompt()
                return
            elif command.startswith("恢复文件 "):
                param = trim_string(command[4:])
                self.run_cmd(f"recover {param}")
                self.show_prompt()
                return
            elif command == "文件关联":
                self.run_cmd("assoc")
                self.show_prompt()
                return
            elif command.startswith("文件关联 "):
                param = trim_string(command[4:])
                self.run_cmd(f"assoc {param}")
                self.show_prompt()
                return
            elif command == "文件属性":
                self.terminal_edit.appendPlainText("[提示] 文件属性用法：文件属性 文件名（如：文件属性 1.txt）")
                self.terminal_edit.appendPlainText("输入【帮助 文件属性】查看详细用法")
                self.show_prompt()
                return
            elif command.startswith("文件属性 "):
                param = trim_string(command[4:])
                self.run_cmd(f"attrib {param}")
                self.show_prompt()
                return
            elif command == "比较文件":
                self.terminal_edit.appendPlainText("[提示] 比较文件用法：比较文件 文件1 文件2（如：比较文件 1.txt 2.txt）")
                self.terminal_edit.appendPlainText("输入【帮助 比较文件】查看详细用法")
                self.show_prompt()
                return
            elif command.startswith("比较文件 "):
                param = trim_string(command[4:])
                self.run_cmd(f"comp {param}")
                self.show_prompt()
                return
            elif command == "文件比较":
                self.terminal_edit.appendPlainText("[提示] 文件比较用法：文件比较 文件1 文件2（如：文件比较 1.txt 2.txt）")
                self.terminal_edit.appendPlainText("输入【帮助 文件比较】查看详细用法")
                self.show_prompt()
                return
            elif command.startswith("文件比较 "):
                param = trim_string(command[5:])
                self.run_cmd(f"fc {param}")
                self.show_prompt()
                return
            elif command == "NTFS压缩":
                self.run_cmd("compact")
                self.show_prompt()
                return
            elif command.startswith("NTFS压缩 "):
                param = trim_string(command[5:])
                self.run_cmd(f"compact {param}")
                self.show_prompt()
                return
            elif command == "转换分区格式":
                self.terminal_edit.appendPlainText("[提示] 转换分区格式用法：转换分区格式 盘符 /fs:ntfs（如：转换分区格式 D: /fs:ntfs）")
                self.terminal_edit.appendPlainText("输入【帮助 转换分区格式】查看详细用法")
                self.show_prompt()
                return
            elif command.startswith("转换分区格式 "):
                param = trim_string(command[6:])
                self.run_cmd(f"convert {param}")
                self.show_prompt()
                return
            elif command == "查找文本":
                self.terminal_edit.appendPlainText("[提示] 查找文本用法：查找文本 字符串 文件名（如：查找文本 hello 1.txt）")
                self.terminal_edit.appendPlainText("输入【帮助 查找文本】查看详细用法")
                self.show_prompt()
                return
            elif command.startswith("查找文本 "):
                param = trim_string(command[4:])
                self.run_cmd(f"find {param}")
                self.show_prompt()
                return
            elif command == "查找字符串":
                self.terminal_edit.appendPlainText("[提示] 查找字符串用法：查找字符串 字符串 文件名（如：查找字符串 hello 1.txt）")
                self.terminal_edit.appendPlainText("输入【帮助 查找字符串】查看详细用法")
                self.show_prompt()
                return
            elif command.startswith("查找字符串 "):
                param = trim_string(command[5:])
                self.run_cmd(f"findstr {param}")
                self.show_prompt()
                return
            elif command == "格式化磁盘":
                self.terminal_edit.appendPlainText("[提示] 格式化磁盘用法：格式化磁盘 盘符（如：格式化磁盘 D:）")
                self.terminal_edit.appendPlainText("输入【帮助 格式化磁盘】查看详细用法")
                self.show_prompt()
                return
            elif command.startswith("格式化磁盘 "):
                param = trim_string(command[5:])
                self.run_cmd(f"format {param}")
                self.show_prompt()
                return
            elif command == "文件系统配置":
                self.terminal_edit.appendPlainText("[提示] 文件系统配置用法：文件系统配置 命令（如：文件系统配置 fsutil volume info C:）")
                self.terminal_edit.appendPlainText("输入【帮助 文件系统配置】查看详细用法")
                self.show_prompt()
                return
            elif command.startswith("文件系统配置 "):
                param = trim_string(command[6:])
                self.run_cmd(f"fsutil {param}")
                self.show_prompt()
                return
            elif command == "文件类型关联":
                self.run_cmd("ftype")
                self.show_prompt()
                return
            elif command.startswith("文件类型关联 "):
                param = trim_string(command[6:])
                self.run_cmd(f"ftype {param}")
                self.show_prompt()
                return
            elif command == "磁盘卷标":
                self.terminal_edit.appendPlainText("[提示] 磁盘卷标用法：磁盘卷标 盘符 卷标名（如：磁盘卷标 D: 数据盘）")
                self.terminal_edit.appendPlainText("输入【帮助 磁盘卷标】查看详细用法")
                self.show_prompt()
                return
            elif command.startswith("磁盘卷标 "):
                param = trim_string(command[4:])
                self.run_cmd(f"label {param}")
                self.show_prompt()
                return
            elif command == "创建链接":
                self.terminal_edit.appendPlainText("[提示] 创建链接用法：创建链接 链接类型 链接名 目标（如：创建链接 /d 我的文档 D:\\文档）")
                self.terminal_edit.appendPlainText("输入【帮助 创建链接】查看详细用法")
                self.show_prompt()
                return
            elif command.startswith("创建链接 "):
                param = trim_string(command[4:])
                self.run_cmd(f"mklink {param}")
                self.show_prompt()
                return
            elif command == "打开文件查询":
                self.run_cmd("openfiles")
                self.show_prompt()
                return
            elif command.startswith("打开文件查询 "):
                param = trim_string(command[6:])
                self.run_cmd(f"openfiles {param}")
                self.show_prompt()
                return
            elif command == "中断检查":
                self.run_cmd("break")
                self.show_prompt()
                return
            elif command.startswith("中断检查 "):
                param = trim_string(command[4:])
                self.run_cmd(f"break {param}")
                self.show_prompt()
                return
            elif command == "启动配置":
                self.run_cmd("bcdedit")
                self.show_prompt()
                return
            elif command.startswith("启动配置 "):
                param = trim_string(command[4:])
                self.run_cmd(f"bcdedit {param}")
                self.show_prompt()
                return
            elif command == "访问控制列表":
                self.terminal_edit.appendPlainText("[提示] 访问控制列表用法：访问控制列表 文件名（如：访问控制列表 1.txt）")
                self.terminal_edit.appendPlainText("输入【帮助 访问控制列表】查看详细用法")
                self.show_prompt()
                return
            elif command.startswith("访问控制列表 "):
                param = trim_string(command[6:])
                self.run_cmd(f"icacls {param}")
                self.show_prompt()
                return
            elif command == "代码页设置":
                self.run_cmd("chcp")
                self.show_prompt()
                return
            elif command.startswith("代码页设置 "):
                param = trim_string(command[5:])
                self.run_cmd(f"chcp {param}")
                self.show_prompt()
                return
            elif command == "打开命令窗口":
                self.run_cmd("cmd")
                self.show_prompt()
                return
            elif command.startswith("打开命令窗口 "):
                param = trim_string(command[6:])
                self.run_cmd(f"cmd {param}")
                self.show_prompt()
                return
            elif command == "驱动查询":
                self.run_cmd("driverquery")
                self.show_prompt()
                return
            elif command.startswith("驱动查询 "):
                param = trim_string(command[4:])
                self.run_cmd(f"driverquery {param}")
                self.show_prompt()
                return
            elif command == "设备配置":
                self.terminal_edit.appendPlainText("[提示] 设备配置用法：设备配置 命令（如：设备配置 con: cols=80 lines=25）")
                self.terminal_edit.appendPlainText("输入【帮助 设备配置】查看详细用法")
                self.show_prompt()
                return
            elif command.startswith("设备配置 "):
                param = trim_string(command[4:])
                self.run_cmd(f"mode {param}")
                self.show_prompt()
                return
            elif command == "命令提示设置":
                self.terminal_edit.appendPlainText("[提示] 命令提示设置用法：命令提示设置 提示符（如：命令提示设置 $p$g）")
                self.terminal_edit.appendPlainText("输入【帮助 命令提示设置】查看详细用法")
                self.show_prompt()
                return
            elif command.startswith("命令提示设置 "):
                param = trim_string(command[6:])
                self.run_cmd(f"prompt {param}")
                self.show_prompt()
                return
            elif command == "服务配置":
                self.run_cmd("sc query")
                self.show_prompt()
                return
            elif command.startswith("服务配置 "):
                param = trim_string(command[4:])
                self.run_cmd(f"sc {param}")
                self.show_prompt()
                return
            elif command == "任务计划":
                self.run_cmd("schtasks /query")
                self.show_prompt()
                return
            elif command.startswith("任务计划 "):
                param = trim_string(command[4:])
                self.run_cmd(f"schtasks {param}")
                self.show_prompt()
                return
            elif command == "关闭计算机":
                self.terminal_edit.appendPlainText("[提示] 关闭计算机用法：关闭计算机 /s /t 30（30秒后关闭）")
                self.terminal_edit.appendPlainText("输入【帮助 关闭计算机】查看详细用法")
                self.show_prompt()
                return
            elif command.startswith("关闭计算机 "):
                param = trim_string(command[5:])
                self.run_cmd(f"shutdown {param}")
                self.show_prompt()
                return
            elif command == "排序输入":
                self.terminal_edit.appendPlainText("[提示] 排序输入用法：排序输入 文件名（如：排序输入 1.txt）")
                self.terminal_edit.appendPlainText("输入【帮助 排序输入】查看详细用法")
                self.show_prompt()
                return
            elif command.startswith("排序输入 "):
                param = trim_string(command[4:])
                self.run_cmd(f"sort {param}")
                self.show_prompt()
                return
            elif command == "启动程序":
                self.terminal_edit.appendPlainText("[提示] 启动程序用法：启动程序 程序名（如：启动程序 notepad）")
                self.terminal_edit.appendPlainText("输入【帮助 启动程序】查看详细用法")
                self.show_prompt()
                return
            elif command.startswith("启动程序 "):
                param = trim_string(command[4:])
                self.run_cmd(f"start {param}")
                self.show_prompt()
                return
            elif command == "时间设置":
                self.run_cmd("time")
                self.show_prompt()
                return
            elif command.startswith("时间设置 "):
                param = trim_string(command[4:])
                self.run_cmd(f"time {param}")
                self.show_prompt()
                return
            elif command == "窗口标题设置":
                self.terminal_edit.appendPlainText("[提示] 窗口标题设置用法：窗口标题设置 标题名（如：窗口标题设置 我的命令行）")
                self.terminal_edit.appendPlainText("输入【帮助 窗口标题设置】查看详细用法")
                self.show_prompt()
                return
            elif command.startswith("窗口标题设置 "):
                param = trim_string(command[6:])
                self.run_cmd(f"title {param}")
                self.show_prompt()
                return
            elif command == "查看Windows版本":
                self.run_cmd("ver")
                self.show_prompt()
                return
            elif command == "文件写入验证":
                self.run_cmd("verify")
                self.show_prompt()
                return
            elif command.startswith("文件写入验证 "):
                param = trim_string(command[6:])
                self.run_cmd(f"verify {param}")
                self.show_prompt()
                return
            elif command == "磁盘卷标查看":
                self.run_cmd("vol")
                self.show_prompt()
                return
            elif command.startswith("磁盘卷标查看 "):
                param = trim_string(command[6:])
                self.run_cmd(f"vol {param}")
                self.show_prompt()
                return
            elif command == "WMI信息查询":
                self.terminal_edit.appendPlainText("[提示] WMI信息查询用法：WMI信息查询 命令（如：WMI信息查询 cpu get name）")
                self.terminal_edit.appendPlainText("输入【帮助 WMI信息查询】查看详细用法")
                self.show_prompt()
                return
            elif command.startswith("WMI信息查询 "):
                param = trim_string(command[6:])
                self.run_cmd(f"wmic {param}")
                self.show_prompt()
                return
            elif command == "查看进程":
                self.run_cmd("tasklist")
                self.show_prompt()
                return
            elif command.startswith("查看进程 "):
                param = trim_string(command[4:])
                self.run_cmd(f"tasklist {param}")
                self.show_prompt()
                return
            elif command == "结束进程":
                self.terminal_edit.appendPlainText("[提示] 结束进程用法：结束进程 进程名/PID（如：结束进程 notepad.exe 或 结束进程 /pid 1234）")
                self.terminal_edit.appendPlainText("输入【帮助 结束进程】查看详细用法")
                self.show_prompt()
                return
            elif command.startswith("结束进程 "):
                param = trim_string(command[4:])
                self.run_cmd(f"taskkill /f /im {param} || taskkill /f {param}")
                self.show_prompt()
                return
            elif command == "系统信息":
                self.run_cmd("systeminfo")
                self.show_prompt()
                return
            elif command.startswith("系统信息 "):
                param = trim_string(command[4:])
                self.run_cmd(f"systeminfo {param}")
                self.show_prompt()
                return
            elif command == "查看IP":
                self.run_cmd("ipconfig")
                self.show_prompt()
                return
            elif command.startswith("查看IP "):
                param = trim_string(command[3:])
                self.run_cmd(f"ipconfig {param}")
                self.show_prompt()
                return
            elif command == "环境变量":
                self.run_cmd("set")
                self.show_prompt()
                return
            elif command.startswith("环境变量 "):
                param = trim_string(command[4:])
                self.run_cmd(f"set {param}")
                self.show_prompt()
                return
            elif command == "查看路径":
                self.run_cmd("path")
                self.show_prompt()
                return
            elif command.startswith("查看路径 "):
                param = trim_string(command[4:])
                self.run_cmd(f"path {param}")
                self.show_prompt()
                return
            elif command == "磁盘分区管理":
                self.run_cmd("diskpart")
                self.show_prompt()
                return
            elif command.startswith("磁盘分区管理 "):
                param = trim_string(command[6:])
                self.run_cmd(f"diskpart {param}")
                self.show_prompt()
                return
            elif command == "查看映像":
                self.run_cmd("subst")
                self.show_prompt()
                return
            elif command == "挂载映像":
                self.terminal_edit.appendPlainText("[提示] 挂载映像用法：挂载映像 路径 盘符（如：挂载映像 D:\\temp\\image.iso Z:）")
                self.terminal_edit.appendPlainText("输入【帮助 挂载映像】查看详细用法")
                self.show_prompt()
                return
            elif command.startswith("挂载映像 "):
                param = trim_string(command[4:])
                self.run_cmd(f"subst {param}")
                self.show_prompt()
                return
            elif command == "卸载映像":
                self.terminal_edit.appendPlainText("[提示] 卸载映像用法：卸载映像 盘符（如：卸载映像 Z:）")
                self.terminal_edit.appendPlainText("输入【帮助 卸载映像】查看详细用法")
                self.show_prompt()
                return
            elif command.startswith("卸载映像 "):
                param = trim_string(command[4:])
                self.run_cmd(f"subst {param} /d")
                self.show_prompt()
                return
            elif command == "打开记事本":
                self.run_cmd("notepad")
                self.show_prompt()
                return
            elif command.startswith("打开记事本 "):
                param = trim_string(command[5:])
                self.run_cmd(f"notepad {param}")
                self.show_prompt()
                return
            elif command == "打开计算器":
                self.run_cmd("calc")
                self.show_prompt()
                return
            elif command == "打开注册表":
                self.run_cmd("regedit")
                self.show_prompt()
                return
            elif command == "打开任务管理器":
                self.run_cmd("taskmgr")
                self.show_prompt()
                return
            elif command == "分屏显示":
                self.terminal_edit.appendPlainText("[提示] 分屏显示用法：分屏显示 文件名（如：分屏显示 1.txt）")
                self.terminal_edit.appendPlainText("输入【帮助 分屏显示】查看详细用法")
                self.show_prompt()
                return
            elif command.startswith("分屏显示 "):
                param = trim_string(command[4:])
                self.run_cmd(f"more {param}")
                self.show_prompt()
                return
            elif command == "暂停批处理":
                self.run_cmd("pause")
                self.show_prompt()
                return
            elif command == "打印":
                self.terminal_edit.appendPlainText("[提示] 打印用法：打印 文件名（如：打印 1.txt）")
                self.terminal_edit.appendPlainText("输入【帮助 打印】查看详细用法")
                self.show_prompt()
                return
            elif command.startswith("打印 "):
                param = trim_string(command[2:])
                self.run_cmd(f"print {param}")
                self.show_prompt()
                return

            elif command == "自定义命令":
                self.terminal_edit.appendPlainText("[提示] 自定义命令用法：")
                self.terminal_edit.appendPlainText("  自定义命令                - 查看所有自定义命令")
                self.terminal_edit.appendPlainText("  自定义命令 别名=命令       - 设置自定义命令（如：自定义命令 查看=dir）")
                self.terminal_edit.appendPlainText("  自定义命令 /d 别名         - 删除自定义命令（如：自定义命令 /d 查看）")
                self.terminal_edit.appendPlainText("  自定义命令 /s 文件名       - 保存自定义命令到文件（如：自定义命令 /s cmds.doskey）")
                self.terminal_edit.appendPlainText("  自定义命令 /c 文件名       - 清除所有自定义命令")
                self.terminal_edit.appendPlainText("  自定义命令 /l 文件名       - 从文件加载自定义命令（如：自定义命令 /l cmds.doskey）")
                self.show_prompt()
                return
            elif command.startswith("自定义命令 "):
                param = trim_string(command[5:])
                self.run_cmd(f"doskey {param}")
                self.show_prompt()
                return

            elif command == "cls":
                self.clear_screen()
                return
            elif command == "exit":
                self.close()
                return

            else:
                self.run_cmd(command)
                self.show_prompt()
        except Exception as e:
            self.terminal_edit.appendPlainText(f"[错误] 执行命令时发生错误：{str(e)}")
            self.show_prompt()
    def is_url(self, text):
        """判断是否为网址"""
        if (text.startswith("http://") or text.startswith("https://")) and "." in text:
            return True
        elif text.startswith("www.") and "." in text:
            return True
        elif "." in text and any(text.endswith(suffix) for suffix in [".com", ".cn", ".net", ".org", ".io", ".gov", ".edu"]):
            return True
        return False
    def is_expression(self, text):
        """判断是否为数学表达式"""
        operators = "+-*/^()√π"
        has_operator = any(op in text for op in operators)
        has_digit = any(char.isdigit() for char in text)
        return has_operator and has_digit
    def calculate_expression(self, expression):
        """计算数学表达式"""
        try:

            expression = expression.replace("√", "math.sqrt")
            expression = expression.replace("^", "**")
            expression = expression.replace("π", "math.pi")

            import math
            result = eval(expression, {"__builtins__": None}, {"math": math, "sqrt": math.sqrt, "pi": math.pi})
            self.terminal_edit.appendPlainText(f"计算结果：{result}")
        except Exception as e:
            self.terminal_edit.appendPlainText(f"[错误] 计算失败：{str(e)}")
    def set_background_color(self, color_input):
        """设置背景颜色"""
        color_map = {
            "黑色": "#000000",
            "深灰色": "#2d2d2d",
            "浅灰色": "#f0f0f0",
            "白色": "#ffffff",
            "红色": "#ff0000",
            "绿色": "#00ff00",
            "蓝色": "#0000ff",
            "黄色": "#ffff00",
            "青色": "#00ffff",
            "紫色": "#ff00ff",
            "橙色": "#ff9900",
            "粉色": "#ff99cc",
            "深蓝色": "#003366",
            "浅绿色": "#99cc99"
        }
        if color_input in color_map:
            self.bg_color = color_map[color_input]
            self.update_background_color()
            self.terminal_edit.appendPlainText(f"背景颜色已设置为：{color_input}（{self.bg_color}）")
        elif len(color_input) == 7 and color_input.startswith("#"):
            try:
                int(color_input[1:], 16)
                self.bg_color = color_input
                self.update_background_color()
                self.terminal_edit.appendPlainText(f"背景颜色已设置为：{self.bg_color}")
            except ValueError:
                self.terminal_edit.appendPlainText("[错误] 无效的颜色值，请输入有效的十六进制颜色（如#2d2d2d）或中文颜色名称（如深灰色）")
        else:
            self.terminal_edit.appendPlainText("[提示] 设置背景颜色用法：\n1. 设置背景颜色 中文颜色名称（如：设置背景颜色 深灰色）\n2. 设置背景颜色 #十六进制颜色值（如：设置背景颜色 #2d2d2d）\n支持的中文颜色名称：黑色、深灰色、浅灰色、白色、红色、绿色、蓝色、黄色、青色、紫色、橙色、粉色、深蓝色、浅绿色")
    def update_background_color(self):
        """更新背景颜色"""
        self.terminal_edit.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {self.bg_color};
                color: #ffffff;
                selection-background-color: #0047ab;
                border: none;
                padding: 5px;
                font-family: "Consolas", "Monaco", "Courier New", monospace;
                font-size: 12px;
            }}
        """)
    def show_global_help(self):
        """显示全局帮助"""
        help_text = """有关某个命令的详细信息，请键入 帮助 命令名
【基础操作类】
  帮助          - 显示帮助信息
  清屏          - 清空屏幕显示（对应cls）
  退出          - 退出命令行工具（对应exit）
  计算          - 进行数学计算（如：计算 1+2*3）
【自定义设置类】
  设置背景颜色  - 设置终端背景颜色，支持中文颜色名称和十六进制颜色值
  自定义命令    - 设置/查看/删除/保存/加载自定义命令别名（对应doskey）
【常用工具类】
  打开记事本    - 启动Windows记事本（对应notepad）
  打开计算器    - 启动Windows计算器（对应calc）
  打开注册表    - 启动注册表编辑器（对应regedit）
  打开任务管理器- 启动Windows任务管理器（对应taskmgr）
  打开浏览器    - 打开内置浏览器，支持访问任意网址
  分屏显示      - 逐屏显示输出（对应more）
  暂停批处理    - 暂停批处理文件的处理并显示消息（对应pause）
  打印          - 打印文本文件（对应print）
【文件管理类】
  查看目录      - 显示目录中的文件和子目录（对应dir）
  切换目录      - 改变当前目录（对应cd）
  新建目录      - 创建目录（对应md）
  删除目录      - 删除目录（对应rd）
  复制文件      - 复制一个或多个文件到另一个位置（对应copy）
  移动文件      - 移动文件并重命名文件和目录（对应move）
  删除文件      - 删除一个或多个文件（对应del）
  重命名文件    - 重命名文件或目录（对应ren）
  复制目录树    - 复制目录树（对应xcopy）
  高级复制      - 高级文件复制（对应robocopy）
  替换文件      - 替换文件（对应replace）
  查看文件内容  - 显示文本文件的内容（对应type）
  恢复文件      - 恢复损坏的文件（对应recover）
  文件关联      - 显示或修改文件扩展名关联（对应assoc）
  文件属性      - 显示或更改文件属性（对应attrib）
  比较文件      - 比较两个文件的内容（对应comp）
  文件比较      - 比较两个文件的内容（对应fc）
  NTFS压缩      - 显示或改变NTFS压缩（对应compact）
  转换分区格式  - 将FAT卷转换为NTFS（对应convert）
  查找文本      - 在文件中搜索字符串（对应find）
  查找字符串    - 在文件中搜索字符串（对应findstr）
  格式化磁盘    - 格式化磁盘（对应format）
  文件系统配置  - 配置文件系统（对应fsutil）
  文件类型关联  - 显示或修改文件类型关联（对应ftype）
  磁盘卷标      - 设置磁盘卷标（对应label）
  创建链接      - 创建符号链接或硬链接（对应mklink）
  打开文件查询  - 显示远程用户为了文件共享而打开的文件（对应openfiles）
【系统管理类】
  中断检查      - 设置或清除扩展的Ctrl+C检查（对应break）
  启动配置      - 设置启动配置数据存储（对应bcdedit）
  访问控制列表  - 显示或修改文件访问控制列表（对应icacls）
  代码页设置    - 显示或更改活动代码页编号（对应chcp）
  打开命令窗口  - 打开新的命令窗口（对应cmd）
  驱动查询      - 显示设备驱动程序信息（对应driverquery）
  设备配置      - 配置系统设备（对应mode）
  命令提示设置  - 更改命令提示符（对应prompt）
  服务配置      - 配置服务（对应sc）
  任务计划      - 安排命令和程序在指定时间和日期运行（对应schtasks）
  关闭计算机    - 关闭或重新启动计算机（对应shutdown）
  排序输入      - 对输入进行排序（对应sort）
  启动程序      - 启动程序或打开文件（对应start）
  时间设置      - 显示或设置系统时间（对应time）
  窗口标题设置  - 设置命令窗口标题（对应title）
  查看Windows版本 - 显示Windows版本（对应ver）
  文件写入验证  - 确定文件是否在写入时得到验证（对应verify）
  磁盘卷标查看  - 显示磁盘卷标和序列号（对应vol）
  WMI信息查询   - WMI命令行（对应wmic）
  查看进程      - 显示进程列表（对应tasklist）
  结束进程      - 结束进程（对应taskkill）
  系统信息      - 显示系统信息（对应systeminfo）
  查看IP        - 显示IP配置信息（对应ipconfig）
  环境变量      - 显示、设置或删除环境变量（对应set）
  查看路径      - 显示或设置可执行文件的搜索路径（对应path）
  磁盘分区管理  - 磁盘分区管理（对应diskpart）
  查看映像      - 显示虚拟驱动器的映射（对应subst）
  挂载映像      - 将路径与驱动器号关联（对应subst）
  卸载映像      - 删除虚拟驱动器的映射（对应subst /d）
【其他命令】
  鸣谢名单      - 显示鸣谢信息
  cls           - 清空屏幕显示（对应清屏）
  exit          - 退出命令行工具（对应退出）
"""
        self.terminal_edit.appendPlainText(help_text)
    def show_single_help(self, topic):
        """显示单个命令的帮助"""
        help_mapping = {
            "设置背景颜色": """
  指令：设置背景颜色
功能：设置终端的背景颜色，支持中文颜色名称和十六进制颜色值
用法：
  1. 设置背景颜色 中文颜色名称    - 设置终端背景为指定颜色（如：设置背景颜色 深灰色）
  2. 设置背景颜色 #十六进制颜色值    - 设置终端背景为指定颜色（如：设置背景颜色 #2d2d2d）
  支持的中文颜色名称及对应值：
     - 黑色：#000000
     - 深灰色：#2d2d2d
     - 浅灰色：#f0f0f0
     - 白色：#ffffff
     - 红色：#ff0000
     - 绿色：#00ff00
     - 蓝色：#0000ff
     - 黄色：#ffff00
     - 青色：#00ffff
     - 紫色：#ff00ff
     - 橙色：#ff9900
     - 粉色：#ff99cc
     - 深蓝色：#003366
     - 浅绿色：#99cc99
 """,
            "打开浏览器": """
  指令：打开浏览器
功能：打开内置浏览器，支持访问任意网址
用法：
  1. 打开浏览器                - 打开内置浏览器，默认打开Bing
  2. 在浏览器地址栏输入网址，按回车即可访问
  3. 直接在命令行输入网址，自动打开浏览器访问
  4. 点击网页链接会在当前标签页中打开
 """,
            "计算": """
  指令：计算
功能：进行数学计算
用法：
  1. 计算 数学表达式    - 计算指定的数学表达式
  2. 直接输入数学表达式，如：1+2*3
支持的运算符：+、-、*、/、^（乘方）、√（开方）、π（圆周率）
示例：
  计算 1+2*3 = 7
  计算 √16 = 4
  计算 π*2^2 = 12.566370614359172
 """,
            "鸣谢名单": """
  指令：鸣谢名单
功能：显示鸣谢信息
用法：
  鸣谢名单    - 显示作者和测试者信息
 """,
            "查看目录": """
  指令：查看目录
功能：显示目录中的文件和子目录（对应dir命令）
用法：
  1. 查看目录                - 显示当前目录的文件和子目录
  2. 查看目录 路径            - 显示指定路径的文件和子目录
  3. 查看目录 /w              - 以宽格式显示
  4. 查看目录 /p              - 分页显示
  5. 查看目录 /s              - 显示所有子目录中的文件
 """,
            "切换目录": """
  指令：切换目录
功能：改变当前目录（对应cd命令）
用法：
  1. 切换目录 路径            - 切换到指定路径
  2. 切换目录 ..              - 切换到上级目录
  3. 切换目录 /d 盘符:        - 切换到指定盘符
  4. 切换目录                - 显示当前目录
 """,
            "新建目录": """
  指令：新建目录
功能：创建目录（对应md命令）
用法：
  1. 新建目录 目录名          - 在当前目录创建新目录
  2. 新建目录 路径\目录名      - 在指定路径创建新目录
 """,
            "删除目录": """
  指令：删除目录
功能：删除目录（对应rd命令）
用法：
  1. 删除目录 目录名          - 删除空目录
  2. 删除目录 /s 目录名        - 删除目录及其所有子目录和文件
  3. 删除目录 /q /s 目录名      - 安静模式删除，不提示确认
 """,
            "复制文件": """
  指令：复制文件
功能：复制一个或多个文件到另一个位置（对应copy命令）
用法：
  1. 复制文件 源文件 目标文件    - 复制文件
  2. 复制文件 源文件 目标路径    - 复制文件到指定路径
  3. 复制文件 *.txt 目标路径     - 复制所有txt文件到指定路径
 """,
            "移动文件": """
  指令：移动文件
功能：移动文件并重命名文件和目录（对应move命令）
用法：
  1. 移动文件 源文件 目标文件    - 移动并重命名文件
  2. 移动文件 源文件 目标路径    - 移动文件到指定路径
  3. 移动文件 *.txt 目标路径     - 移动所有txt文件到指定路径
 """,
            "删除文件": """
  指令：删除文件
功能：删除一个或多个文件（对应del命令）
用法：
  1. 删除文件 文件名          - 删除指定文件
  2. 删除文件 *.txt          - 删除所有txt文件
  3. 删除文件 /f 文件名        - 强制删除只读文件
  4. 删除文件 /s 文件名        - 删除所有子目录中的指定文件
 """,
            "重命名文件": """
  指令：重命名文件
功能：重命名文件或目录（对应ren命令）
用法：
  1. 重命名文件 旧文件名 新文件名  - 重命名文件
  2. 重命名文件 *.txt *.bak      - 将所有txt文件重命名为bak文件
 """,
            "查看进程": """
  指令：查看进程
功能：显示进程列表（对应tasklist命令）
用法：
  1. 查看进程                - 显示所有进程
  2. 查看进程 /svc            - 显示每个进程的服务
  3. 查看进程 /m 模块名        - 显示使用指定模块的进程
  4. 查看进程 /fi "PID eq 1234" - 显示指定PID的进程
 """,
            "结束进程": """
  指令：结束进程
功能：结束进程（对应taskkill命令）
用法：
  1. 结束进程 进程名          - 结束指定进程名的所有进程
  2. 结束进程 /pid 进程ID      - 结束指定PID的进程
  3. 结束进程 /f 进程名        - 强制结束进程
  4. 结束进程 /t 进程名        - 结束进程及其子进程
 """,
            "系统信息": """
  指令：系统信息
功能：显示系统信息（对应systeminfo命令）
用法：
  1. 系统信息                - 显示所有系统信息
  2. 系统信息 /s 计算机名      - 显示远程计算机的系统信息
  3. 系统信息 /fo csv          - 以CSV格式输出
 """,
            "查看IP": """
  指令：查看IP
功能：显示IP配置信息（对应ipconfig命令）
用法：
  1. 查看IP                  - 显示所有网络适配器的IP配置
  2. 查看IP /all             - 显示所有网络适配器的完整配置信息
  3. 查看IP /release          - 释放IP地址
  4. 查看IP /renew            - 重新获取IP地址
  5. 查看IP /flushdns         - 刷新DNS解析缓存
 """,
            "打开记事本": """
  指令：打开记事本
功能：启动Windows记事本（对应notepad命令）
用法：
  1. 打开记事本              - 打开新的记事本
  2. 打开记事本 文件名        - 用记事本打开指定文件
 """,
            "打开计算器": """
  指令：打开计算器
功能：启动Windows计算器（对应calc命令）
用法：
  1. 打开计算器              - 打开计算器
 """,
            "打开注册表": """
  指令：打开注册表
功能：启动注册表编辑器（对应regedit命令）
用法：
  1. 打开注册表              - 打开注册表编辑器
 """,
            "打开任务管理器": """
  指令：打开任务管理器
功能：启动Windows任务管理器（对应taskmgr命令）
用法：
  1. 打开任务管理器          - 打开任务管理器
 """,
            "自定义命令": """
  指令：自定义命令
功能：设置/查看/删除/保存/加载自定义命令别名（对应doskey命令）
用法：
  1. 自定义命令                - 查看所有自定义命令
  2. 自定义命令 别名=命令       - 设置自定义命令（如：自定义命令 查看=dir）
  3. 自定义命令 /d 别名         - 删除自定义命令（如：自定义命令 /d 查看）
  4. 自定义命令 /s 文件名       - 保存自定义命令到文件（如：自定义命令 /s cmds.doskey）
  5. 自定义命令 /c 文件名       - 清除所有自定义命令
  6. 自定义命令 /l 文件名       - 从文件加载自定义命令（如：自定义命令 /l cmds.doskey）
 """
        }
        if topic in help_mapping:
            self.terminal_edit.appendPlainText(help_mapping[topic])
        else:
            self.terminal_edit.appendPlainText(f"[提示] 未找到命令「{topic}」的帮助信息")
class BrowserTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.url_bar.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                selection-background-color: #0047ab;
                border: 1px solid #333333;
                padding: 5px;
                font-family: "Consolas", "Monaco", "Courier New", monospace;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #0047ab;
            }
        """)
        layout.addWidget(self.url_bar)

        self.web_view = QWebEngineView()
        self.web_view.urlChanged.connect(self.update_url_bar)

        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadImages, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadIconsForPage, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True)

        self.web_view.page().profile().setHttpUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        self.web_view.page().profile().downloadRequested.connect(self.handle_download)

        self.web_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.web_view.customContextMenuRequested.connect(self.show_context_menu)

        self.web_view.setUrl(QUrl("https://www.bing.com"))
        layout.addWidget(self.web_view)
        self.setLayout(layout)
    def navigate_to_url(self):
        """导航到指定URL"""
        url = self.url_bar.text()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        self.web_view.setUrl(QUrl(url))
    def update_url_bar(self, url):
        """更新地址栏"""
        self.url_bar.setText(url.toString())
    def handle_download(self, download):
        """处理下载请求，显示下载进度"""
        from PyQt6.QtWidgets import QFileDialog, QProgressDialog, QMessageBox
        from PyQt6.QtCore import Qt
        from PyQt6.QtWebEngineCore import QWebEngineDownloadItem
        default_filename = download.url().fileName()
        save_path, _ = QFileDialog.getSaveFileName(self, "保存文件", default_filename)
        if save_path:
            download.setPath(save_path)

            progress_dialog = QProgressDialog("正在下载...", "取消下载", 0, 100, self)
            progress_dialog.setWindowTitle("下载进度")
            progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
            progress_dialog.setMinimumDuration(0)
            progress_dialog.show()

            def update_progress(bytes_received, bytes_total):
                if bytes_total > 0:
                    progress = int((bytes_received / bytes_total) * 100)
                    progress_dialog.setValue(progress)
                    progress_dialog.setLabelText(f"正在下载 {default_filename}：{bytes_received/1024/1024:.2f}MB / {bytes_total/1024/1024:.2f}MB")

            def on_download_finished():
                progress_dialog.close()
                if download.state() == QWebEngineDownloadItem.State.DownloadCompleted:
                    QMessageBox.information(self, "下载完成", f"文件 {default_filename} 已成功下载到 {save_path}")
                elif download.state() == QWebEngineDownloadItem.State.DownloadCancelled:
                    QMessageBox.information(self, "下载取消", "下载已被用户取消")
                else:
                    QMessageBox.warning(self, "下载失败", f"文件 {default_filename} 下载失败，请检查网络或文件路径")

            download.progressChanged.connect(update_progress)
            download.finished.connect(on_download_finished)

            progress_dialog.canceled.connect(download.cancel)
            download.accept()
    def createWindow(self, windowType):
        """处理新窗口请求 - 所有链接都在当前标签页打开"""
        if windowType in [QWebEnginePage.WebWindowType.WebBrowserWindow,
                         QWebEnginePage.WebWindowType.WebBrowserTab,
                         QWebEnginePage.WebWindowType.WebDialog]:

            return self.web_view
        return super().createWindow(windowType)
    def show_context_menu(self, position):
        """显示中文右键菜单"""
        from PyQt6.QtWidgets import QMenu
        from PyQt6.QtWebEngineCore import QWebEnginePage
        menu = QMenu()

        back_action = menu.addAction("后退")
        back_action.triggered.connect(self.web_view.back)
        back_action.setEnabled(self.web_view.history().canGoBack())
        forward_action = menu.addAction("前进")
        forward_action.triggered.connect(self.web_view.forward)
        forward_action.setEnabled(self.web_view.history().canGoForward())
        refresh_action = menu.addAction("刷新")
        refresh_action.triggered.connect(self.web_view.reload)
        menu.addSeparator()

        copy_action = menu.addAction("复制")
        copy_action.triggered.connect(lambda: self.web_view.page().triggerAction(QWebEnginePage.WebAction.Copy))
        paste_action = menu.addAction("粘贴")
        paste_action.triggered.connect(lambda: self.web_view.page().triggerAction(QWebEnginePage.WebAction.Paste))
        select_all_action = menu.addAction("全选")
        select_all_action.triggered.connect(lambda: self.web_view.page().triggerAction(QWebEnginePage.WebAction.SelectAll))
        menu.addSeparator()

        save_action = menu.addAction("另存为")
        save_action.triggered.connect(self.save_page)
        view_source_action = menu.addAction("查看源代码")
        view_source_action.triggered.connect(self.view_source)
        menu.addSeparator()

        open_in_new_tab_action = menu.addAction("在新标签页打开链接")
        open_in_new_tab_action.triggered.connect(self.open_link_in_new_tab)
        menu.exec(self.web_view.mapToGlobal(position))
    def save_page(self):
        """保存页面"""
        from PyQt6.QtWidgets import QFileDialog
        from PyQt6.QtWebEngineCore import QWebEnginePage
        save_path, _ = QFileDialog.getSaveFileName(self, "保存网页", "", "网页文件 (*.html *.htm);;所有文件 (*.*)")
        if save_path:
            self.web_view.page().save(save_path, QWebEnginePage.SaveFormat.CompleteHtml)
    def view_source(self):
        """查看源代码"""
        from PyQt6.QtWidgets import QDialog, QPlainTextEdit, QVBoxLayout
        from PyQt6.QtCore import QEventLoop
        dialog = QDialog(self)
        dialog.setWindowTitle("查看网页源代码")
        dialog.resize(800, 600)
        text_edit = QPlainTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setStyleSheet("""
            QPlainTextEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                font-family: "Consolas", "Monaco", "Courier New", monospace;
                font-size: 12px;
            }
        """)
        layout = QVBoxLayout()
        layout.addWidget(text_edit)
        dialog.setLayout(layout)

        loop = QEventLoop()
        def on_get_html(html):
            text_edit.setPlainText(html)
            loop.quit()

        self.web_view.page().toHtml(on_get_html)

        loop.exec()

        dialog.exec()
    def open_link_in_new_tab(self):
        """在新标签页打开链接（保留该功能，用户可选择）"""
        main_window = self.window()
        new_browser = BrowserTab()
        tab_index = main_window.tab_widget.addTab(new_browser, "新标签页")
        main_window.tab_widget.setCurrentIndex(tab_index)

        def on_get_url(url):
            if url:
                if not url.startswith("http://") and not url.startswith("https://"):
                    url = "https://" + url
                new_browser.url_bar.setText(url)
                new_browser.navigate_to_url()
        self.web_view.page().runJavaScript("window.getSelection().toString()", on_get_url)
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cmd-ZH beta 5.0")
        self.setGeometry(100, 100, 800, 600)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #2d2d2d;
            }
            QWidget {
                background-color: #2d2d2d;
            }
        """)
        self.init_ui()
        self.add_new_tab()
    def init_ui(self):

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        central_widget.setLayout(main_layout)

        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #333333;
                background-color: #2d2d2d;
            }
            QTabBar::tab {
                background-color: #333333;
                color: #ffffff;
                padding: 5px 10px;
                margin-right: 2px;
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
                min-width: 80px;
            }
            QTabBar::tab:selected {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #333333;
                border-bottom: none;
            }
            QTabBar::tab:hover {
                background-color: #444444;
            }
        """)
        self.tab_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tab_widget.customContextMenuRequested.connect(self.show_tab_context_menu)
        main_layout.addWidget(self.tab_widget)
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(5)
        new_tab_btn = QPushButton("新建标签页")
        new_tab_btn.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                color: #ffffff;
                border: 1px solid #444444;
                padding: 5px 10px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #444444;
            }
            QPushButton:pressed {
                background-color: #222222;
            }
        """)
        new_tab_btn.clicked.connect(self.add_new_tab)
        toolbar_layout.addWidget(new_tab_btn)
        new_browser_btn = QPushButton("新建浏览器")
        new_browser_btn.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                color: #ffffff;
                border: 1px solid #444444;
                padding: 5px 10px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #444444;
            }
            QPushButton:pressed {
                background-color: #222222;
            }
        """)
        new_browser_btn.clicked.connect(self.add_browser_tab)
        toolbar_layout.addWidget(new_browser_btn)
        close_tab_btn = QPushButton("关闭标签页")
        close_tab_btn.setStyleSheet("""
            QPushButton {
                background-color: #333333;
                color: #ffffff;
                border: 1px solid #444444;
                padding: 5px 10px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #444444;
            }
            QPushButton:pressed {
                background-color: #222222;
            }
        """)
        close_tab_btn.clicked.connect(self.close_current_tab)
        toolbar_layout.addWidget(close_tab_btn)
        toolbar_layout.addStretch()
        main_layout.addLayout(toolbar_layout)
    def add_new_tab(self):
        terminal_tab = TerminalTab()
        tab_index = self.tab_widget.addTab(terminal_tab, f"终端 {self.tab_widget.count() + 1}")
        self.tab_widget.setCurrentIndex(tab_index)
    def add_browser_tab(self):
        browser_tab = BrowserTab()
        tab_index = self.tab_widget.addTab(browser_tab, f"浏览器 {self.tab_widget.count() + 1}")
        self.tab_widget.setCurrentIndex(tab_index)
    def close_current_tab(self):
        current_index = self.tab_widget.currentIndex()
        if current_index >= 0:
            self.tab_widget.removeTab(current_index)
    def show_tab_context_menu(self, position):
        menu = QMenu()
        new_tab_action = menu.addAction("新建终端标签页")
        new_tab_action.triggered.connect(self.add_new_tab)
        new_browser_action = menu.addAction("新建浏览器标签页")
        new_browser_action.triggered.connect(self.add_browser_tab)
        menu.addSeparator()
        close_tab_action = menu.addAction("关闭当前标签页")
        close_tab_action.triggered.connect(self.close_current_tab)
        close_other_action = menu.addAction("关闭其他标签页")
        close_other_action.triggered.connect(self.close_other_tabs)
        menu.exec(self.tab_widget.mapToGlobal(position))
    def close_other_tabs(self):
        current_index = self.tab_widget.currentIndex()
        if current_index >= 0:
            for i in range(self.tab_widget.count() - 1, -1, -1):
                if i != current_index:
                    self.tab_widget.removeTab(i)
def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet("""
        QMenu {
            background-color: #333333;
            color: #ffffff;
            border: 1px solid #444444;
        }
        QMenu::item {
            padding: 5px 20px;
        }
        QMenu::item:selected {
            background-color: #0047ab;
        }
        QMessageBox {
            background-color: #2d2d2d;
            color: #ffffff;
        }
        QMessageBox QLabel {
            color: #ffffff;
        }
        QMessageBox QPushButton {
            background-color: #333333;
            color: #ffffff;
            border: 1px solid #444444;
            padding: 5px 15px;
        }
        QMessageBox QPushButton:hover {
            background-color: #444444;
        }
        QFileDialog {
            background-color: #2d2d2d;
            color: #ffffff;
        }
        QFileDialog QLabel {
            color: #ffffff;
        }
        QFileDialog QPushButton {
            background-color: #333333;
            color: #ffffff;
            border: 1px solid #444444;
            padding: 5px 15px;
        }
        QFileDialog QPushButton:hover {
            background-color: #444444;
        }
        QProgressDialog {
            background-color: #2d2d2d;
            color: #ffffff;
        }
        QProgressDialog QLabel {
            color: #ffffff;
        }
        QProgressDialog QPushButton {
            background-color: #333333;
            color: #ffffff;
            border: 1px solid #444444;
            padding: 5px 15px;
        }
        QProgressDialog QPushButton:hover {
            background-color: #444444;
        }
        QDialog {
            background-color: #2d2d2d;
            color: #ffffff;
        }
        QDialog QLabel {
            color: #ffffff;
        }
    """)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
if __name__ == "__main__":
    main()