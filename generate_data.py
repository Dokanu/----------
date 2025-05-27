from db import Database
from data_generator import (
    generate_driving_categories,
    generate_districts,
    generate_car_brands,
    generate_ownership_types,
    generate_car_types,
    generate_instructors,
    generate_driving_schools,
    generate_courses,
    generate_streams,
    generate_student_groups,
    generate_provided_courses,
    generate_enrollments,
    generate_lessons,
    generate_reviews,
    generate_ordered_courses,
    generate_cars,
    generate_car_usage_stats,
    generate_active_courses,
)

DSN = "host=localhost dbname=kurs_bd user=postgres password=admin2005"
db = Database(DSN)

CAT_PHOTO_BYTES = (
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
    b'\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
    b'\x00\x00\x00\nIDATx\x9cc`\x00\x00\x00\x02\x00\x01'
    b'\xe2!\xbc\x33\x00\x00\x00\x00IEND\xaeB`\x82'
)

def insert_and_return_ids(table, data_list, columns, id_column="id"):
    ids = []
    for data in data_list:
        placeholders = ','.join(['%s'] * len(columns))
        cols = ','.join(columns)
        sql = f"INSERT INTO {table} ({cols}) VALUES ({placeholders}) RETURNING {id_column};"
        params = tuple(data[col] for col in columns)
        res = db.execute_returning(sql, params)
        ids.append(res[0])
    return ids


def insert_batch(table, rows, cols):
    sql = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join(['%s']*len(cols))})"
    for r in rows:
        params = [r[c] for c in cols]
        db.execute(sql, params)

def main():
    # Вставляем справочники и получаем id
    driving_categories = generate_driving_categories()
    driving_category_ids = insert_and_return_ids("driving_category", driving_categories, ["driving_category_name"], id_column="driving_category_id")

    districts = generate_districts()
    district_ids = insert_and_return_ids("district", districts, ["district_name"], id_column="district_id")

    car_brands = generate_car_brands()
    car_brand_ids = insert_and_return_ids("car_brand", car_brands, ["car_brand"], id_column="brand_id")

    ownerships = generate_ownership_types()
    ownership_type_ids = insert_and_return_ids("ownership_type", ownerships, ["ownership_type_name"], id_column="ownership_type_id")

    car_types = generate_car_types()
    car_type_ids = insert_and_return_ids("car_type", car_types, ["car_type_name"], id_column="car_type_id")

    # Получаем id студентов из базы (без вставки новых)
    student_ids = db.execute("SELECT student_id FROM student;")
    student_ids = [sid[0] for sid in student_ids]

    # Инструкторы (нужно использовать корректные driving_category_id)
    instructors_raw = generate_instructors(len(student_ids))
    instructors = []
    for instr in instructors_raw:
        instr["driving_category_id"] = driving_category_ids[instr["driving_category_id"] % len(driving_category_ids)]
        instructors.append(instr)
    instructor_ids = insert_and_return_ids("instructor", instructors, ["instructor_fullname", "driving_category_id"], id_column="instructor_id")

    # Автошколы — district_id и ownership_type_id
    schools_raw = generate_driving_schools(len(student_ids))
    schools = []
    for school in schools_raw:
        school["district_id"] = district_ids[school["district_id"] % len(district_ids)]
        school["ownership_type_id"] = ownership_type_ids[school["ownership_type_id"] % len(ownership_type_ids)]
        schools.append(school)
    driving_school_ids = insert_and_return_ids("driving_school", schools, [
        "driving_school_name", "district_id", "ownership_type_id", "driving_school_adress", "driving_school_url"
    ], id_column="driving_school_id")

    # Курсы - связываем с driving_category_id, instructor_id и driving_school_id
    courses_raw = generate_courses(len(student_ids))
    courses = []
    for course in courses_raw:
        course["driving_category_id"] = driving_category_ids[course["driving_category_id"] % len(driving_category_ids)]
        course["instructor_id"] = instructor_ids[course["instructor_id"] % len(instructor_ids)]
        course["driving_school_id"] = driving_school_ids[course["driving_school_id"] % len(driving_school_ids)]
        courses.append(course)
    course_ids = insert_and_return_ids("course", courses, [
        "course_duration_month", "course_price", "driving_hours",
        "driving_category_id", "instructor_id", "driving_school_id"
    ], id_column="course_id")

    # Потоки
    streams = generate_streams(len(student_ids))
    stream_ids = insert_and_return_ids("stream", streams, ["stream_name", "start_stream_date", "end_stream_date"], id_column="stream_id")

    # Группы студентов — привязать к course_id и stream_id
    groups_raw = generate_student_groups(len(student_ids))
    groups = []
    for group in groups_raw:
        group["course_id"] = course_ids[group["course_id"] % len(course_ids)]
        group["stream_id"] = stream_ids[group["stream_id"] % len(stream_ids)]
        groups.append(group)
    group_ids = insert_and_return_ids("student_group", groups, ["course_id", "stream_id"], id_column="student_group_id")

    # Предоставленные курсы — course_id и instructor_id
    provided_raw = generate_provided_courses(len(student_ids))
    provided = []
    for p in provided_raw:
        p["course_id"] = course_ids[p["course_id"] % len(course_ids)]
        p["instructor_id"] = instructor_ids[p["instructor_id"] % len(instructor_ids)]
        provided.append(p)
    provided_course_ids = insert_and_return_ids("provided_course", provided, ["course_id", "instructor_id", "start_date", "end_date"], id_column="provided_course_id")

    # Записи на курсы — student_id, student_group_id
    enrolls_raw = generate_enrollments(len(student_ids))
    enrolls = []
    for e in enrolls_raw:
        e["student_id"] = student_ids[e["student_id"] % len(student_ids)]
        e["student_group_id"] = group_ids[e["student_group_id"] % len(group_ids)]
        enrolls.append(e)
    insert_batch("enrollment", enrolls, ["student_id", "student_group_id", "enrollment_date"])

    # Автомобили - привязка brand_id и car_type_id
    cars_raw = generate_cars(len(student_ids))
    cars = []
    for car in cars_raw:
        car["brand_id"] = car_brand_ids[car["brand_id"] % len(car_brand_ids)]
        car["car_type_id"] = car_type_ids[car["car_type_id"] % len(car_type_ids)]
        cars.append(car)
    car_ids = insert_and_return_ids("car", cars, ["brand_id", "car_type_id", "year_of_production", "year_of_exploitation", "fuel_cost"], id_column="car_id")

    # Использование автомобилей
    stats_raw = generate_car_usage_stats(len(student_ids))
    stats = []
    for stat in stats_raw:
        stat["car_id"] = car_ids[stat["car_id"] % len(car_ids)]
        stats.append(stat)
    insert_batch("car_usage_stats", stats, ["car_id", "total_lessons", "last_used"])

    # Занятия - course_id, instructor_id, student_id, car_id
    lessons_raw = generate_lessons(len(student_ids))
    lessons = []
    for lesson in lessons_raw:
        lesson["course_id"] = course_ids[lesson["course_id"] % len(course_ids)]
        lesson["instructor_id"] = instructor_ids[lesson["instructor_id"] % len(instructor_ids)]
        lesson["student_id"] = student_ids[lesson["student_id"] % len(student_ids)]
        lesson["car_id"] = car_ids[lesson["car_id"] % len(car_ids)]
        lessons.append(lesson)
    insert_batch("lesson", lessons, ["lesson_date", "course_id", "instructor_id", "student_id", "car_id"])

    # Отзывы - course_id
    reviews_raw = generate_reviews(len(student_ids))
    reviews = []
    for review in reviews_raw:
        review["course_id"] = course_ids[review["course_id"] % len(course_ids)]
        reviews.append(review)
    insert_batch("review", reviews, ["review_text", "rating", "course_id"])

    # Заказы курсов
    ordered_raw = generate_ordered_courses(len(student_ids))
    ordered = []
    for o in ordered_raw:
        o["student_id"] = student_ids[o["student_id"] % len(student_ids)]
        o["course_id"] = course_ids[o["course_id"] % len(course_ids)]
        ordered.append(o)
    insert_batch("ordered_course", ordered, ["student_id", "course_id", "order_date"])

    # Активные курсы — student_id, course_id
    active_courses_raw = generate_active_courses(len(student_ids))
    active_courses = []
    for ac in active_courses_raw:
        ac["student_id"] = student_ids[ac["student_id"] % len(student_ids)]
        ac["course_id"] = course_ids[ac["course_id"] % len(course_ids)]
        active_courses.append(ac)
    insert_batch("active_course", active_courses, ["student_id", "course_id", "start_date", "end_date"])

    print("Data inserted successfully!")

if __name__ == "__main__":
    main()
