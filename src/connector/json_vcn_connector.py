import json
import os.path

from src import Parser, Vacancy
from src.connector.basic_vcn_connector import BasicVacancyConnector


class JSONVacancyConnector(BasicVacancyConnector):
    __file_worker: str
    __parser: Parser

    def __init__(self, file_worker):
        if not os.path.isfile(file_worker):
            raise FileNotFoundError

        self.__file_worker = file_worker
        self.__parser = Parser(file_worker)

    @property
    def vacancy_count(self) -> int:
        vacancies_obj_list = self.__parser.parse_json()
        return len(vacancies_obj_list)

    def add_vacancy(self, new_vacancy: Vacancy) -> bool:
        """
        добавляет вакансию в JSON-файл
        :param new_vacancy: новая вакансия Vacancy
        :return: True - успешное добавление
        """

        # получение списка объектов вакансий из JSON-файла
        vacancies_obj_list = self.__parser.parse_json()

        # новая вакансия как объект списка объектов вакансий JSON файла
        new_vacancy_json_obj = {
            'id': new_vacancy.id,
            'name': new_vacancy.name,
            'alternate_url': new_vacancy.url,
            'area': {'name': new_vacancy.area},
            'snippet': {'requirement': new_vacancy.requirement},
            'salary': {
                'from': new_vacancy.salary_numeric_value_from,
                'to': new_vacancy.salary_numeric_value_to,
                'currency': new_vacancy.salary_currency
            }
        }

        # сохранение новой вакансии в JSON-файл
        vacancies_obj_list.append(new_vacancy_json_obj)
        json_data = json.dumps({'items': vacancies_obj_list})
        with open(self.__file_worker, 'w') as file:
            file.write(json_data)
        return True

    def delete_vacancy(self, deleted_vacancy_id: int = None) -> bool:
        """
        удаляет вакансию в JSON-файле
        :param deleted_vacancy_id: id удаляемой вакансии
        :return: True - успешное удаление
        """

        # получение списка объектов вакансий из JSON-файла
        vcn_obj_list = self.__parser.parse_json()

        if not deleted_vacancy_id:
            # если не указан удаляемый элемент, удаляется последний
            found_index = len(vcn_obj_list) - 1
        else:
            # поиск удаляемого элемента по уникальному id (первое совпадение)
            found_index = -1
            for i in range(len(vcn_obj_list)):
                if vcn_obj_list[i]['id'] == deleted_vacancy_id:
                    found_index = i
                    break

        # удаление элемента и перезапись JSON-файла
        if found_index > -1:
            vcn_obj_list.pop(found_index)
            json_data = json.dumps({'items': vcn_obj_list})
            with open(self.__file_worker, 'w') as file:
                file.write(json_data)
            return True
        return False

    def get_vacancies(self, params: dict = None) -> list:
        """
        получает вакансии из JSON-файла по заданным параметрам
        :param params: параметры вакансии
        :return: список объектов вакансий
        """

        # получение списка объектов вакансий из JSON-файла
        vacancies_obj_list = self.__parser.parse_json()
        vacancy_copy_list = self.__parser.parse_obj_to_vacancy_cls_copy(vacancies_obj_list)

        # получение списка объектов вакансий, полученных из списка вакансий класса Vacancy
        vacancies_obj_list = [el.get_props_dict() for el in vacancy_copy_list]

        # поиск вакансий в списке объектов вакансий
        found_vacancies_obj_list = []
        if params:
            for vcn in vacancies_obj_list:
                # флаг совпадения
                is_matching = True
                for par_key, par_value in params.items():
                    if par_key not in vcn:
                        # если такого параметра нет у объекта
                        return []

                    if vcn[par_key] != par_value:
                        # перебор свойств объекта
                        is_matching = False
                        break
                if is_matching:
                    found_vacancies_obj_list.append(vcn)
        else:
            for vcn in vacancies_obj_list:
                found_vacancies_obj_list.append(vcn)

        return found_vacancies_obj_list
