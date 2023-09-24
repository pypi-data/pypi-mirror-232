from typing import List
import json

class option:
    def __init__(self, value, label: str) -> None:
        self.value = value
        self.label = label


class select:
    def __init__(self, options: List[option] = []):
        self.options = options

    def __str__(self) -> str:
        return json.dumps(self.get_show_options())

    def get_show_options(self) -> str:
        ret = []
        index = 0
        for option in self.options:
            ret.append({
                "value": index,
                "label": option.label
            })
            index += 1
        return ret

    def get_option_value(self, index):
        return self.options[index].value

    def add_option(self, opt, label = None):
        if isinstance(opt, option):
            self.options.append(opt)
        else:
            self.options.append(option(opt, label or opt))

    def remove_option(self, value):
        length = len(self.options)
        for i in range(length):
            if (self.options[i].value == value):
                self.options.pop(i)
                return


class mselect:
    def __init__(self, options: List[option] = []):
        self.options = options
    
    def __str__(self) -> str:
        return json.dumps(self.get_show_options())

    def get_show_options(self) -> str:
        ret = []
        index = 0
        for option in self.options:
            ret.append({
                "value": index,
                "label": option.label
            })
            index += 1
        return ret

    def get_option_value(self, indexs):
        ret = []
        for index in indexs:
            ret.append(self.options[index].value)
        return ret

    def add_option(self, opt, label = None):
        if isinstance(opt, option):
            self.options.append(opt)
        else:
            self.options.append(option(opt, label or opt))

    def remove_option(self, value):
        length = len(self.options)
        for i in range(length):
            if (self.options[i].value == value):
                self.options.pop(i)
                return
