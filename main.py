import math
import logging
from datetime import datetime
from typing import List, Tuple, Union

# Настройка логирования
def setup_logging():
    # Создаем логгер
    logger = logging.getLogger('TriangleLogger')
    logger.setLevel(logging.INFO)
    
    # Формат логирования
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Логирование в файл
    file_handler = logging.FileHandler('triangle_requests.log', encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Логирование в консоль
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()

class TriangleCalculator:
    @staticmethod
    def parse_input(side_a: str, side_b: str, side_c: str) -> Union[Tuple[float, float, float], None]:
        """Парсинг входных строк в числа float"""
        try:
            a = float(side_a)
            b = float(side_b)
            c = float(side_c)
            
            # Проверка на положительные числа
            if a <= 0 or b <= 0 or c <= 0:
                return None
            return (a, b, c)
        except ValueError:
            return None
    
    @staticmethod
    def get_triangle_type(a: float, b: float, c: float) -> str:
        """Определение типа треугольника"""
        # Проверка неравенства треугольника
        if a + b <= c or a + c <= b or b + c <= a:
            return "не треугольник"
        
        # Проверка на равенство сторон
        if math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9) and \
           math.isclose(b, c, rel_tol=1e-9, abs_tol=1e-9):
            return "равносторонний"
        elif math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9) or \
             math.isclose(b, c, rel_tol=1e-9, abs_tol=1e-9) or \
             math.isclose(a, c, rel_tol=1e-9, abs_tol=1e-9):
            return "равнобедренный"
        else:
            return "разносторонний"
    
    @staticmethod
    def calculate_vertices(a: float, b: float, c: float) -> List[Tuple[int, int]]:
        """
        Вычисление координат вершин треугольника для отображения в поле 100x100 px
        Вершина A размещается в точке (0, 0)
        Вершина B размещается на оси X в точке (c, 0)
        Вершина C вычисляется по формулам координат из длин сторон
        """
        # Проверка существования треугольника
        if a + b <= c or a + c <= b or b + c <= a:
            return [(-1, -1), (-1, -1), (-1, -1)]
        
        # Размещаем вершины
        # Вершина A в начале координат
        x_a, y_a = 0.0, 0.0
        
        # Вершина B на оси X на расстоянии c от A
        x_b, y_b = c, 0.0
        
        # Вычисляем координаты вершины C
        # Используем формулу: 
        # x_c = (b^2 + c^2 - a^2) / (2c)
        # y_c = sqrt(b^2 - x_c^2)
        
        if abs(c) < 1e-9:
            return [(-1, -1), (-1, -1), (-1, -1)]
            
        x_c = (b**2 + c**2 - a**2) / (2 * c)
        y_c = math.sqrt(abs(b**2 - x_c**2))
        
        # Масштабирование в поле 100x100 px
        # Находим минимальные и максимальные координаты
        xs = [x_a, x_b, x_c]
        ys = [y_a, y_b, y_c]
        
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        # Избегаем деления на ноль
        if math.isclose(max_x - min_x, 0, rel_tol=1e-9, abs_tol=1e-9):
            range_x = 1
        else:
            range_x = max_x - min_x
            
        if math.isclose(max_y - min_y, 0, rel_tol=1e-9, abs_tol=1e-9):
            range_y = 1
        else:
            range_y = max_y - min_y
        
        # Масштабирование с отступами (10px от каждого края)
        margin = 10
        scale_x = (100 - 2 * margin) / range_x
        scale_y = (100 - 2 * margin) / range_y
        
        # Функция масштабирования
        def scale(x, y):
            # Сдвигаем так, чтобы min координаты попали в margin
            scaled_x = margin + (x - min_x) * scale_x
            scaled_y = 100 - margin - (y - min_y) * scale_y  # Инвертируем Y для экранных координат
            return (int(round(scaled_x)), int(round(scaled_y)))
        
        # Получаем масштабированные координаты
        vertices = [scale(x_a, y_a), scale(x_b, y_b), scale(x_c, y_c)]
        
        # Дополнительная проверка на выход за пределы [0, 100]
        for i, (vx, vy) in enumerate(vertices):
            vertices[i] = (max(0, min(100, vx)), max(0, min(100, vy)))
        
        return vertices
    
    @staticmethod
    def process_request(side_a: str, side_b: str, side_c: str) -> Tuple[str, List[Tuple[int, int]]]:
        """Обработка запроса"""
        # Парсинг входных данных
        parsed = TriangleCalculator.parse_input(side_a, side_b, side_c)
        
        if parsed is None:
            # Нечисловые данные
            logger.error(f"Невалидные данные: a='{side_a}', b='{side_b}', c='{side_c}' - нечисловые значения")
            return "", [(-2, -2), (-2, -2), (-2, -2)]
        
        a, b, c = parsed
        
        # Определение типа треугольника
        triangle_type = TriangleCalculator.get_triangle_type(a, b, c)
        
        # Вычисление координат
        if triangle_type == "не треугольник":
            vertices = [(-1, -1), (-1, -1), (-1, -1)]
            logger.warning(f"Неуспешный запрос: a={a}, b={b}, c={c} - {triangle_type}")
        else:
            vertices = TriangleCalculator.calculate_vertices(a, b, c)
            # Логирование успешного запроса
            logger.info(f"Успешный запрос: a={a}, b={b}, c={c}, тип={triangle_type}, вершины={vertices}")
        
        return triangle_type, vertices

def main():
    """Основная функция для демонстрации работы"""
    print("=== Калькулятор треугольника ===")
    print("Введите длины сторон треугольника (вещественные положительные числа)")
    print("Для выхода введите 'exit'")
    
    while True:
        print("\n" + "="*50)
        
        side_a = input("Сторона A: ").strip()
        if side_a.lower() == 'exit':
            break
            
        side_b = input("Сторона B: ").strip()
        if side_b.lower() == 'exit':
            break
            
        side_c = input("Сторона C: ").strip()
        if side_c.lower() == 'exit':
            break
        
        triangle_type, vertices = TriangleCalculator.process_request(side_a, side_b, side_c)
        
        print(f"\nРезультат:")
        print(f"Тип треугольника: {triangle_type if triangle_type else 'невалидные данные'}")
        print(f"Координаты вершин: {vertices}")

# Пример использования для тестирования
def run_tests():
    """Функция для тестирования различных сценариев"""
    test_cases = [
        # Успешные случаи
        ("5", "5", "5"),      # Равносторонний
        ("5", "5", "7"),      # Равнобедренный
        ("3", "4", "5"),      # Прямоугольный (разносторонний)
        ("6", "8", "10"),     # Прямоугольный (разносторонний)
        
        # Неуспешные случаи
        ("1", "2", "3"),      # Не треугольник (вырожденный)
        ("1", "1", "3"),      # Не треугольник
        ("abc", "4", "5"),    # Нечисловые данные
        ("-3", "4", "5"),     # Отрицательные числа
        ("0", "4", "5"),      # Нулевая сторона
        ("", "4", "5"),       # Пустая строка
        ("3.5", "4.2", "5.8") # Разносторонний
    ]
    
    print("=== Запуск тестов ===\n")
    for i, (a, b, c) in enumerate(test_cases, 1):
        print(f"Тест {i}: a={a}, b={b}, c={c}")
        triangle_type, vertices = TriangleCalculator.process_request(a, b, c)
        print(f"Результат: тип='{triangle_type}', вершины={vertices}\n")

if __name__ == "__main__":
    # Раскомментируйте для запуска тестов:
    # run_tests()
    
    # Запуск интерактивного режима:
    main()