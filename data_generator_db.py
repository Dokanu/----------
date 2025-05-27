# data_generator_batch.py

from db import Database
from faker import Faker
import random
from datetime import date, timedelta
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor, as_completed

fake = Faker('ru_RU')

class BatchGenerator:
    def __init__(self, dsn):
        self.db = Database(dsn)

        # Preload reference IDs
        self.driving_category_ids = [r['driving_category_id']
            for r in self.db.fetch_all("SELECT driving_category_id FROM driving_category;")]
        self.driving_school_ids = [r['driving_school_id']
            for r in self.db.fetch_all("SELECT driving_school_id FROM driving_school;")]
        self.instructor_ids = [r['instructor_id']
            for r in self.db.fetch_all("SELECT instructor_id FROM instructor;")]
        self.course_ids = [r['course_id']
            for r in self.db.fetch_all("SELECT course_id FROM course;")]
        self.student_group_ids = [r['student_group_id']
            for r in self.db.fetch_all("SELECT student_group_id FROM student_group;")]

    # --- Courses ---

    def _insert_courses_chunk(self, chunk_size):
        inserted = 0
        attempts = 0
        max_attempts = chunk_size * 2
        while inserted < chunk_size and attempts < max_attempts:
            attempts += 1
            duration = random.randint(1, 12)
            price    = Decimal(f"{random.uniform(10000,50000):.2f}")
            hours    = random.randint(20, 100)
            cat      = random.choice(self.driving_category_ids)
            instr    = random.choice(self.instructor_ids)
            school   = random.choice(self.driving_school_ids)
            try:
                self.db.execute(
                    "INSERT INTO course (course_duration_month, course_price, driving_hours, "
                    "driving_category_id, instructor_id, driving_school_id) "
                    "VALUES (%s, %s, %s, %s, %s, %s);",
                    (duration, price, hours, cat, instr, school)
                )
                inserted += 1
            except Exception:
                continue
        if inserted < chunk_size:
            print(f"⚠ Only inserted {inserted}/{chunk_size} courses after {attempts} attempts")

    def insert_courses(self, total=10000, workers=8):
        base = total // workers
        rem  = total % workers
        chunks = [base+1 if i<rem else base for i in range(workers)]
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futures = [ex.submit(self._insert_courses_chunk, c) for c in chunks]
            for f in as_completed(futures):
                f.result()
        print(f"Finished inserting up to {total} courses.")

    # --- Reviews ---

    def _insert_reviews_chunk(self, chunk_size):
        inserted = 0
        attempts = 0
        max_attempts = chunk_size * 2
        while inserted < chunk_size and attempts < max_attempts:
            attempts += 1
            text     = fake.sentence(nb_words=10)
            reviewer = fake.name()
            grade    = round(random.uniform(1.0, 5.0), 1)
            dt       = date.today() - timedelta(days=random.randint(0,365))
            course   = random.choice(self.course_ids)
            likes    = random.randint(0,100)
            try:
                self.db.execute(
                    "INSERT INTO review (review_text, reviewer_name, grade, review_date, course_id, likes) "
                    "VALUES (%s, %s, %s, %s, %s, %s);",
                    (text, reviewer, grade, dt, course, likes)
                )
                inserted += 1
            except Exception:
                continue
        if inserted < chunk_size:
            print(f"⚠ Only inserted {inserted}/{chunk_size} reviews after {attempts} attempts")

    def insert_reviews(self, total=10000, workers=8):
        base = total // workers
        rem  = total % workers
        chunks = [base+1 if i<rem else base for i in range(workers)]
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futures = [ex.submit(self._insert_reviews_chunk, c) for c in chunks]
            for f in as_completed(futures):
                f.result()
        print(f"Finished inserting up to {total} reviews.")

    # --- Enrollments ---

    def _insert_enrollments_chunk(self, chunk_size):
        inserted = 0
        attempts = 0
        max_attempts = chunk_size * 5
        while inserted < chunk_size and attempts < max_attempts:
            attempts += 1
            sid   = random.randint(10000, 30000)
            group = random.choice(self.student_group_ids)
            try:
                self.db.execute(
                    "INSERT INTO enrollment (student_id, student_group_id) VALUES (%s, %s);",
                    (sid, group)
                )
                inserted += 1
            except Exception:
                continue
        if inserted < chunk_size:
            print(f"⚠ Only inserted {inserted}/{chunk_size} enrollments after {attempts} attempts")

    def insert_enrollments(self, total=10000, workers=8):
        base = total // workers
        rem  = total % workers
        chunks = [base+1 if i<rem else base for i in range(workers)]
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futures = [ex.submit(self._insert_enrollments_chunk, c) for c in chunks]
            for f in as_completed(futures):
                f.result()
        print(f"Finished inserting up to {total} enrollments.")

if __name__ == '__main__':
    DSN = "host=localhost dbname=kurs_bd user=postgres password=admin2005"
    gen = BatchGenerator(DSN)

    gen.insert_courses(total=10000, workers=8)
    gen.insert_reviews(total=10000, workers=8)
    gen.insert_enrollments(total=10000, workers=8)
