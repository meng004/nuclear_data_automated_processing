from pathlib import Path

from utils import configlib
from utils.physical_quantity_list_generator import physical_quantity_list_generator


class InputXmlFile:
    chosen_physical_quantity: list
    length_of_physical_quantity: dict

    def __init__(self, file_path, physical_quantity_name='all'):
        """
        可以根据输入的文件路径和物理量自动计算得出选择的物理量chosen_physical_quantity和物理量对应的行号范围length_of_physical_quantity
        :param file_path: 文件路径
        :param physical_quantity_name: 物理量对应的名字，默认为all
        """
        self.path = Path(file_path)
        self.name = Path(file_path).name
        self.chosen_physical_quantity = physical_quantity_list_generator(physical_quantity_name)
        self.length_of_physical_quantity = self.get_length_of_physical_quantity()
        self.unfetched_physical_quantity = self.get_unfetched_physical_quantity()

    def set_chosen_physical_quantity(self, physical_quantity_name):
        """
        输入选择的物理量，设置类的属性chosen_physical_quantity和length_of_physical_quantity
        :param physical_quantity_name: 物理量对应的名字
        :return: None
        """
        self.chosen_physical_quantity = physical_quantity_list_generator(physical_quantity_name)
        self.length_of_physical_quantity = self.get_length_of_physical_quantity()

    def get_length_of_physical_quantity(self, physical_quantity_name=None):
        """
        获取对应物理量的行号范围，physical_quantity_name默认为None,设置则输出physical_quantity_name对应的行号的字典
        但是此只是临时返回一个物理量及行号范围的字典，不修改类的属性self.chosen_physical_quantity和self.length_of_physical_quantity
        :param physical_quantity_name: 物理量对应的名字
        :return: 返回一个物理量及行号范围的字典
        """
        chosen_physical_quantity = self.chosen_physical_quantity
        if physical_quantity_name:
            chosen_physical_quantity = physical_quantity_list_generator(physical_quantity_name)
        else:
            if len(chosen_physical_quantity) == 6:
                physical_quantity_name = 'all'
            else:
                physical_quantity_name = chosen_physical_quantity[0]

        list_of_strings_to_search = configlib.Config.get_data_extraction_conf("keys_of_rows").get(
            physical_quantity_name)

        index_start = list_of_strings_to_search[:-1]
        index_end = list_of_strings_to_search[-1]

        length_of_physical_quantity = {key: [] for key in chosen_physical_quantity}

        i = -1
        is_find_start_title = False

        for row_number, line in enumerate(self.path.open(encoding='UTF-8')):
            if not is_find_start_title:
                for string_to_search in index_start:
                    if string_to_search in line:
                        i += 1
                        is_find_start_title = True
                        length_of_physical_quantity[chosen_physical_quantity[i]].append(
                            row_number + 7 if chosen_physical_quantity[i] != 'gamma_spectra' else row_number + 2)

            if is_find_start_title:
                if index_end in line:
                    is_find_start_title = False
                    length_of_physical_quantity[chosen_physical_quantity[i]].append(
                        row_number - 3 if chosen_physical_quantity[i] != 'gamma_spectra' else row_number - 2)
                    if physical_quantity_name != 'all':
                        break

        return length_of_physical_quantity

    def get_unfetched_physical_quantity(self):
        unfetched_physical_quantity = [name for name in self.chosen_physical_quantity
                                       if not self.length_of_physical_quantity.get(name)]
        return unfetched_physical_quantity
