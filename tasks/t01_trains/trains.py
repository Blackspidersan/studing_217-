import sys


def heap_push(
    heap: list, item
) -> (
    None
):  # название параметра: тип-аннотация параметров(необязательно для работы кода)

    heap.append(item)
    idx = len(heap) - 1
    while idx > 0:
        parent = (idx - 1) // 2  # индекс родительского элемента
        if heap[idx] < heap[parent]:
            heap[idx], heap[parent] = heap[parent], heap[idx]
            idx = parent
        else:
            break


def heap_pop(heap):
    # Извлекает и возвращает минимальный элемент
    if len(heap) == 1:
        return heap.pop()

    top = heap[0]
    heap[0] = heap.pop()
    idx = 0
    size = len(heap)

    while True:
        left = 2 * idx + 1
        right = 2 * idx + 2
        smallest = idx

        if left < size and heap[left] < heap[smallest]:
            smallest = left
        if right < size and heap[right] < heap[smallest]:
            smallest = right

        if smallest != idx:
            heap[idx], heap[smallest] = heap[smallest], heap[idx]
            idx = smallest
        else:
            break

    return top


def parse_time(time_str: str, is_departure: bool = False) -> tuple[int, str]:
    # Разбирает и проверяет время формата ЧЧ:ММ
    parts = time_str.split(":")
    if len(parts) != 2:
        raise ValueError(f"Неверный формат времени '{time_str}'")

    h_str, m_str = parts[0], parts[1]
    if not (1 <= len(h_str) <= 2 and len(m_str) == 2):
        raise ValueError(f"Неверный формат времени '{time_str}'")
    if not (h_str.isdigit() and m_str.isdigit()):
        raise ValueError(f"Время должно состоять из цифр '{time_str}'")

    hours, minutes = int(h_str), int(m_str)

    if not (0 <= minutes <= 59):
        raise ValueError(f"Некорректные минуты в значении '{time_str}'")

    if hours == 24 and minutes == 0:
        if not is_departure:
            raise ValueError("Время прибытия не может быть 24:00")
    elif not (0 <= hours <= 23):
        raise ValueError(f"Некорректные часы в значении '{time_str}'")

    return hours * 60 + minutes, f"{hours:02d}:{minutes:02d}"


def parse_part(part: str, expected_keyword: str) -> str:
    # Извлекает время из фрагмента вида 'прибытие 09:00'
    tokens = part.split()
    if len(tokens) != 2 or tokens[0].lower() != expected_keyword:
        raise ValueError(
            f"Ожидалось '{expected_keyword} ЧЧ:ММ', получено '{part.strip()}'"
        )
    return tokens[1]


def parse_schedule(lines) -> list[dict]:
    # Читает и валидирует расписание без регулярных выражений
    trains = []

    for line_num, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        # Делим по первому двоеточию (название поезда двоеточий не содержит)
        if ":" not in line:
            raise ValueError(f"Строка {line_num}: отсутствует двоеточие -> '{line}'")

        name_part, rest = line.split(":", 1)
        name = name_part.strip()
        if not name:
            raise ValueError(f"Строка {line_num}: пустое название поезда")

        # Делим оставшуюся часть по запятой на прибытие и отправление
        times_parts = rest.split(",")
        if len(times_parts) != 2:
            raise ValueError(
                f"Строка {line_num}: неверный разделитель запятая -> '{line}'"
            )

        try:
            arr_str = parse_part(times_parts[0], "прибытие")
            dep_str = parse_part(times_parts[1], "отправление")
            arr_min, arr_fmt = parse_time(arr_str, is_departure=False)
            dep_min, dep_fmt = parse_time(dep_str, is_departure=True)
        except ValueError as err:
            raise ValueError(
                f"Строка {line_num}: {err}"
            ) from None  # frome None скрывает трассировку

        actual_dep_min = dep_min + (24 * 60 if dep_min < arr_min else 0)
        duration = actual_dep_min - arr_min  # длительность стоянки

        if duration == 0:
            raise ValueError(
                f"Строка {line_num} ({name}): стоянка не может быть нулевой"
            )
        if duration > 120:
            raise ValueError(
                f"Строка {line_num} ({name}): стоянка превышает 2 часа ({duration} мин)"
            )
