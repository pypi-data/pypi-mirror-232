import os
import queue
import shutil
import subprocess
import sys
import threading
import typing
from pathlib import Path
from queue import Queue
from threading import Thread

from PySide6.QtCore import QTimer
from je_editor.pyside_ui.main_ui.save_settings.user_color_setting_file import actually_color_dict

from automation_editor.automation_editor_ui.show_code_window.code_window import CodeWindow
from automation_editor.utils.exception.exception_tags import compiler_not_found_error
from automation_editor.utils.exception.exceptions import ITEExecException


class TaskProcessManager(object):
    def __init__(
            self,
            main_window: CodeWindow,
            task_done_trigger_function: typing.Callable = None,
            error_trigger_function: typing.Callable = None,
            program_buffer_size: int = 1024000,
            program_encoding: str = "utf-8"
    ):
        super().__init__()
        # ite_instance param
        self.read_program_error_output_from_thread: [threading.Thread, None] = None
        self.read_program_output_from_thread: [threading.Thread, None] = None
        self.main_window: CodeWindow = main_window
        self.timer: QTimer = QTimer(self.main_window)
        self.still_run_program: bool = True
        self.program_encoding: str = program_encoding
        self.run_output_queue: Queue = Queue()
        self.run_error_queue: Queue = Queue()
        self.process: [subprocess.Popen, None] = None

        self.task_done_trigger_function: typing.Callable = task_done_trigger_function
        self.error_trigger_function: typing.Callable = error_trigger_function
        self.program_buffer_size = program_buffer_size

    def start_test_process(self, package: str, exec_str: str):
        # try to find file and compiler
        if sys.platform in ["win32", "cygwin", "msys"]:
            venv_path = Path(os.getcwd() + "/venv/Scripts")
        else:
            venv_path = Path(os.getcwd() + "/venv/bin")
        if venv_path.is_dir() and venv_path.exists():
            compiler_path = shutil.which(
                cmd="python3",
                path=str(venv_path)
            )
        else:
            compiler_path = shutil.which(cmd="python3")
        if compiler_path is None:
            if sys.platform in ["win32", "cygwin", "msys"]:
                venv_path = Path(os.getcwd() + "/venv/Scripts")
            else:
                venv_path = Path(os.getcwd() + "/venv/bin")
            if venv_path.is_dir() and venv_path.exists():
                compiler_path = shutil.which(
                    cmd="python",
                    path=str(venv_path)
                )
            else:
                compiler_path = shutil.which(cmd="python")
        if compiler_path is None:
            raise ITEExecException(compiler_not_found_error)
        self.process = subprocess.Popen(
            [
                compiler_path,
                "-m",
                package,
                "--execute_str",
                exec_str
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )
        self.still_run_program = True
        # program output message queue thread
        self.read_program_output_from_thread = Thread(
            target=self.read_program_output_from_process,
            daemon=True
        )
        self.read_program_output_from_thread.start()
        # program error message queue thread
        self.read_program_error_output_from_thread = Thread(
            target=self.read_program_error_output_from_process,
            daemon=True
        )
        self.read_program_error_output_from_thread.start()
        # start Pyside update
        # start timer
        self.main_window.setWindowTitle(package)
        self.main_window.show()
        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.pull_text)
        self.timer.start()

    # Pyside UI update method
    def pull_text(self):
        try:
            self.main_window.code_result.setTextColor(actually_color_dict.get("normal_output_color"))
            if not self.run_output_queue.empty():
                output_message = self.run_output_queue.get_nowait()
                output_message = str(output_message).strip()
                if output_message:
                    self.main_window.code_result.append(output_message)
            self.main_window.code_result.setTextColor(actually_color_dict.get("error_output_color"))
            if not self.run_error_queue.empty():
                error_message = self.run_error_queue.get_nowait()
                error_message = str(error_message).strip()
                if error_message:
                    self.main_window.code_result.append(error_message)
            self.main_window.code_result.setTextColor(actually_color_dict.get("normal_output_color"))
        except queue.Empty:
            pass
        if self.process is not None:
            if self.process.returncode == 0:
                if self.timer.isActive():
                    self.timer.stop()
                self.exit_program()
            elif self.process.returncode is not None:
                if self.timer.isActive():
                    self.timer.stop()
                self.exit_program()
            if self.still_run_program:
                # poll return code
                self.process.poll()
        else:
            if self.timer.isActive():
                self.timer.stop()

    # exit program change run flag to false and clean read thread and queue and process
    def exit_program(self):
        self.still_run_program = False
        if self.read_program_output_from_thread is not None:
            self.read_program_output_from_thread = None
        if self.read_program_error_output_from_thread is not None:
            self.read_program_error_output_from_thread = None
        self.print_and_clear_queue()
        if self.process is not None:
            self.process.terminate()
            self.main_window.code_result.append(f"Task exit with code {self.process.returncode}")
            self.process = None

    def print_and_clear_queue(self):
        self.run_output_queue = queue.Queue()
        self.run_error_queue = queue.Queue()

    def read_program_output_from_process(self):
        while self.still_run_program:
            program_output_data = self.process.stdout.raw.read(self.program_buffer_size).decode(self.program_encoding)
            if program_output_data.strip() != "":
                self.run_output_queue.put(program_output_data)

    def read_program_error_output_from_process(self):
        while self.still_run_program:
            program_error_output_data = self.process.stderr.raw.read(self.program_buffer_size).decode(
                self.program_encoding)
            if program_error_output_data.strip() != "":
                self.run_error_queue.put(program_error_output_data)
