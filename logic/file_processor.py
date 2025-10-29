import json
import re
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from collections import defaultdict


class FileProcessor:
    @staticmethod
    def process_file(filepath):
        # Заглушка для обработки файла
        return f"Обработан {os.path.basename(filepath)} ({datetime.now().strftime('%H:%M:%S')})"

    @staticmethod
    def build_vm_template(scenario_path, xsd_path, output_dir=None):
        """
        Генерирует адаптивный Velocity шаблон из трех входных файлов
        Возвращает два файла: template_raw.vm (чистый шаблон) и template_generated.vm (с частичной подстановкой)
        """
        try:
            # Обработка пути для сохранения
            if output_dir is None or output_dir == "":
                output_dir = Path.cwd()
            else:
                output_dir = Path(output_dir)

            # Создаем директорию, если она не существует
            output_dir.mkdir(parents=True, exist_ok=True)

            # Загрузка и парсинг файлов
            scenario = FileProcessor._load_maybe_json(scenario_path)
            xsd_text = Path(xsd_path).read_text(encoding='utf-8')

            # Парсинг XSD структуры
            structure = FileProcessor._parse_xsd(xsd_text)
            if structure is None:
                raise RuntimeError("Не удалось распознать структуру из XSD. Проверьте файл схемы вида сведений.")

            # Генерация сырого VM шаблона
            raw_vm = FileProcessor._generate_raw_vm(structure, scenario)

            # Частичная подстановка значений
            filled_vm, replacements = FileProcessor._partially_render_vm(raw_vm, scenario, structure)

            # Сохранение результатов
            raw_output_path = output_dir / "template_raw.vm"
            filled_output_path = output_dir / "template_generated.vm"

            raw_output_path.write_text(raw_vm, encoding='utf-8')
            filled_output_path.write_text(filled_vm, encoding='utf-8')

            result_info = {
                'success': True,
                'raw_output_path': str(raw_output_path.resolve()),
                'filled_output_path': str(filled_output_path.resolve()),
                'output_dir': str(output_dir.resolve()),
                'root_element': structure.get('name', 'Неизвестно'),
                'replacements_count': len(replacements),
                'replacements_sample': dict(list(replacements.items())[:10]),  # первые 10 замен
                'structure_summary': FileProcessor._summarize_structure(structure)
            }
            return result_info

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def _load_maybe_json(path):
        """Загружает файл, пытаясь распарсить как JSON, иначе возвращает текст"""
        txt = Path(path).read_text(encoding='utf-8')
        try:
            return json.loads(txt)
        except Exception:
            # Попытки очистки (замена одинарных кавычек на двойные только если похоже на JSON)
            try:
                cleaned = txt.strip()
                # если начинается с { или [, попробуем исправить одинарные кавычки
                if cleaned.startswith("{") or cleaned.startswith("["):
                    cleaned2 = re.sub(r"'", '"', cleaned)
                    return json.loads(cleaned2)
            except Exception:
                pass
        # если не JSON — вернем текст
        return txt

    @staticmethod
    def _parse_xsd(xsd_text):
        try:
            root = ET.fromstring(xsd_text.encode('utf-8'))
        except Exception as e:
            # попытаемся найти начало тега <xs: or <xsd:
            m = re.search(r"<(xsd:|xs:)?schema", xsd_text)
            if m:
                idx = m.start()
                root = ET.fromstring(xsd_text[idx:].encode('utf-8'))
            else:
                raise

        # Сбор namespace map
        nsmap = {}
        for k, v in root.attrib.items():
            if k.startswith("xmlns:"):
                ns = k.split(":", 1)[1]
                nsmap[ns] = v

        # Стандартный XSD namespace
        XSD_NS = ''
        for prefix, uri in nsmap.items():
            if uri in ("http://www.w3.org/2001/XMLSchema", "http://www.w3.org/2001/XMLSchema-instance"):
                XSD_NS = uri
        if not XSD_NS:
            XSD_NS = "http://www.w3.org/2001/XMLSchema"

        ns = {'xsd': XSD_NS, 'xs': XSD_NS}

        # Находим элементы
        elements = root.findall('.//xsd:element', ns)

        # Находим корневой элемент
        root_element = None
        for el in elements:
            if el.get('name') and 'SetRequest' in el.get('name'):
                root_element = el
                break
        if root_element is None and elements:
            root_element = elements[0]

        # Собираем complex types
        complex_types = {ct.get('name'): ct for ct in root.findall('.//xsd:complexType', ns) if ct.get('name')}

        def parse_element(el):
            name = el.get('name')
            type_attr = el.get('type')
            max_occurs = el.get('maxOccurs') or '1'
            min_occurs = el.get('minOccurs') or '1'
            node = {
                'name': name,
                'type': type_attr,
                'minOccurs': min_occurs,
                'maxOccurs': max_occurs,
                'children': []
            }

            # Inline complexType?
            ct = el.find('xsd:complexType', ns) or el.find('xs:complexType', ns)
            if ct is not None:
                seq = ct.find('.//xsd:sequence', ns) or ct.find('.//xs:sequence', ns)
                if seq is not None:
                    for child in seq.findall('xsd:element', ns) + seq.findall('xs:element', ns):
                        node['children'].append(parse_element(child))
            elif type_attr and ':' in type_attr:
                # Тип, возможно complexType объявлен elsewhere
                tname = type_attr.split(':', 1)[1]
                if tname in complex_types:
                    ct = complex_types[tname]
                    seq = ct.find('.//xsd:sequence', ns) or ct.find('.//xs:sequence', ns)
                    if seq is not None:
                        for child in seq.findall('xsd:element', ns) + seq.findall('xs:element', ns):
                            node['children'].append(parse_element(child))
            return node

        structure = None
        if root_element is not None:
            structure = parse_element(root_element)
        return structure

    @staticmethod
    def _deep_search_for_key(obj, target_key):
        """Поиск значения по ключу (игнорируя регистр и подстроки). Возвращает первое найденное"""
        target = target_key.lower()
        if isinstance(obj, dict):
            # Прямые совпадения сначала
            for k, v in obj.items():
                if k.lower() == target:
                    return v
            for k, v in obj.items():
                if target in k.lower() or k.lower() in target:
                    # Если v простое, вернем его; иначе продолжаем глубже
                    if isinstance(v, (str, int, float, bool)):
                        return v
                    # Если список с простыми значениями, вернем первое простое
                    if isinstance(v, list) and v and isinstance(v[0], (str, int, float, bool)):
                        return v[0]
                    # Иначе рекурсия
                    found = FileProcessor._deep_search_for_key(v, target_key)
                    if found is not None:
                        return found
            # Рекурсия в детей
            for k, v in obj.items():
                found = FileProcessor._deep_search_for_key(v, target_key)
                if found is not None:
                    return found
        elif isinstance(obj, list):
            for item in obj:
                found = FileProcessor._deep_search_for_key(item, target_key)
                if found is not None:
                    return found
        return None

    @staticmethod
    def _to_camel_case(s):
        parts = re.split(r'[_\-\s\.]+', s)
        if not parts:
            return s
        return parts[0] + ''.join(p.title() for p in parts[1:])

    @staticmethod
    def _generate_vm_for_node(node, scenario, indent=2, list_name_overrides=None):
        if list_name_overrides is None:
            list_name_overrides = {}
        pad = " " * indent
        lines = []
        name = node['name']
        tag = name
        maxocc = node.get('maxOccurs', '1')
        children = node.get('children', [])

        if children:
            if maxocc == 'unbounded' or (maxocc.isdigit() and int(maxocc) > 1):
                # Список: создаем foreach
                list_var = None
                if isinstance(scenario, dict):
                    for k, v in scenario.items():
                        if isinstance(v, list):
                            if v and isinstance(v[0], dict):
                                item_keys = set(v[0].keys())
                                child_key_names = set(ch['name'] for ch in children)
                                if item_keys & child_key_names:
                                    list_var = k
                                    break
                if not list_var:
                    list_var = list_name_overrides.get(name, name + "List")
                item_var = name.rstrip('s') if name.endswith('s') else name + "Item"
                lines.append(f'{pad}#foreach(${item_var} in ${list_var})')
                lines.append(f'{pad}<{tag}>')
                for ch in children:
                    child_lines = FileProcessor._generate_vm_for_node_inner(ch, scenario, indent + 2, item_var,
                                                                            list_name_overrides)
                    lines.extend(child_lines)
                lines.append(f'{pad}</{tag}>')
                lines.append(f'{pad}#end')
            else:
                lines.append(f'{pad}<{tag}>')
                for ch in children:
                    lines.extend(FileProcessor._generate_vm_for_node(ch, scenario, indent + 2, list_name_overrides))
                lines.append(f'{pad}</{tag}>')
        else:
            # Простой элемент: пытаемся найти значение в сценарии
            found = FileProcessor._deep_search_for_key(scenario, name)
            varname = FileProcessor._to_camel_case(name)
            if found is not None and isinstance(found, (str, int, float, bool)):
                val = str(found).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                lines.append(f'{pad}<{tag}>{val}</{tag}>')
            else:
                lines.append(f'{pad}<{tag}>${varname}</{tag}>')
        return lines

    @staticmethod
    def _generate_vm_for_node_inner(node, scenario, indent, item_var, list_name_overrides=None):
        pad = " " * indent
        lines = []
        name = node['name']
        children = node.get('children', [])
        tag = name

        if children:
            lines.append(f'{pad}<{tag}>')
            for ch in children:
                lines.extend(
                    FileProcessor._generate_vm_for_node_inner(ch, scenario, indent + 2, item_var, list_name_overrides))
            lines.append(f'{pad}</{tag}>')
        else:
            # Простой элемент внутри foreach
            found = None
            if isinstance(scenario, dict):
                for k, v in scenario.items():
                    if isinstance(v, list) and v and isinstance(v[0], dict) and name in v[0]:
                        val = v[0].get(name)
                        if isinstance(val, (str, int, float, bool)):
                            found = val
                            break
            if found is not None:
                val = str(found).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                lines.append(f'{pad}<{tag}>{val}</{tag}>')
            else:
                lines.append(f'{pad}<{tag}>${{{item_var}.{name}}}</{tag}>')
        return lines

    @staticmethod
    def _generate_raw_vm(structure, scenario):
        lines = []
        lines.append('<?xml version="1.0" encoding="UTF-8"?>')
        lines.append('<!-- Adaptive generated Velocity template -->')
        lines.append('<soc:AppDataRequest xmlns:xml="http://www.w3.org/XML/1998/namespace"')
        lines.append('    xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soc="http://socit.ru/kalin/orders/2.0.0"')
        lines.append('    xmlns:soc1="http://socit.ru/kalin/orders/2.0.0/attachments">')
        lines.append('  <soc:SetRequest>')

        if structure.get('children'):
            for child in structure['children']:
                lines.extend(FileProcessor._generate_vm_for_node(child, scenario, indent=4))
        else:
            lines.extend(FileProcessor._generate_vm_for_node(structure, scenario, indent=4))

        lines.append('  </soc:SetRequest>')
        lines.append('</soc:AppDataRequest>')

        return "\n".join(lines)

    @staticmethod
    def _collect_placeholders(vm_text):
        ph = set(re.findall(r"\$\{?([A-Za-z0-9_\.]+)\}?", vm_text))
        # Удаляем числовые и общие VM ключевые слова
        ph = {p for p in ph if p.lower() not in ('foreach', 'end', 'if', 'else', 'set') and not p.isdigit()}
        return ph

    @staticmethod
    def _partially_render_vm(raw_vm, scenario, structure):
        placeholders = FileProcessor._collect_placeholders(raw_vm)
        filled_vm = raw_vmF
        replacements = {}

        # Создаем карту путей для более точного поиска
        def build_value_map(obj, prefix="", result=None):
            if result is None:
                result = {}
            if isinstance(obj, dict):
                for k, v in obj.items():
                    full_key = f"{prefix}.{k}" if prefix else k
                    if isinstance(v, (dict, list)):
                        build_value_map(v, full_key, result)
                    else:
                        result[full_key.lower()] = v
                        # Также добавляем вариант без префикса для простых случаев
                        result[k.lower()] = v
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    if isinstance(item, (dict, list)):
                        build_value_map(item, f"{prefix}[{i}]", result)
                    else:
                        list_key = f"{prefix}.{i}" if prefix else str(i)
                        result[list_key.lower()] = item
            return result

        value_map = build_value_map(scenario)

        for ph in placeholders:
            # Обрабатываем разные форматы переменных
            clean_ph = ph.replace('{', '').replace('}', '')

            # Для переменных вида item.field ищем в value_map
            if '.' in clean_ph:
                # Это переменная внутри объекта или цикла
                parts = clean_ph.split('.')
                search_key = parts[-1].lower()  # берем последнюю часть

                # Пробуем найти значение по полному пути и по последнему ключу
                val = value_map.get(clean_ph.lower()) or value_map.get(search_key)
            else:
                # Простая переменная
                search_key = clean_ph.lower()
                val = value_map.get(search_key)

            # Дополнительный поиск по структуре, если в сценарии не найдено
            if val is None and isinstance(structure, dict):
                # Ищем в структуре значения по умолчанию или примеры
                structure_vals = FileProcessor._extract_structure_values(structure)
                val = structure_vals.get(search_key)

            if val is not None and isinstance(val, (str, int, float, bool)):
                sval = str(val).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                # Заменяем ${ph} и $ph
                filled_vm = re.sub(r"\$\{" + re.escape(ph) + r"\}", sval, filled_vm)
                filled_vm = re.sub(r"(?<![\w\$])\$" + re.escape(ph) + r"(?![\w\.])", sval, filled_vm)
                replacements[ph] = sval

        return filled_vm, replacements

    @staticmethod
    def _extract_structure_values(structure):
        """Извлекает возможные значения из структуры (имена полей и т.д.)"""
        values = {}

        def extract_from_node(node, path=""):
            name = node.get('name', '')
            if name:
                full_path = f"{path}.{name}" if path else name
                values[name.lower()] = name  # используем имя поля как значение по умолчанию
                values[full_path.lower()] = name

            for child in node.get('children', []):
                extract_from_node(child, f"{path}.{name}" if path else name)

        if structure:
            extract_from_node(structure)

        return values

    @staticmethod
    def _summarize_structure(structure, level=0):
        """Создает текстовое описание структуры"""
        if not structure:
            return "Пустая структура"

        name = structure.get('name', 'Без имени')
        children = structure.get('children', [])
        max_occurs = structure.get('maxOccurs', '1')

        summary = []
        indent = "  " * level
        node_type = "список" if max_occurs == 'unbounded' or (
                    max_occurs.isdigit() and int(max_occurs) > 1) else "элемент"
        summary.append(f"{indent}{name} ({node_type})")

        for child in children:
            summary.append(FileProcessor._summarize_structure(child, level + 1))

        return "\n".join(summary)