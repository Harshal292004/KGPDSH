import datetime
from rich.console import Console 


class RichLogger:
    """
    Class for logging during development 
    
    Logs with time and color:
        - error 
        - warning 
        - info 
        - debug
        - success
    """
    def __init__(self):
        self.console = Console()

    def log_with_time(self,message: str, style: str = "cyan"):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.console.print(f"[{now}] {message}", style=style)

    def error(self, message: str):
        self.log_with_time(message=f"{message}",style="red")


    def warn(self, message: str):
        self.log_with_time(message=f"{message}",style="yellow")

    def info(self, message: str):
        self.log_with_time(message=f"{message}",style="blue")

    def debug(self, message: str):
        self.log_with_time(message=f"{message}",style="magenta")

    def success(self, message: str):
        self.log_with_time(message=f"{message}",style="green")