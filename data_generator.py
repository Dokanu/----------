from faker import Faker
import random
from datetime import date, timedelta

fake = Faker('ru_RU')

DRIVING_CATEGORIES = ['A', 'B', 'C', 'D', 'E', 'M', 'T']
DISTRICTS_DONETSK = [
    'Ворошиловский', 'Киевский', 'Будённовский', 
    'Калининский', 'Петровский', 'Пролетарский', 'Тельмановский'
]
CAR_BRANDS = [
    'Toyota', 'Mercedes-Benz', 'BMW', 'Ford', 
    'Volkswagen', 'Hyundai', 'Nissan', 'Kia', 'Audi'
]
OWNERSHIP_TYPES = [
    'Индивидуальный предприниматель (ИП)', 
    'Общество с ограниченной ответственностью (ООО)', 
    'Некоммерческое образовательное учреждение (НОУ)', 
    'Потребительский кооператив (ПОЧУ)', 
    'Государственная автошкола'
]
CAR_TYPES = ['Легковой', 'Грузовой', 'Мотоцикл', 'Автобус']


def generate_driving_categories():
    return [{'driving_category_id': i + 1, 'driving_category_name': cat} 
            for i, cat in enumerate(DRIVING_CATEGORIES)]


def generate_districts():
    return [{'district_id': i + 1, 'district_name': name} 
            for i, name in enumerate(DISTRICTS_DONETSK)]


def generate_car_brands():
    return [{'brand_id': i + 1, 'car_brand': brand} 
            for i, brand in enumerate(CAR_BRANDS)]


def generate_ownership_types():
    return [{'ownership_type_id': i + 1, 'ownership_type_name': ot} 
            for i, ot in enumerate(OWNERSHIP_TYPES)]


def generate_car_types():
    return [{'car_type_id': i + 1, 'car_type_name': ct} 
            for i, ct in enumerate(CAR_TYPES)]


def generate_students(n=10):
    result = []
    for _ in range(n):
        result.append({
            'student_id': None,
            'full_name': fake.name(),
            'born_date': fake.date_between(start_date='-60y', end_date='-18y'),
            'social_status': random.choice(['Студент', 'Работающий', 'Пенсионер']),
            'work_or_studying_place': fake.company(),
            'phone': fake.phone_number(),
            'non_cash': random.choice([True, False])
        })
    return result


def generate_instructors(n=5):
    result = []
    for _ in range(n):
        result.append({
            'instructor_id': None,
            'instructor_fullname': fake.name(),
            'driving_category_id': random.randint(1, len(DRIVING_CATEGORIES))
        })
    return result


def generate_driving_schools(n=3):
    result = []
    for _ in range(n):
        result.append({
            'driving_school_id': None,
            'driving_school_name': fake.company(),
            'district_id': random.randint(1, len(DISTRICTS_DONETSK)),
            'ownership_type_id': random.randint(1, len(OWNERSHIP_TYPES)),
            'driving_school_address': fake.address(),
            'driving_school_url': fake.url()
        })
    return result


def generate_courses(n=10):
    result = []
    for _ in range(n):
        duration = random.randint(1, 12)  # месяцы
        price = round(random.uniform(10000, 50000), 2)
        result.append({
            'course_id': None,
            'course_duration_month': duration,
            'course_price': price,
            'driving_hours': random.randint(20, 100),
            'driving_category_id': random.randint(1, len(DRIVING_CATEGORIES)),
            'instructor_id': random.randint(1, 5),
            'driving_school_id': random.randint(1, 3)
        })
    return result


def generate_streams(n=3):
    today = date.today()
    result = []
    for i in range(n):
        start = today - timedelta(days=random.randint(0, 365))
        end = start + timedelta(days=random.randint(30, 180))
        result.append({
            'stream_id': None,
            'stream_name': f'Поток {i + 1}',
            'start_stream_date': start,
            'end_stream_date': end
        })
    return result


def generate_student_groups(n=10):
    result = []
    for _ in range(n):
        result.append({
            'student_group_id': None,
            'course_id': random.randint(1, 10),
            'stream_id': random.randint(1, 3)
        })
    return result


def generate_provided_courses(n=10):
    result = []
    today = date.today()
    for _ in range(n):
        start = today - timedelta(days=random.randint(0, 180))
        end = start + timedelta(days=random.randint(30, 90))
        result.append({
            'provided_course_id': None,
            'course_id': random.randint(1, 10),
            'instructor_id': random.randint(1, 5),
            'start_date': start,
            'end_date': end
        })
    return result


def generate_enrollments(n=20):
    result = []
    base_date = date.today() - timedelta(days=180)
    for _ in range(n):
        enroll = base_date + timedelta(days=random.randint(0, 180))
        result.append({
            'enrollment_id': None,
            'student_id': random.randint(1, 10),
            'student_group_id': random.randint(1, 10),
            'enrollment_date': enroll
        })
    return result


def generate_lessons(n=30):
    result = []
    base_date = date.today() - timedelta(days=90)
    for _ in range(n):
        ld = base_date + timedelta(days=random.randint(0, 90))
        result.append({
            'lesson_id': None,
            'lesson_date': ld,
            'course_id': random.randint(1, 10),
            'instructor_id': random.randint(1, 5),
            'student_id': random.randint(1, 10),
            'car_id': random.randint(1, 10)
        })
    return result


def generate_reviews(n=25):
    result = []
    for _ in range(n):
        rd = date.today() - timedelta(days=random.randint(0, 365))
        result.append({
            'review_id': None,
            'review_text': fake.sentence(),
            'reviewer_name': fake.name(),
            'grade': round(random.uniform(1, 5), 1),
            'review_date': rd,
            'course_id': random.randint(1, 10)
        })
    return result


def generate_ordered_courses(n=15):
    result = []
    base_date = date.today() - timedelta(days=120)
    for _ in range(n):
        start = base_date + timedelta(days=random.randint(0, 120))
        end = start + timedelta(days=random.randint(30, 60))
        result.append({
            'ordered_course_id': None,
            'student_count': random.randint(1, 30),
            'stream_id': random.randint(1, 3),
            'provided_course_id': random.randint(1, 10),
            'start_date': start,
            'end_date': end
        })
    return result


def generate_cars(n=10):
    result = []
    for _ in range(n):
        result.append({
            'car_id': None,
            'brand_id': random.randint(1, len(CAR_BRANDS)),
            'car_type_id': random.randint(1, len(CAR_TYPES)),
            'year_of_production': random.randint(2000, 2025),
            'year_of_exploitation': random.randint(1, 25),
            'fuel_cost': round(random.uniform(5, 15), 2)
        })
    return result


def generate_car_usage_stats(n=10):
    result = []
    for _ in range(n):
        last = date.today() - timedelta(days=random.randint(0, 200))
        result.append({
            'car_id': random.randint(1, 10),
            'total_lessons': random.randint(0, 200),
            'last_used': last
        })
    return result


def generate_active_courses(n=10):
    result = []
    for _ in range(n):
        start = date.today() - timedelta(days=random.randint(0, 100))
        end = start + timedelta(days=random.randint(30, 90))
        price = round(random.uniform(10000, 50000), 2)
        result.append({
            'course_id': random.randint(1, 10),
            'start_date': start,
            'end_date': end,
            'course_price': price
        })
    return result
