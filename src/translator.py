from opencc import OpenCC

from pathlib import Path
from tqdm    import tqdm

class MyTranslator:
    def __init__(self, mode : str = "s2twp"):
        self.cc = OpenCC(mode)

    def do_translate(self , text : str) -> str:
        """
        Do translate from CN to TW
        
        :param cn_texts: Texts in CN
        :return: Texts in TW
        """
        return self.cc.convert(text)
    
    def read_file(self, file_full_path: str) -> str:
        this_file = Path(file_full_path)
        all_text = this_file.read_text(encoding = "utf-8")
        return all_text

    def translate(self, content: str, show_progress : bool = True) -> str:
        """
        Read str
        :param content: str
        :return: List of lines in the srt file
        """
        new_text = ""
        if show_progress:
            tasks = tqdm(content.split("\n"), desc="Processing")
        else:
            tasks = content.split("\n")
        for each_line in tasks:
            new_text += self.do_translate(each_line) + "\n"
        return new_text
