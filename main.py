from src.proxies import Proxies

import random
import time

from opencc import OpenCC

from tqdm    import tqdm
from pathlib import Path

class MyTranslator:

    def __init__(self):
        self.cc = OpenCC('s2twp')

    def do_translate(self , text : str) -> str:
        """
        Do translate from CN to TW
        
        :param cn_texts: Texts in CN
        :return: Texts in TW
        """
        return self.cc.convert(text)

    def tran2tw(self, file_full_path: str) -> list[str]:
        """
        Read srt file
        :param file_path: Path to the srt file
        :return: List of lines in the srt file
        """
        this_file = Path(file_full_path)
        new_file_path = this_file.parent / f"{this_file.stem}_tw.srt"
        all_text = this_file.read_text(encoding = "utf-8")
        new_text = ""
        for each_block in tqdm(all_text.split("\n\n")):
            cn_text = each_block.split("\n")[-1]
            tw_text = self.do_translate(cn_text)
            this_str = "\n".join(each_block.split("\n")[:-1]) + "\n" + tw_text + "\n\n"
            new_text += this_str
        new_file_path.write_text(new_text, encoding = "utf-8")
        print(f"Translated file saved to {new_file_path}")
        return new_text.split("\n\n")

if __name__ == "__main__":
    file_path = r"D:\video_output\4月3日.srt"
    MyTranslator().tran2tw(file_path)

