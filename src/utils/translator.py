from abc import ABC, abstractmethod
from pathlib import Path
import time

from googletrans import Translator
from deep_translator import GoogleTranslator, PonsTranslator
from opencc import OpenCC
from tqdm import tqdm
import asyncio

class MyTranslateBase(ABC):
    @abstractmethod
    def do_translate(self, text : str) -> str:
        ...


class MyTranslator(MyTranslateBase):
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


class MyTranslator2(MyTranslateBase):
    def __init__(self, dest : str, source = "auto") -> None:
        self.dest = dest
        self.source = source
        self.max_length : int = 1500

        self._translator_api_list = [
            GoogleTranslator(source=source, target= dest,),
            Translator(),
        ]

    def get_plain_text_list_from_str(self, text) -> list[str]:
        text_splited : list[str]     = text.split("\n")
        this_index  : int            = 0
        srt_index   : int            = 1
        output_word_list : list[str] = []
        while this_index < len(text_splited):
            if text_splited[this_index] == f"{srt_index}":
                srt_index  += 1
                this_index += 2 # skip time line
            else:
                if text_splited[this_index] != "":
                    output_word_list.append(text_splited[this_index])
                this_index += 1
        return output_word_list

    def insert_back2text(self, text, translated_str) -> list[str]:
        text_splited     : list[str] = text.split("\n")
        tran_splited     : list[str] = translated_str.split("\n")
        this_index       : int       = 0
        tran_index       : int       = 0
        srt_index        : int       = 1

        while this_index < len(text_splited) and tran_index < len(tran_splited):
            if text_splited[this_index] == f"{srt_index}":
                srt_index  += 1
                this_index += 2 # skip time line
            else:
                if text_splited[this_index] != "":
                    text_splited[this_index] = tran_splited[tran_index]
                    tran_index += 1
                this_index += 1
        return "\n".join(text_splited)

    def _translate_each(self, text : str, index = 0) -> str:
        try:
            return self._translator_api_list[index].translate(text)
        except Exception as e:
            # print(e)
            # print(f"Google translated fail, use another api")
            try:
                loop = asyncio.get_event_loop()
            except:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            return loop.run_until_complete(self._translat_with_googletrans(text, index))

    async def _translat_with_googletrans(self, text, index : int):
        result = await self._translator_api_list[index+1].translate(text = text, dest = self.dest.lower(), src = self.source.lower())
        return result.text

       # return "\n".join(["test" for _ in range(text.count("\n") + 2)])

    def cut_block(self, text : list[str]) -> list[str]:
        total_text = "\n".join(text)
        if len(total_text) < self.max_length:
            return [total_text,]

        output : list[str] = []
        temp_text = ""
        for each in text:
            if (len(temp_text) + len(each)) < self.max_length:
                temp_text = temp_text + each + "\n"
            else:
                output.append(temp_text.strip())
                temp_text = ""
        return output

    def translate_block(self, block_text_list : str) -> str:
        translated_str : str = ""
        for each in tqdm(block_text_list):
            this_result = self._translate_each(each)
            print(this_result)
            time.sleep(3)
            translated_str = translated_str + this_result + "\n"
        return translated_str.strip()

    def do_translate(self, text: str) -> str:
        text = text.strip()
        # block_text_list : list[str] = self.cut_block(text.split("\n"))
        # translated_str : str = ""
        #
        # for each in tqdm(block_text_list):
        #     this_result = self._translate_each(each)
        #     time.sleep( random.random() * 2.5 + 0.5)
        #     translated_str = translated_str + this_result + "\n"
        #
        # return translated_str

        plain_text_list : list[str] = self.get_plain_text_list_from_str(text)
        block_text_list : list[str] = self.cut_block(plain_text_list)
        return self.insert_back2text(text, self.translate_block(block_text_list))

class MyTranslator3:
    def __init__(self, source : str, dest : str) -> None:
        if source == "zh-TW" and dest =='en':
            self.t1 = MyTranslator(mode = "tw2s")
            self.t2 = MyTranslator2(source='zh-CN', dest = 'en')
        if dest == "zh-TW" and source == 'en':
            self.t1 = MyTranslator2(source='en', dest = 'zh-CN')
            self.t2 = MyTranslator(mode = "s2twp")

    def do_translate(self, text):
        return self.t2.do_translate(self.t1.do_translate(text))



