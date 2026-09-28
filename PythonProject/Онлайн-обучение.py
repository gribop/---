import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import hashlib
from datetime import datetime


class DatabaseManager:

    def __init__(self, db_name='university.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.insert_sample_data()

    def create_tables(self):
        tables = {
            'students': '''
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    last_name TEXT NOT NULL,
                    first_name TEXT NOT NULL,
                    middle_name TEXT,
                    group_name TEXT NOT NULL,
                    phone TEXT,
                    email TEXT,
                    status TEXT DEFAULT 'активен',
                    enrollment_date DATE DEFAULT CURRENT_DATE
                )
            ''',
            'teachers': '''
                CREATE TABLE IF NOT EXISTS teachers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    last_name TEXT NOT NULL,
                    first_name TEXT NOT NULL,
                    middle_name TEXT,
                    position TEXT NOT NULL,
                    department TEXT,
                    phone TEXT,
                    email TEXT,
                    status TEXT DEFAULT 'работает'
                )
            ''',
            'subjects': '''
                CREATE TABLE IF NOT EXISTS subjects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    hours INTEGER NOT NULL,
                    semester INTEGER,
                    type TEXT CHECK(type IN ('лекция', 'практика', 'лабораторная')),
                    teacher_id INTEGER,
                    FOREIGN KEY (teacher_id) REFERENCES teachers (id)
                )
            ''',
            'grades': '''
                CREATE TABLE IF NOT EXISTS grades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    subject_id INTEGER NOT NULL,
                    grade INTEGER CHECK(grade BETWEEN 2 AND 5),
                    work_type TEXT CHECK(work_type IN ('экзамен', 'зачет', 'тест', 'дз')),
                    date DATE DEFAULT CURRENT_DATE,
                    teacher_id INTEGER NOT NULL,
                    comment TEXT,
                    FOREIGN KEY (student_id) REFERENCES students (id),
                    FOREIGN KEY (subject_id) REFERENCES subjects (id),
                    FOREIGN KEY (teacher_id) REFERENCES teachers (id)
                )
            ''',
            'users': '''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT CHECK(role IN ('студент', 'преподаватель', 'админ')),
                    student_id INTEGER,
                    teacher_id INTEGER,
                    FOREIGN KEY (student_id) REFERENCES students (id),
                    FOREIGN KEY (teacher_id) REFERENCES teachers (id)
                )
            ''',
            'schedule': '''
                CREATE TABLE IF NOT EXISTS schedule (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject_id INTEGER NOT NULL,
                    day_of_week TEXT CHECK(day_of_week IN ('пн', 'вт', 'ср', 'чт', 'пт', 'сб')),
                    start_time TEXT,
                    end_time TEXT,
                    room TEXT,
                    FOREIGN KEY (subject_id) REFERENCES subjects (id)
                )
            ''',
            'student_subjects': '''
                CREATE TABLE IF NOT EXISTS student_subjects (
                    student_id INTEGER NOT NULL,
                    subject_id INTEGER NOT NULL,
                    PRIMARY KEY (student_id, subject_id),
                    FOREIGN KEY (student_id) REFERENCES students (id),
                    FOREIGN KEY (subject_id) REFERENCES subjects (id)
                )
            '''
        }

        for table_name, sql in tables.items():
            try:
                self.cursor.execute(sql)
            except sqlite3.Error as e:
                print(f"Ошибка создания таблицы {table_name}: {e}")

        self.conn.commit()

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def insert_sample_data(self):
        # Проверяем, есть ли уже данные
        self.cursor.execute("SELECT COUNT(*) FROM users")
        if self.cursor.fetchone()[0] > 0:
            return

        # Добавляем студентов
        students = [
            ('Иванов', 'Иван', 'Иванович', 'ИТ-101', '+79001112233', 'ivanov@edu.ru'),
            ('Петров', 'Петр', 'Петрович', 'ИТ-101', '+79002223344', 'petrov@edu.ru'),
            ('Сидорова', 'Мария', 'Сергеевна', 'ИТ-102', '+79003334455', 'sidorova@edu.ru'),
            ('Кузнецов', 'Алексей', 'Дмитриевич', 'ИТ-102', '+79004445566', 'kuznetsov@edu.ru'),
            ('Смирнова', 'Анна', 'Владимировна', 'ИТ-103', '+79005556677', 'smirnova@edu.ru')
        ]

        for student in students:
            self.cursor.execute('''
                INSERT INTO students (last_name, first_name, middle_name, group_name, phone, email)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', student)

        # Добавляем преподавателей
        teachers = [
            ('Попов', 'Александр', 'Владимирович', 'профессор', 'Кафедра информатики', '+79006667788', 'popov@edu.ru'),
            ('Николаева', 'Елена', 'Анатольевна', 'доцент', 'Кафедра математики', '+79007778899', 'nikolaeva@edu.ru'),
            ('Федоров', 'Сергей', 'Игоревич', 'старший преподаватель', 'Кафедра программирования', '+79008889900',
             'fedorov@edu.ru')
        ]

        for teacher in teachers:
            self.cursor.execute('''
                INSERT INTO teachers (last_name, first_name, middle_name, position, department, phone, email)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', teacher)

        # Добавляем предметы
        subjects = [
            ('Математический анализ', 120, 1, 'лекция', 1),
            ('Основы программирования', 90, 1, 'практика', 3),
            ('Базы данных', 90, 2, 'лабораторная', 2),
            ('Алгоритмы и структуры данных', 120, 2, 'лекция', 1),
            ('Веб-разработка', 60, 3, 'практика', 3)
        ]

        for subject in subjects:
            self.cursor.execute('''
                INSERT INTO subjects (name, hours, semester, type, teacher_id)
                VALUES (?, ?, ?, ?, ?)
            ''', subject)

        # Добавляем расписание
        schedule = [
            (1, 'пн', '09:00', '10:30', 'А-101'),
            (2, 'пн', '11:00', '12:30', 'Б-203'),
            (3, 'вт', '09:00', '10:30', 'В-305'),
            (4, 'ср', '14:00', '15:30', 'А-102'),
            (5, 'чт', '16:00', '17:30', 'Г-404')
        ]

        for item in schedule:
            self.cursor.execute('''
                INSERT INTO schedule (subject_id, day_of_week, start_time, end_time, room)
                VALUES (?, ?, ?, ?, ?)
            ''', item)

        # Добавляем связи студентов и предметов
        for student_id in range(1, 6):
            for subject_id in range(1, 4):
                self.cursor.execute('''
                    INSERT OR IGNORE INTO student_subjects (student_id, subject_id)
                    VALUES (?, ?)
                ''', (student_id, subject_id))

        # Добавляем оценки
        import random
        work_types = ['экзамен', 'зачет', 'тест']
        for student_id in range(1, 6):
            for subject_id in range(1, 4):
                grade = random.choice([3, 4, 5])
                work_type = work_types[subject_id % 3]
                teacher_id = subject_id % 3 + 1

                self.cursor.execute('''
                    INSERT INTO grades (student_id, subject_id, grade, work_type, teacher_id, comment)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (student_id, subject_id, grade, work_type, teacher_id,
                      f'Комментарий к работе студента {student_id} по предмету {subject_id}'))

        # Добавляем пользователей
        users = [
            ('admin', self.hash_password('admin'), 'админ', None, None),
            ('teacher1', self.hash_password('teacher1'), 'преподаватель', None, 1),
            ('teacher2', self.hash_password('teacher2'), 'преподаватель', None, 2),
            ('teacher3', self.hash_password('teacher3'), 'преподаватель', None, 3),
            ('student1', self.hash_password('student1'), 'студент', 1, None),
            ('student2', self.hash_password('student2'), 'студент', 2, None),
            ('student3', self.hash_password('student3'), 'студент', 3, None),
            ('student4', self.hash_password('student4'), 'студент', 4, None),
            ('student5', self.hash_password('student5'), 'студент', 5, None)
        ]

        for user in users:
            self.cursor.execute('''
                INSERT INTO users (username, password, role, student_id, teacher_id)
                VALUES (?, ?, ?, ?, ?)
            ''', user)

        self.conn.commit()
        print("Тестовые данные успешно добавлены")

    def authenticate_user(self, username, password):
        hashed_password = self.hash_password(password)

        self.cursor.execute('''
            SELECT u.*, s.last_name, s.first_name, s.middle_name, s.group_name,
                   t.last_name, t.first_name, t.middle_name, t.position
            FROM users u
            LEFT JOIN students s ON u.student_id = s.id
            LEFT JOIN teachers t ON u.teacher_id = t.id
            WHERE u.username = ? AND u.password = ?
        ''', (username, hashed_password))

        result = self.cursor.fetchone()

        if result:
            return {
                'id': result[0],
                'username': result[1],
                'role': result[3],
                'student_id': result[4],
                'teacher_id': result[5],
                'full_name': self.get_full_name(result),
                'group': result[8] if result[8] else None,
                'position': result[12] if result[12] else None
            }
        return None

    def get_full_name(self, user_data):
        if user_data[3] == 'студент' and user_data[6]:
            return f"{user_data[6]} {user_data[7]} {user_data[8] or ''}".strip()
        elif user_data[3] == 'преподаватель' and user_data[9]:
            return f"{user_data[9]} {user_data[10]} {user_data[11] or ''}".strip()
        return user_data[1]

    # CRUD операции для студентов
    def get_students(self, search_query=None):
        if search_query:
            sql = '''
                SELECT * FROM students 
                WHERE last_name LIKE ? OR first_name LIKE ? OR group_name LIKE ?
                ORDER BY last_name, first_name
            '''
            params = (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%')
        else:
            sql = 'SELECT * FROM students ORDER BY last_name, first_name'
            params = ()

        self.cursor.execute(sql, params)
        return self.cursor.fetchall()

    def add_student(self, data):
        sql = '''
            INSERT INTO students (last_name, first_name, middle_name, group_name, phone, email, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        self.cursor.execute(sql, data)
        self.conn.commit()
        return self.cursor.lastrowid

    def update_student(self, student_id, data):

        sql = '''
            UPDATE students 
            SET last_name=?, first_name=?, middle_name=?, group_name=?, phone=?, email=?, status=?
            WHERE id=?
        '''
        self.cursor.execute(sql, (*data, student_id))
        self.conn.commit()
        return self.cursor.rowcount

    def delete_student(self, student_id):
        try:
            self.cursor.execute('DELETE FROM students WHERE id=?', (student_id,))
            self.cursor.execute('DELETE FROM users WHERE student_id=?', (student_id,))
            self.cursor.execute('DELETE FROM grades WHERE student_id=?', (student_id,))
            self.cursor.execute('DELETE FROM student_subjects WHERE student_id=?', (student_id,))
            self.conn.commit()
            return True
        except:
            return False

    # CRUD операции для преподавателей
    def get_teachers(self, search_query=None):
        if search_query:
            sql = '''
                SELECT * FROM teachers 
                WHERE last_name LIKE ? OR first_name LIKE ? OR position LIKE ?
                ORDER BY last_name, first_name
            '''
            params = (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%')
        else:
            sql = 'SELECT * FROM teachers ORDER BY last_name, first_name'
            params = ()

        self.cursor.execute(sql, params)
        return self.cursor.fetchall()

    def add_teacher(self, data):
        sql = '''
            INSERT INTO teachers (last_name, first_name, middle_name, position, department, phone, email, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        self.cursor.execute(sql, data)
        self.conn.commit()
        return self.cursor.lastrowid

    def update_teacher(self, teacher_id, data):
        sql = '''
            UPDATE teachers 
            SET last_name=?, first_name=?, middle_name=?, position=?, department=?, phone=?, email=?, status=?
            WHERE id=?
        '''
        self.cursor.execute(sql, (*data, teacher_id))
        self.conn.commit()
        return self.cursor.rowcount

    def delete_teacher(self, teacher_id):
        try:
            # Сначала обнуляем teacher_id в связанных таблицах
            self.cursor.execute('UPDATE subjects SET teacher_id = NULL WHERE teacher_id = ?', (teacher_id,))
            self.cursor.execute('UPDATE grades SET teacher_id = 1 WHERE teacher_id = ?', (teacher_id,))
            self.cursor.execute('DELETE FROM users WHERE teacher_id = ?', (teacher_id,))
            self.cursor.execute('DELETE FROM teachers WHERE id = ?', (teacher_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка удаления преподавателя: {e}")
            return False

    # CRUD операции для предметов
    def get_subjects(self):
        self.cursor.execute('''
            SELECT s.*, t.last_name, t.first_name 
            FROM subjects s
            LEFT JOIN teachers t ON s.teacher_id = t.id
            ORDER BY s.semester, s.name
        ''')
        return self.cursor.fetchall()

    def add_subject(self, data):
        sql = '''
            INSERT INTO subjects (name, hours, semester, type, teacher_id)
            VALUES (?, ?, ?, ?, ?)
        '''
        self.cursor.execute(sql, data)
        self.conn.commit()
        return self.cursor.lastrowid

    def update_subject(self, subject_id, data):
        sql = '''
            UPDATE subjects 
            SET name=?, hours=?, semester=?, type=?, teacher_id=?
            WHERE id=?
        '''
        self.cursor.execute(sql, (*data, subject_id))
        self.conn.commit()
        return self.cursor.rowcount

    def delete_subject(self, subject_id):
        try:
            self.cursor.execute('DELETE FROM student_subjects WHERE subject_id = ?', (subject_id,))
            self.cursor.execute('DELETE FROM grades WHERE subject_id = ?', (subject_id,))
            self.cursor.execute('DELETE FROM schedule WHERE subject_id = ?', (subject_id,))
            self.cursor.execute('DELETE FROM subjects WHERE id = ?', (subject_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Ошибка удаления предмета: {e}")
            return False

    # CRUD операции для оценок
    def get_grades(self, student_id=None, subject_id=None):
        if student_id:
            sql = '''
                SELECT g.id, 
                       st.last_name || ' ' || st.first_name || ' (' || st.group_name || ')' as student,
                       s.name as subject,
                       CASE g.grade
                           WHEN 2 THEN '2 (неуд)'
                           WHEN 3 THEN '3 (удовл)'
                           WHEN 4 THEN '4 (хорошо)'
                           WHEN 5 THEN '5 (отлично)'
                           ELSE 'нет оценки'
                       END as grade_text,
                       g.work_type,
                       t.last_name || ' ' || t.first_name as teacher,
                       g.date,
                       g.comment
                FROM grades g
                JOIN students st ON g.student_id = st.id
                JOIN subjects s ON g.subject_id = s.id
                JOIN teachers t ON g.teacher_id = t.id
                WHERE g.student_id = ?
                ORDER BY g.date DESC
            '''
            params = (student_id,)
        elif subject_id:
            sql = '''
                SELECT g.id,
                       st.last_name || ' ' || st.first_name || ' (' || st.group_name || ')' as student,
                       s.name as subject,
                       CASE g.grade
                           WHEN 2 THEN '2 (неуд)'
                           WHEN 3 THEN '3 (удовл)'
                           WHEN 4 THEN '4 (хорошо)'
                           WHEN 5 THEN '5 (отлично)'
                           ELSE 'нет оценки'
                       END as grade_text,
                       g.work_type,
                       t.last_name || ' ' || t.first_name as teacher,
                       g.date,
                       g.comment
                FROM grades g
                JOIN students st ON g.student_id = st.id
                JOIN subjects s ON g.subject_id = s.id
                JOIN teachers t ON g.teacher_id = t.id
                WHERE g.subject_id = ?
                ORDER BY g.date DESC
            '''
            params = (subject_id,)
        else:
            sql = '''
                SELECT g.id,
                       st.last_name || ' ' || st.first_name || ' (' || st.group_name || ')' as student,
                       s.name as subject,
                       CASE g.grade
                           WHEN 2 THEN '2 (неуд)'
                           WHEN 3 THEN '3 (удовл)'
                           WHEN 4 THEN '4 (хорошо)'
                           WHEN 5 THEN '5 (отлично)'
                           ELSE 'нет оценки'
                       END as grade_text,
                       g.work_type,
                       t.last_name || ' ' || t.first_name as teacher,
                       g.date,
                       g.comment
                FROM grades g
                JOIN students st ON g.student_id = st.id
                JOIN subjects s ON g.subject_id = s.id
                JOIN teachers t ON g.teacher_id = t.id
                ORDER BY g.date DESC
            '''
            params = ()

        self.cursor.execute(sql, params)
        return self.cursor.fetchall()

    def add_grade(self, data):
        sql = '''
            INSERT INTO grades (student_id, subject_id, grade, work_type, teacher_id, comment, date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        self.cursor.execute(sql, data)
        self.conn.commit()
        return self.cursor.lastrowid

    def update_grade(self, grade_id, data):
        sql = '''
            UPDATE grades 
            SET student_id=?, subject_id=?, grade=?, work_type=?, teacher_id=?, comment=?, date=?
            WHERE id=?
        '''
        self.cursor.execute(sql, (*data, grade_id))
        self.conn.commit()
        return self.cursor.rowcount

    def delete_grade(self, grade_id):
        self.cursor.execute('DELETE FROM grades WHERE id=?', (grade_id,))
        self.conn.commit()
        return self.cursor.rowcount

    # CRUD операции для расписания
    def get_schedule(self):
        self.cursor.execute('''
            SELECT sch.id,
                   CASE sch.day_of_week
                       WHEN 'пн' THEN 'Понедельник'
                       WHEN 'вт' THEN 'Вторник'
                       WHEN 'ср' THEN 'Среда'
                       WHEN 'чт' THEN 'Четверг'
                       WHEN 'пт' THEN 'Пятница'
                       WHEN 'сб' THEN 'Суббота'
                       ELSE sch.day_of_week
                   END as day,
                   sch.start_time,
                   sch.end_time,
                   s.name as subject,
                   t.last_name || ' ' || t.first_name as teacher,
                   sch.room
            FROM schedule sch
            JOIN subjects s ON sch.subject_id = s.id
            LEFT JOIN teachers t ON s.teacher_id = t.id
            ORDER BY 
                CASE sch.day_of_week
                    WHEN 'пн' THEN 1
                    WHEN 'вт' THEN 2
                    WHEN 'ср' THEN 3
                    WHEN 'чт' THEN 4
                    WHEN 'пт' THEN 5
                    WHEN 'сб' THEN 6
                    ELSE 7
                END,
                sch.start_time
        ''')
        return self.cursor.fetchall()

    def add_schedule(self, data):
        sql = '''
            INSERT INTO schedule (subject_id, day_of_week, start_time, end_time, room)
            VALUES (?, ?, ?, ?, ?)
        '''
        self.cursor.execute(sql, data)
        self.conn.commit()
        return self.cursor.lastrowid

    def update_schedule(self, schedule_id, data):
        sql = '''
            UPDATE schedule 
            SET subject_id=?, day_of_week=?, start_time=?, end_time=?, room=?
            WHERE id=?
        '''
        self.cursor.execute(sql, (*data, schedule_id))
        self.conn.commit()
        return self.cursor.rowcount

    def delete_schedule(self, schedule_id):
        self.cursor.execute('DELETE FROM schedule WHERE id=?', (schedule_id,))
        self.conn.commit()
        return self.cursor.rowcount

    # Получение статистики
    def get_statistics(self):
        stats = {}

        # Количество студентов
        self.cursor.execute('SELECT COUNT(*) FROM students')
        stats['students_count'] = self.cursor.fetchone()[0]

        # Количество преподавателей
        self.cursor.execute('SELECT COUNT(*) FROM teachers')
        stats['teachers_count'] = self.cursor.fetchone()[0]

        # Количество предметов
        self.cursor.execute('SELECT COUNT(*) FROM subjects')
        stats['subjects_count'] = self.cursor.fetchone()[0]

        # Количество оценок
        self.cursor.execute('SELECT COUNT(*) FROM grades')
        stats['grades_count'] = self.cursor.fetchone()[0]

        # Средний балл
        self.cursor.execute('SELECT AVG(grade) FROM grades')
        avg_grade = self.cursor.fetchone()[0]
        stats['avg_grade'] = round(avg_grade, 2) if avg_grade else 0

        # Активные студенты
        self.cursor.execute("SELECT COUNT(*) FROM students WHERE status='активен'")
        stats['active_students'] = self.cursor.fetchone()[0]
        return stats

class LoginWindow:

    def __init__(self, root, db_manager, on_success):
        self.root = root
        self.db_manager = db_manager
        self.on_success = on_success

        self.setup_ui()

    def setup_ui(self):
        self.root.title("Система онлайн-обучения - Вход")
        self.root.geometry("500x400")
        self.center_window()

        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="30")
        main_frame.pack(expand=True, fill='both')

        # Заголовок
        title = ttk.Label(main_frame, text="Электронный журнал",
                          font=("Arial", 24, "bold"))
        title.pack(pady=(0, 30))

        # Фрейм формы
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(pady=20)

        # Поля ввода
        ttk.Label(form_frame, text="Логин:", font=("Arial", 11)).grid(
            row=0, column=0, padx=5, pady=10, sticky='e')
        self.username_entry = ttk.Entry(form_frame, width=30, font=("Arial", 11))
        self.username_entry.grid(row=0, column=1, padx=5, pady=10)
        self.username_entry.insert(0, "admin")

        ttk.Label(form_frame, text="Пароль:", font=("Arial", 11)).grid(
            row=1, column=0, padx=5, pady=10, sticky='e')
        self.password_entry = ttk.Entry(form_frame, width=30, show="*", font=("Arial", 11))
        self.password_entry.grid(row=1, column=1, padx=5, pady=10)
        self.password_entry.insert(0, "admin")

        # Кнопка входа
        login_btn = ttk.Button(main_frame, text="Войти", command=self.login,
                               style="Accent.TButton")
        login_btn.pack(pady=20)

        # Информация о тестовых аккаунтах
        info_frame = ttk.LabelFrame(main_frame, text="Тестовые аккаунты", padding=10)
        info_frame.pack(fill='x', pady=10)

        accounts = [
            "Администратор: admin / admin",
            "Преподаватель: teacher1 / teacher1",
            "Студент: student1 / student1"
        ]

        for account in accounts:
            ttk.Label(info_frame, text=account, font=("Arial", 9)).pack(anchor='w', pady=2)

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Предупреждение", "Введите логин и пароль")
            return

        user_data = self.db_manager.authenticate_user(username, password)

        if user_data:
            self.on_success(user_data)
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")


class MainApplication:

    def __init__(self, root, db_manager, user_data):
        self.root = root
        self.db_manager = db_manager
        self.user_data = user_data

        self.root.title(f"Система онлайн-обучения - {user_data['role'].capitalize()}")
        self.root.geometry("1200x700")

        self.setup_styles()
        self.create_widgets()

    def setup_styles(self):
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Arial', 18, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 14, 'bold'))
        style.configure('Accent.TButton', font=('Arial', 10, 'bold'))

        # Цвета для разных ролей
        role_colors = {
            'админ': 'navy',
            'преподаватель': 'darkgreen',
            'студент': 'darkred'
        }

        color = role_colors.get(self.user_data['role'], 'black')
        style.configure('Role.TLabel', foreground=color, font=('Arial', 12, 'bold'))

    def create_widgets(self):
        # Верхняя панель
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill='x')

        ttk.Label(top_frame, text="Электронная система обучения",
                  style='Title.TLabel').pack(side='left')

        user_info = ttk.Label(top_frame,
                              text=f"{self.user_data['full_name']} ({self.user_data['role']})",
                              style='Role.TLabel')
        user_info.pack(side='right')

        # Основная область
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True)

        # Левая панель - меню
        self.menu_frame = ttk.LabelFrame(main_frame, text="Меню", padding="15")
        self.menu_frame.pack(side='left', fill='y', padx=10, pady=10)

        # Правая панель - контент
        self.content_frame = ttk.Frame(main_frame)
        self.content_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        # Создаем меню в зависимости от роли
        self.create_menu()

        # Отображаем стартовую страницу
        self.show_start_page()

    def create_menu(self):
        # Очищаем меню
        for widget in self.menu_frame.winfo_children():
            widget.destroy()

        menu_items = []

        if self.user_data['role'] == 'админ':
            menu_items = [
                ("Статистика", self.show_statistics),
                ("Управление студентами", self.manage_students),
                ("Управление преподавателями", self.manage_teachers),
                ("Управление предметами", self.manage_subjects),
                ("Управление оценками", self.manage_grades),
                ("Управление расписанием", self.manage_schedule),
                ("Отчеты", self.show_reports),
                ("Настройки", self.show_settings)
            ]
        elif self.user_data['role'] == 'преподаватель':
            menu_items = [
                ("Выставить оценку", self.add_grade_teacher),
                ("Мои студенты", self.show_my_students),
                ("Мои предметы", self.show_my_subjects),
                ("Успеваемость", self.show_performance)
            ]
        else:  # студент
            menu_items = [
                ("Мои оценки", self.show_my_grades),
                ("Мое расписание", self.show_my_schedule),
                ("Мои данные", self.show_my_info),
                ("Успеваемость", self.show_my_performance)
            ]

        # Добавляем кнопки меню
        for text, command in menu_items:
            btn = ttk.Button(self.menu_frame, text=text, command=command, width=20)
            btn.pack(pady=5, anchor='w')

        # Кнопка выхода
        ttk.Separator(self.menu_frame, orient='horizontal').pack(fill='x', pady=10)
        logout_btn = ttk.Button(self.menu_frame, text="Выход",
                                command=self.logout, width=20)
        logout_btn.pack(pady=5)

    def show_start_page(self):
        self.clear_content()

        title = ttk.Label(self.content_frame, text="Добро пожаловать!",
                          style='Title.TLabel')
        title.pack(pady=50)

        info_text = f"""
        Добро пожаловать в систему электронного обучения!

        Роль: {self.user_data['role']}
        Пользователь: {self.user_data['full_name']}
        """

        if self.user_data['role'] == 'студент':
            info_text += f"\nГруппа: {self.user_data.get('group', 'Не указана')}"
        elif self.user_data['role'] == 'преподаватель':
            info_text += f"\nДолжность: {self.user_data.get('position', 'Не указана')}"

        info_label = ttk.Label(self.content_frame, text=info_text,
                               font=("Arial", 12), justify='center')
        info_label.pack(pady=20)

        # Статистика для админа
        if self.user_data['role'] == 'админ':
            stats = self.db_manager.get_statistics()
            stats_text = f"""
            Статистика системы:
            • Студентов: {stats['students_count']}
            • Преподавателей: {stats['teachers_count']}
            • Предметов: {stats['subjects_count']}
            • Оценок: {stats['grades_count']}
            • Средний балл: {stats['avg_grade']}
            • Активных студентов: {stats['active_students']}
            """
            stats_label = ttk.Label(self.content_frame, text=stats_text,
                                    font=("Arial", 11), justify='left')
            stats_label.pack(pady=20)

    def show_statistics(self):
        """Показать статистику системы"""
        self.clear_content()

        title = ttk.Label(self.content_frame, text="Статистика системы",
                          style='Title.TLabel')
        title.pack(pady=20)

        stats = self.db_manager.get_statistics()

        # Таблица статистики
        tree_frame = ttk.Frame(self.content_frame)
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)

        tree = ttk.Treeview(tree_frame, columns=('Показатель', 'Значение'), show='headings')
        tree.heading('Показатель', text='Показатель')
        tree.heading('Значение', text='Значение')

        tree.column('Показатель', width=250)
        tree.column('Значение', width=150, anchor='center')

        stats_display = [
            ('Количество студентов', stats['students_count']),
            ('Количество преподавателей', stats['teachers_count']),
            ('Количество предметов', stats['subjects_count']),
            ('Количество оценок', stats['grades_count']),
            ('Средний балл', stats['avg_grade']),
            ('Активных студентов', stats['active_students'])
        ]

        for name, value in stats_display:
            tree.insert('', 'end', values=(name, value))

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def manage_students(self):
        """Управление студентами"""
        self.clear_content()

        title = ttk.Label(self.content_frame, text="Управление студентами",
                          style='Title.TLabel')
        title.pack(pady=10)

        # Панель поиска и управления
        control_frame = ttk.Frame(self.content_frame)
        control_frame.pack(fill='x', padx=20, pady=10)

        ttk.Label(control_frame, text="Поиск:").pack(side='left', padx=5)
        search_entry = ttk.Entry(control_frame, width=30)
        search_entry.pack(side='left', padx=5)

        def search():
            query = search_entry.get().strip()
            students = self.db_manager.get_students(query if query else None)
            self.display_students_table(students)

        search_btn = ttk.Button(control_frame, text="Найти", command=search)
        search_btn.pack(side='left', padx=5)

        add_btn = ttk.Button(control_frame, text="Добавить студента",
                             command=self.add_student_dialog)
        add_btn.pack(side='right', padx=5)

        # Таблица студентов
        self.students_tree_frame = ttk.Frame(self.content_frame)
        self.students_tree_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Получаем и отображаем студентов
        students = self.db_manager.get_students()
        self.display_students_table(students)

    def display_students_table(self, students):
        # Очищаем предыдущую таблицу
        for widget in self.students_tree_frame.winfo_children():
            widget.destroy()

        # Создаем таблицу
        columns = ('ID', 'Фамилия', 'Имя', 'Отчество', 'Группа', 'Телефон', 'Email', 'Статус', 'Дата поступления')
        tree = ttk.Treeview(self.students_tree_frame, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        tree.column('ID', width=50)
        tree.column('Фамилия', width=120)
        tree.column('Имя', width=120)
        tree.column('Email', width=150)
        tree.column('Дата поступления', width=120)

        # Добавляем данные
        for student in students:
            # Форматируем дату для отображения
            enrollment_date = student[8]
            if enrollment_date:
                try:
                    date_obj = datetime.strptime(enrollment_date, '%Y-%m-%d')
                    enrollment_date = date_obj.strftime('%d.%m.%Y')
                except:
                    pass

            tree.insert('', 'end', values=student)

        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(self.students_tree_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Контекстное меню
        def show_context_menu(event):
            item = tree.identify_row(event.y)
            if item:
                menu = tk.Menu(self.root, tearoff=0)
                menu.add_command(label="Редактировать",
                                 command=lambda: self.edit_student_dialog(tree.item(item)['values'][0]))
                menu.add_command(label="Удалить",
                                 command=lambda: self.delete_student_dialog(tree.item(item)['values'][0]))
                menu.tk_popup(event.x_root, event.y_root)

        tree.bind('<Button-3>', show_context_menu)

    def add_student_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавление студента")
        dialog.geometry("400x500")

        ttk.Label(dialog, text="Добавление нового студента",
                  font=("Arial", 14, "bold")).pack(pady=10)

        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill='both', expand=True)

        entries = {}
        fields = [
            ('Фамилия*', 'last_name'),
            ('Имя*', 'first_name'),
            ('Отчество', 'middle_name'),
            ('Группа*', 'group_name'),
            ('Телефон', 'phone'),
            ('Email', 'email'),
            ('Статус', 'status')
        ]

        for i, (label, key) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky='w', pady=5)

            if key == 'status':
                entry = ttk.Combobox(form_frame, values=['активен', 'отчислен', 'академический отпуск'])
                entry.set('активен')
            else:
                entry = ttk.Entry(form_frame, width=30)

            entry.grid(row=i, column=1, pady=5, padx=10)
            entries[key] = entry

        def save_student():
            data = []
            required_fields = ['last_name', 'first_name', 'group_name']

            for key in ['last_name', 'first_name', 'middle_name', 'group_name', 'phone', 'email', 'status']:
                value = entries[key].get().strip() if entries[key].get() else None

                if key in required_fields and not value:
                    messagebox.showwarning("Ошибка", f"Поле '{key}' обязательно!")
                    return

                data.append(value)

            try:
                student_id = self.db_manager.add_student(tuple(data))
                if student_id:
                    messagebox.showinfo("Успех", f"Студент добавлен! ID: {student_id}")
                    dialog.destroy()
                    self.manage_students()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при добавлении: {e}")

        # Кнопки
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Сохранить", command=save_student).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Отмена", command=dialog.destroy).pack(side='right', padx=5)

    def edit_student_dialog(self, student_id):
        # Получаем данные студента
        self.db_manager.cursor.execute('SELECT * FROM students WHERE id=?', (student_id,))
        student = self.db_manager.cursor.fetchone()

        if not student:
            messagebox.showerror("Ошибка", "Студент не найден")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Редактирование студента")
        dialog.geometry("400x500")

        ttk.Label(dialog, text="Редактирование студента",
                  font=("Arial", 14, "bold")).pack(pady=10)

        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill='both', expand=True)

        entries = {}
        fields = [
            ('ID', 'id', student[0], True),
            ('Фамилия*', 'last_name', student[1], False),
            ('Имя*', 'first_name', student[2], False),
            ('Отчество', 'middle_name', student[3], False),
            ('Группа*', 'group_name', student[4], False),
            ('Телефон', 'phone', student[5], False),
            ('Email', 'email', student[6], False),
            ('Статус', 'status', student[7], False)
        ]

        for i, (label, key, value, readonly) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky='w', pady=5)

            if key == 'status':
                entry = ttk.Combobox(form_frame, values=['активен', 'отчислен', 'академический отпуск'])
                entry.set(value or 'активен')
            elif key == 'ID':
                entry = ttk.Entry(form_frame, width=30)
                entry.insert(0, str(value))
                entry.config(state='readonly')
            else:
                entry = ttk.Entry(form_frame, width=30)
                entry.insert(0, value if value else '')

            entry.grid(row=i, column=1, pady=5, padx=10)
            entries[key] = entry

        def update_student():
            data = []
            required_fields = ['last_name', 'first_name', 'group_name']

            for key in ['last_name', 'first_name', 'middle_name', 'group_name', 'phone', 'email', 'status']:
                value = entries[key].get().strip() if entries[key].get() else None

                if key in required_fields and not value:
                    messagebox.showwarning("Ошибка", f"Поле '{key}' обязательно!")
                    return

                data.append(value)

            try:
                result = self.db_manager.update_student(student_id, tuple(data))
                if result:
                    messagebox.showinfo("Успех", "Данные студента обновлены!")
                    dialog.destroy()
                    self.manage_students()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при обновлении: {e}")

        # Кнопки
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Сохранить", command=update_student).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Отмена", command=dialog.destroy).pack(side='right', padx=5)

    def delete_student_dialog(self, student_id):
        if messagebox.askyesno("Подтверждение",
                               "Удалить студента и все связанные данные?"):
            if self.db_manager.delete_student(student_id):
                messagebox.showinfo("Успех", "Студент удален")
                self.manage_students()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить студента")

    def manage_teachers(self):
        self.clear_content()

        title = ttk.Label(self.content_frame, text="Управление преподавателями",
                          style='Title.TLabel')
        title.pack(pady=10)

        # Панель поиска и управления
        control_frame = ttk.Frame(self.content_frame)
        control_frame.pack(fill='x', padx=20, pady=10)

        ttk.Label(control_frame, text="Поиск:").pack(side='left', padx=5)
        search_entry = ttk.Entry(control_frame, width=30)
        search_entry.pack(side='left', padx=5)

        def search():
            query = search_entry.get().strip()
            teachers = self.db_manager.get_teachers(query if query else None)
            self.display_teachers_table(teachers)

        search_btn = ttk.Button(control_frame, text="Найти", command=search)
        search_btn.pack(side='left', padx=5)

        add_btn = ttk.Button(control_frame, text="➕ Добавить преподавателя",
                             command=self.add_teacher_dialog)
        add_btn.pack(side='right', padx=5)

        # Таблица преподавателей
        self.teachers_tree_frame = ttk.Frame(self.content_frame)
        self.teachers_tree_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Получаем и отображаем преподавателей
        teachers = self.db_manager.get_teachers()
        self.display_teachers_table(teachers)

    def display_teachers_table(self, teachers):
        # Очищаем предыдущую таблицу
        for widget in self.teachers_tree_frame.winfo_children():
            widget.destroy()

        # Создаем таблицу
        columns = ('ID', 'Фамилия', 'Имя', 'Отчество', 'Должность', 'Кафедра', 'Телефон', 'Email', 'Статус')
        tree = ttk.Treeview(self.teachers_tree_frame, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        tree.column('ID', width=50)
        tree.column('Фамилия', width=120)
        tree.column('Имя', width=120)
        tree.column('Должность', width=150)
        tree.column('Кафедра', width=150)
        tree.column('Email', width=150)

        # Добавляем данные
        for teacher in teachers:
            tree.insert('', 'end', values=teacher)

        # Добавляем скроллбар
        scrollbar = ttk.Scrollbar(self.teachers_tree_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Контекстное меню
        def show_context_menu(event):
            item = tree.identify_row(event.y)
            if item:
                menu = tk.Menu(self.root, tearoff=0)
                menu.add_command(label="Редактировать",
                                 command=lambda: self.edit_teacher_dialog(tree.item(item)['values'][0]))
                menu.add_command(label="Удалить",
                                 command=lambda: self.delete_teacher_dialog(tree.item(item)['values'][0]))
                menu.tk_popup(event.x_root, event.y_root)

        tree.bind('<Button-3>', show_context_menu)

    def add_teacher_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавление преподавателя")
        dialog.geometry("500x500")

        ttk.Label(dialog, text="Добавление преподавателя",
                  font=("Arial", 14, "bold")).pack(pady=10)

        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill='both', expand=True)

        entries = {}
        fields = [
            ('Фамилия*', 'last_name'),
            ('Имя*', 'first_name'),
            ('Отчество', 'middle_name'),
            ('Должность*', 'position'),
            ('Кафедра', 'department'),
            ('Телефон', 'phone'),
            ('Email', 'email'),
            ('Статус', 'status')
        ]

        for i, (label, key) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky='w', pady=5)

            if key == 'status':
                entry = ttk.Combobox(form_frame, values=['работает', 'отпуск', 'уволен'])
                entry.set('работает')
            else:
                entry = ttk.Entry(form_frame, width=30)

            entry.grid(row=i, column=1, pady=5, padx=10)
            entries[key] = entry

        def save_teacher():
            data = []
            required_fields = ['last_name', 'first_name', 'position']

            for key in ['last_name', 'first_name', 'middle_name', 'position', 'department', 'phone', 'email', 'status']:
                value = entries[key].get().strip() if entries[key].get() else None

                if key in required_fields and not value:
                    messagebox.showwarning("Ошибка", f"Поле '{key}' обязательно!")
                    return

                data.append(value)

            try:
                teacher_id = self.db_manager.add_teacher(tuple(data))
                if teacher_id:
                    messagebox.showinfo("Успех", f"Преподаватель добавлен! ID: {teacher_id}")
                    dialog.destroy()
                    self.manage_teachers()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при добавлении: {e}")

        # Кнопки
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Сохранить", command=save_teacher).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Отмена", command=dialog.destroy).pack(side='right', padx=5)

    def edit_teacher_dialog(self, teacher_id):
        # Получаем данные преподавателя
        self.db_manager.cursor.execute('SELECT * FROM teachers WHERE id=?', (teacher_id,))
        teacher = self.db_manager.cursor.fetchone()

        if not teacher:
            messagebox.showerror("Ошибка", "Преподаватель не найден")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Редактирование преподавателя")
        dialog.geometry("500x500")

        ttk.Label(dialog, text="Редактирование преподавателя",
                  font=("Arial", 14, "bold")).pack(pady=10)

        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill='both', expand=True)

        entries = {}
        fields = [
            ('ID', 'id', teacher[0], True),
            ('Фамилия*', 'last_name', teacher[1], False),
            ('Имя*', 'first_name', teacher[2], False),
            ('Отчество', 'middle_name', teacher[3], False),
            ('Должность*', 'position', teacher[4], False),
            ('Кафедра', 'department', teacher[5], False),
            ('Телефон', 'phone', teacher[6], False),
            ('Email', 'email', teacher[7], False),
            ('Статус', 'status', teacher[8], False)
        ]

        for i, (label, key, value, readonly) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky='w', pady=5)

            if key == 'status':
                entry = ttk.Combobox(form_frame, values=['работает', 'отпуск', 'уволен'])
                entry.set(value or 'работает')
            elif key == 'ID':
                entry = ttk.Entry(form_frame, width=30)
                entry.insert(0, str(value))
                entry.config(state='readonly')
            else:
                entry = ttk.Entry(form_frame, width=30)
                entry.insert(0, value if value else '')

            entry.grid(row=i, column=1, pady=5, padx=10)
            entries[key] = entry

        def update_teacher():
            data = []
            required_fields = ['last_name', 'first_name', 'position']

            for key in ['last_name', 'first_name', 'middle_name', 'position', 'department', 'phone', 'email', 'status']:
                value = entries[key].get().strip() if entries[key].get() else None

                if key in required_fields and not value:
                    messagebox.showwarning("Ошибка", f"Поле '{key}' обязательно!")
                    return

                data.append(value)

            try:
                result = self.db_manager.update_teacher(teacher_id, tuple(data))
                if result:
                    messagebox.showinfo("Успех", "Данные преподавателя обновлены!")
                    dialog.destroy()
                    self.manage_teachers()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при обновлении: {e}")

        # Кнопки
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Сохранить", command=update_teacher).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Отмена", command=dialog.destroy).pack(side='right', padx=5)

    def delete_teacher_dialog(self, teacher_id):
        if messagebox.askyesno("Подтверждение",
                               "Удалить преподавателя? Его предметы будут освобождены."):
            if self.db_manager.delete_teacher(teacher_id):
                messagebox.showinfo("Успех", "Преподаватель удален")
                self.manage_teachers()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить преподавателя")

    def manage_subjects(self):
        self.clear_content()

        title = ttk.Label(self.content_frame, text="Управление предметами",
                          style='Title.TLabel')
        title.pack(pady=10)

        # Получаем предметы
        subjects = self.db_manager.get_subjects()

        # Таблица
        tree_frame = ttk.Frame(self.content_frame)
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)

        columns = ('ID', 'Название', 'Часы', 'Семестр', 'Тип', 'Преподаватель')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        tree.column('ID', width=50)
        tree.column('Название', width=200)
        tree.column('Преподаватель', width=150)

        for subject in subjects:
            teacher_name = f"{subject[5]} {subject[6]}" if subject[5] else "Не назначен"
            tree.insert('', 'end', values=(subject[0], subject[1], subject[2],
                                           subject[3] if subject[3] else '-',
                                           subject[4], teacher_name))

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Кнопки управления
        btn_frame = ttk.Frame(self.content_frame)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Добавить предмет",
                   command=self.add_subject_dialog).pack(side='left', padx=5)

        # Контекстное меню
        def show_context_menu(event):
            item = tree.identify_row(event.y)
            if item:
                menu = tk.Menu(self.root, tearoff=0)
                menu.add_command(label="Редактировать",
                                 command=lambda: self.edit_subject_dialog(tree.item(item)['values'][0]))
                menu.add_command(label="Удалить",
                                 command=lambda: self.delete_subject_dialog(tree.item(item)['values'][0]))
                menu.tk_popup(event.x_root, event.y_root)

        tree.bind('<Button-3>', show_context_menu)

    def add_subject_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавление предмета")
        dialog.geometry("400x400")

        ttk.Label(dialog, text="Добавление предмета",
                  font=("Arial", 14, "bold")).pack(pady=10)

        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill='both', expand=True)

        # Название
        ttk.Label(form_frame, text="Название*:").grid(row=0, column=0, sticky='w', pady=5)
        name_entry = ttk.Entry(form_frame, width=30)
        name_entry.grid(row=0, column=1, pady=5, padx=10)

        # Часы
        ttk.Label(form_frame, text="Часы*:").grid(row=1, column=0, sticky='w', pady=5)
        hours_entry = ttk.Entry(form_frame, width=30)
        hours_entry.grid(row=1, column=1, pady=5, padx=10)
        hours_entry.insert(0, "90")

        # Семестр
        ttk.Label(form_frame, text="Семестр:").grid(row=2, column=0, sticky='w', pady=5)
        semester_entry = ttk.Entry(form_frame, width=30)
        semester_entry.grid(row=2, column=1, pady=5, padx=10)
        semester_entry.insert(0, "1")

        # Тип
        ttk.Label(form_frame, text="Тип:").grid(row=3, column=0, sticky='w', pady=5)
        type_combo = ttk.Combobox(form_frame, values=['лекция', 'практика', 'лабораторная'])
        type_combo.set('лекция')
        type_combo.grid(row=3, column=1, pady=5, padx=10)

        # Преподаватель
        ttk.Label(form_frame, text="Преподаватель:").grid(row=4, column=0, sticky='w', pady=5)

        # Получаем список преподавателей
        teachers = self.db_manager.get_teachers()
        teacher_options = ["Не назначен"] + [f"{t[0]}: {t[1]} {t[2]}" for t in teachers]
        teacher_combo = ttk.Combobox(form_frame, values=teacher_options, width=28)
        teacher_combo.set('Не назначен')
        teacher_combo.grid(row=4, column=1, pady=5, padx=10)

        def save_subject():
            name = name_entry.get().strip()
            hours = hours_entry.get().strip()
            semester = semester_entry.get().strip()
            subject_type = type_combo.get()
            teacher_selection = teacher_combo.get()

            if not name or not hours:
                messagebox.showwarning("Ошибка", "Название и часы обязательны!")
                return

            try:
                hours = int(hours)
                if hours <= 0:
                    messagebox.showwarning("Ошибка", "Часы должны быть положительным числом!")
                    return

                if semester:
                    semester = int(semester)

                # Получаем ID преподавателя
                teacher_id = None
                if teacher_selection != "Не назначен":
                    teacher_id = int(teacher_selection.split(':')[0])

                data = (name, hours, semester if semester else None, subject_type, teacher_id)

                subject_id = self.db_manager.add_subject(data)
                if subject_id:
                    messagebox.showinfo("Успех", f"Предмет добавлен! ID: {subject_id}")
                    dialog.destroy()
                    self.manage_subjects()

            except ValueError:
                messagebox.showerror("Ошибка", "Часы и семестр должны быть числами!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при добавлении: {e}")

        # Кнопки
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Сохранить", command=save_subject).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Отмена", command=dialog.destroy).pack(side='right', padx=5)

    def edit_subject_dialog(self, subject_id):
        # Получаем данные предмета
        subjects = self.db_manager.get_subjects()
        subject = None
        for s in subjects:
            if s[0] == subject_id:
                subject = s
                break

        if not subject:
            messagebox.showerror("Ошибка", "Предмет не найден")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Редактирование предмета")
        dialog.geometry("400x400")

        ttk.Label(dialog, text="Редактирование предмета",
                  font=("Arial", 14, "bold")).pack(pady=10)

        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill='both', expand=True)

        # ID (только чтение)
        ttk.Label(form_frame, text="ID:").grid(row=0, column=0, sticky='w', pady=5)
        id_entry = ttk.Entry(form_frame, width=30)
        id_entry.insert(0, str(subject[0]))
        id_entry.config(state='readonly')
        id_entry.grid(row=0, column=1, pady=5, padx=10)

        # Название
        ttk.Label(form_frame, text="Название*:").grid(row=1, column=0, sticky='w', pady=5)
        name_entry = ttk.Entry(form_frame, width=30)
        name_entry.insert(0, subject[1])
        name_entry.grid(row=1, column=1, pady=5, padx=10)

        # Часы
        ttk.Label(form_frame, text="Часы*:").grid(row=2, column=0, sticky='w', pady=5)
        hours_entry = ttk.Entry(form_frame, width=30)
        hours_entry.insert(0, str(subject[2]))
        hours_entry.grid(row=2, column=1, pady=5, padx=10)

        # Семестр
        ttk.Label(form_frame, text="Семестр:").grid(row=3, column=0, sticky='w', pady=5)
        semester_entry = ttk.Entry(form_frame, width=30)
        semester_entry.insert(0, str(subject[3]) if subject[3] else "")
        semester_entry.grid(row=3, column=1, pady=5, padx=10)

        # Тип
        ttk.Label(form_frame, text="Тип:").grid(row=4, column=0, sticky='w', pady=5)
        type_combo = ttk.Combobox(form_frame, values=['лекция', 'практика', 'лабораторная'])
        type_combo.set(subject[4] if subject[4] else 'лекция')
        type_combo.grid(row=4, column=1, pady=5, padx=10)

        # Преподаватель
        ttk.Label(form_frame, text="Преподаватель:").grid(row=5, column=0, sticky='w', pady=5)

        # Получаем список преподавателей
        teachers = self.db_manager.get_teachers()
        teacher_options = ["Не назначен"] + [f"{t[0]}: {t[1]} {t[2]}" for t in teachers]
        teacher_combo = ttk.Combobox(form_frame, values=teacher_options, width=28)

        # Устанавливаем текущего преподавателя
        current_teacher = "Не назначен"
        if subject[5] and subject[6]:
            current_teacher = f"{subject[5]}: {subject[6]}"
        teacher_combo.set(current_teacher)
        teacher_combo.grid(row=5, column=1, pady=5, padx=10)

        def update_subject():
            name = name_entry.get().strip()
            hours = hours_entry.get().strip()
            semester = semester_entry.get().strip()
            subject_type = type_combo.get()
            teacher_selection = teacher_combo.get()

            if not name or not hours:
                messagebox.showwarning("Ошибка", "Название и часы обязательны!")
                return

            try:
                hours = int(hours)
                if hours <= 0:
                    messagebox.showwarning("Ошибка", "Часы должны быть положительным числом!")
                    return

                if semester:
                    semester = int(semester)
                else:
                    semester = None

                # Получаем ID преподавателя
                teacher_id = None
                if teacher_selection != "Не назначен":
                    teacher_id = int(teacher_selection.split(':')[0])

                data = (name, hours, semester, subject_type, teacher_id)

                result = self.db_manager.update_subject(subject_id, data)
                if result:
                    messagebox.showinfo("Успех", "Данные предмета обновлены!")
                    dialog.destroy()
                    self.manage_subjects()

            except ValueError:
                messagebox.showerror("Ошибка", "Часы и семестр должны быть числами!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при обновлении: {e}")

        # Кнопки
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Сохранить", command=update_subject).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Отмена", command=dialog.destroy).pack(side='right', padx=5)

    def delete_subject_dialog(self, subject_id):
        if messagebox.askyesno("Подтверждение",
                               "Удалить предмет и все связанные данные (оценки, расписание)?"):
            if self.db_manager.delete_subject(subject_id):
                messagebox.showinfo("Успех", "Предмет удален")
                self.manage_subjects()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить предмет")

    def manage_grades(self):
        self.clear_content()

        title = ttk.Label(self.content_frame, text="Управление оценками",
                          style='Title.TLabel')
        title.pack(pady=10)

        # Получаем все оценки
        grades = self.db_manager.get_grades()

        # Таблица
        tree_frame = ttk.Frame(self.content_frame)
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)

        columns = ('ID', 'Студент (Группа)', 'Предмет', 'Оценка', 'Тип работы',
                   'Преподаватель', 'Дата', 'Комментарий')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        tree.column('ID', width=50)
        tree.column('Студент (Группа)', width=180)
        tree.column('Предмет', width=150)
        tree.column('Оценка', width=100, anchor='center')
        tree.column('Преподаватель', width=150)
        tree.column('Дата', width=100, anchor='center')
        tree.column('Комментарий', width=200)

        for grade in grades:
            # Форматируем дату для отображения
            date_str = grade[6]
            if date_str:
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    date_str = date_obj.strftime('%d.%m.%Y')
                except:
                    pass

            tree.insert('', 'end', values=(grade[0], grade[1], grade[2], grade[3],
                                           grade[4], grade[5], date_str, grade[7]))

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Кнопки управления
        btn_frame = ttk.Frame(self.content_frame)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Добавить оценку",
                   command=self.add_grade_admin).pack(side='left', padx=5)

        # Контекстное меню
        def show_context_menu(event):
            item = tree.identify_row(event.y)
            if item:
                menu = tk.Menu(self.root, tearoff=0)
                menu.add_command(label="Редактировать",
                                 command=lambda: self.edit_grade_dialog(tree.item(item)['values'][0]))
                menu.add_command(label="Удалить",
                                 command=lambda: self.delete_grade_dialog(tree.item(item)['values'][0]))
                menu.tk_popup(event.x_root, event.y_root)

        tree.bind('<Button-3>', show_context_menu)

    def add_grade_admin(self):
        self.add_grade_dialog()

    def add_grade_dialog(self, teacher_id=None):
        dialog = tk.Toplevel(self.root)
        dialog.title("Выставление оценки")
        dialog.geometry("500x500")

        ttk.Label(dialog, text="Выставление оценки",
                  font=("Arial", 14, "bold")).pack(pady=10)

        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill='both', expand=True)

        # Получаем студентов для выпадающего списка
        self.db_manager.cursor.execute('SELECT id, last_name, first_name, group_name FROM students ORDER BY last_name')
        students = self.db_manager.cursor.fetchall()

        # Получаем предметы
        self.db_manager.cursor.execute('SELECT id, name FROM subjects ORDER BY name')
        subjects = self.db_manager.cursor.fetchall()

        # Получаем преподавателей
        self.db_manager.cursor.execute('SELECT id, last_name, first_name FROM teachers ORDER BY last_name')
        teachers = self.db_manager.cursor.fetchall()

        # Студент
        ttk.Label(form_frame, text="Студент*:").grid(row=0, column=0, sticky='w', pady=5)
        student_combo = ttk.Combobox(form_frame, width=30)
        student_combo['values'] = [f"{s[0]}: {s[1]} {s[2]} ({s[3]})" for s in students]
        student_combo.grid(row=0, column=1, pady=5, padx=10)
        if students:
            student_combo.current(0)

        # Предмет
        ttk.Label(form_frame, text="Предмет*:").grid(row=1, column=0, sticky='w', pady=5)
        subject_combo = ttk.Combobox(form_frame, width=30)
        subject_combo['values'] = [f"{s[0]}: {s[1]}" for s in subjects]
        subject_combo.grid(row=1, column=1, pady=5, padx=10)
        if subjects:
            subject_combo.current(0)

        # Оценка
        ttk.Label(form_frame, text="Оценка* (2-5):").grid(row=2, column=0, sticky='w', pady=5)
        grade_combo = ttk.Combobox(form_frame, values=['2 (неуд)', '3 (удовл)', '4 (хорошо)', '5 (отлично)'])
        grade_combo.set('5 (отлично)')
        grade_combo.grid(row=2, column=1, pady=5, padx=10)

        # Тип работы
        ttk.Label(form_frame, text="Тип работы*:").grid(row=3, column=0, sticky='w', pady=5)
        work_type_combo = ttk.Combobox(form_frame, values=['экзамен', 'зачет', 'тест', 'дз'])
        work_type_combo.set('экзамен')
        work_type_combo.grid(row=3, column=1, pady=5, padx=10)

        # Преподаватель (если не указан)
        if not teacher_id:
            ttk.Label(form_frame, text="Преподаватель*:").grid(row=4, column=0, sticky='w', pady=5)
            teacher_combo = ttk.Combobox(form_frame, width=30)
            teacher_combo['values'] = [f"{t[0]}: {t[1]} {t[2]}" for t in teachers]
            teacher_combo.grid(row=4, column=1, pady=5, padx=10)
            if teachers:
                teacher_combo.current(0)

        # Комментарий
        ttk.Label(form_frame, text="Комментарий:").grid(row=5, column=0, sticky='w', pady=5)
        comment_text = scrolledtext.ScrolledText(form_frame, width=30, height=4)
        comment_text.grid(row=5, column=1, pady=5, padx=10)

        def save_grade():
            """Сохранение оценки"""
            try:
                # Извлекаем ID из строк вида "ID: Информация"
                student_id = int(student_combo.get().split(':')[0].strip())
                subject_id = int(subject_combo.get().split(':')[0].strip())

                # Извлекаем числовую оценку из строки
                grade_text = grade_combo.get()
                grade = int(grade_text[0])  # Берем первую цифру

                work_type = work_type_combo.get()

                if teacher_id:
                    teacher_id_val = teacher_id
                else:
                    teacher_id_val = int(teacher_combo.get().split(':')[0].strip())

                comment = comment_text.get(1.0, tk.END).strip()
                date = datetime.now().strftime('%Y-%m-%d')

                data = (student_id, subject_id, grade, work_type, teacher_id_val, comment, date)

                result = self.db_manager.add_grade(data)
                if result:
                    messagebox.showinfo("Успех", "Оценка добавлена!")
                    dialog.destroy()

                    # Обновляем таблицу в зависимости от роли
                    if self.user_data['role'] == 'админ':
                        self.manage_grades()
                    elif self.user_data['role'] == 'преподаватель':
                        self.add_grade_teacher()

            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при добавлении: {str(e)}")

        # Кнопки
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Сохранить", command=save_grade).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Отмена", command=dialog.destroy).pack(side='right', padx=5)

    def edit_grade_dialog(self, grade_id):
        """Диалог редактирования оценки"""
        # Получаем данные оценки
        grades = self.db_manager.get_grades()
        grade_data = None
        for g in grades:
            if g[0] == grade_id:
                grade_data = g
                break

        if not grade_data:
            messagebox.showerror("Ошибка", "Оценка не найдена")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Редактирование оценки")
        dialog.geometry("500x500")

        ttk.Label(dialog, text="Редактирование оценки",
                  font=("Arial", 14, "bold")).pack(pady=10)

        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill='both', expand=True)

        # ID (только чтение)
        ttk.Label(form_frame, text="ID:").grid(row=0, column=0, sticky='w', pady=5)
        id_entry = ttk.Entry(form_frame, width=30)
        id_entry.insert(0, str(grade_data[0]))
        id_entry.config(state='readonly')
        id_entry.grid(row=0, column=1, pady=5, padx=10)

        # Студент (только чтение)
        ttk.Label(form_frame, text="Студент:").grid(row=1, column=0, sticky='w', pady=5)
        student_label = ttk.Label(form_frame, text=grade_data[1], font=("Arial", 10))
        student_label.grid(row=1, column=1, sticky='w', pady=5, padx=10)

        # Предмет (только чтение)
        ttk.Label(form_frame, text="Предмет:").grid(row=2, column=0, sticky='w', pady=5)
        subject_label = ttk.Label(form_frame, text=grade_data[2], font=("Arial", 10))
        subject_label.grid(row=2, column=1, sticky='w', pady=5, padx=10)

        # Оценка
        ttk.Label(form_frame, text="Оценка*:").grid(row=3, column=0, sticky='w', pady=5)
        grade_combo = ttk.Combobox(form_frame, values=['2 (неуд)', '3 (удовл)', '4 (хорошо)', '5 (отлично)'])

        # Устанавливаем текущую оценку
        current_grade = grade_data[3]
        grade_combo.set(current_grade)
        grade_combo.grid(row=3, column=1, pady=5, padx=10)

        # Тип работы
        ttk.Label(form_frame, text="Тип работы*:").grid(row=4, column=0, sticky='w', pady=5)
        work_type_combo = ttk.Combobox(form_frame, values=['экзамен', 'зачет', 'тест', 'дз'])
        work_type_combo.set(grade_data[4])
        work_type_combo.grid(row=4, column=1, pady=5, padx=10)

        # Преподаватель (только чтение)
        ttk.Label(form_frame, text="Преподаватель:").grid(row=5, column=0, sticky='w', pady=5)
        teacher_label = ttk.Label(form_frame, text=grade_data[5], font=("Arial", 10))
        teacher_label.grid(row=5, column=1, sticky='w', pady=5, padx=10)

        # Дата
        ttk.Label(form_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=6, column=0, sticky='w', pady=5)
        date_entry = ttk.Entry(form_frame, width=30)
        date_entry.insert(0, grade_data[6])
        date_entry.grid(row=6, column=1, pady=5, padx=10)

        # Комментарий
        ttk.Label(form_frame, text="Комментарий:").grid(row=7, column=0, sticky='w', pady=5)
        comment_text = scrolledtext.ScrolledText(form_frame, width=30, height=4)
        comment_text.insert(1.0, grade_data[7] if grade_data[7] else "")
        comment_text.grid(row=7, column=1, pady=5, padx=10)

        def update_grade():
            try:
                # Извлекаем числовую оценку из строки
                grade_text = grade_combo.get()
                grade = int(grade_text[0])  # Берем первую цифру

                work_type = work_type_combo.get()
                date = date_entry.get().strip()
                comment = comment_text.get(1.0, tk.END).strip()

                # Получаем оригинальные данные для неизменяемых полей
                student_id = None
                subject_id = None
                teacher_id_val = None

                # Извлекаем ID из оригинальных данных
                self.db_manager.cursor.execute('SELECT student_id, subject_id, teacher_id FROM grades WHERE id = ?',
                                               (grade_id,))
                original_data = self.db_manager.cursor.fetchone()

                if original_data:
                    student_id, subject_id, teacher_id_val = original_data

                if not student_id or not subject_id or not teacher_id_val:
                    messagebox.showerror("Ошибка", "Не удалось получить оригинальные данные оценки")
                    return

                data = (student_id, subject_id, grade, work_type, teacher_id_val, comment, date)

                result = self.db_manager.update_grade(grade_id, data)
                if result:
                    messagebox.showinfo("Успех", "Оценка обновлена!")
                    dialog.destroy()
                    self.manage_grades()

            except ValueError:
                messagebox.showerror("Ошибка", "Оценка должна быть числом!")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при обновлении: {str(e)}")

        # Кнопки
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Сохранить", command=update_grade).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Отмена", command=dialog.destroy).pack(side='right', padx=5)

    def delete_grade_dialog(self, grade_id):
        """Диалог удаления оценки"""
        if messagebox.askyesno("Подтверждение", "Удалить оценку?"):
            if self.db_manager.delete_grade(grade_id):
                messagebox.showinfo("Успех", "Оценка удалена")
                self.manage_grades()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить оценку")

    def manage_schedule(self):
        """Управление расписанием"""
        self.clear_content()

        title = ttk.Label(self.content_frame, text="Управление расписанием",
                          style='Title.TLabel')
        title.pack(pady=10)

        # Получаем расписание
        schedule = self.db_manager.get_schedule()

        # Таблица
        tree_frame = ttk.Frame(self.content_frame)
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)

        columns = ('ID', 'День', 'Начало', 'Конец', 'Предмет', 'Преподаватель', 'Аудитория')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        tree.column('ID', width=50)
        tree.column('Предмет', width=150)
        tree.column('Преподаватель', width=150)

        for item in schedule:
            tree.insert('', 'end', values=item)

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Кнопки управления
        btn_frame = ttk.Frame(self.content_frame)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Добавить занятие",
                   command=self.add_schedule_dialog).pack(side='left', padx=5)

        # Контекстное меню
        def show_context_menu(event):
            item = tree.identify_row(event.y)
            if item:
                menu = tk.Menu(self.root, tearoff=0)
                menu.add_command(label="Редактировать",
                                 command=lambda: self.edit_schedule_dialog(tree.item(item)['values'][0]))
                menu.add_command(label="Удалить",
                                 command=lambda: self.delete_schedule_dialog(tree.item(item)['values'][0]))
                menu.tk_popup(event.x_root, event.y_root)

        tree.bind('<Button-3>', show_context_menu)

    def add_schedule_dialog(self):
        """Диалог добавления занятия в расписание"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавление занятия")
        dialog.geometry("400x400")

        ttk.Label(dialog, text="Добавление занятия",
                  font=("Arial", 14, "bold")).pack(pady=10)

        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill='both', expand=True)

        # Предмет
        ttk.Label(form_frame, text="Предмет*:").grid(row=0, column=0, sticky='w', pady=5)

        # Получаем список предметов
        subjects = self.db_manager.get_subjects()
        subject_options = [f"{s[0]}: {s[1]}" for s in subjects]
        subject_combo = ttk.Combobox(form_frame, values=subject_options, width=30)
        subject_combo.grid(row=0, column=1, pady=5, padx=10)
        if subject_options:
            subject_combo.current(0)

        # День недели
        ttk.Label(form_frame, text="День недели*:").grid(row=1, column=0, sticky='w', pady=5)
        day_combo = ttk.Combobox(form_frame, values=['пн', 'вт', 'ср', 'чт', 'пт', 'сб'])
        day_combo.set('пн')
        day_combo.grid(row=1, column=1, pady=5, padx=10)

        # Время начала
        ttk.Label(form_frame, text="Начало* (ЧЧ:ММ):").grid(row=2, column=0, sticky='w', pady=5)
        start_entry = ttk.Entry(form_frame, width=30)
        start_entry.insert(0, "09:00")
        start_entry.grid(row=2, column=1, pady=5, padx=10)

        # Время окончания
        ttk.Label(form_frame, text="Окончание* (ЧЧ:ММ):").grid(row=3, column=0, sticky='w', pady=5)
        end_entry = ttk.Entry(form_frame, width=30)
        end_entry.insert(0, "10:30")
        end_entry.grid(row=3, column=1, pady=5, padx=10)

        # Аудитория
        ttk.Label(form_frame, text="Аудитория:").grid(row=4, column=0, sticky='w', pady=5)
        room_entry = ttk.Entry(form_frame, width=30)
        room_entry.insert(0, "А-101")
        room_entry.grid(row=4, column=1, pady=5, padx=10)

        def save_schedule():
            try:
                subject_selection = subject_combo.get()
                day = day_combo.get()
                start = start_entry.get().strip()
                end = end_entry.get().strip()
                room = room_entry.get().strip()

                if not subject_selection or not day or not start or not end:
                    messagebox.showwarning("Ошибка", "Заполните все обязательные поля!")
                    return

                # Извлекаем ID предмета
                subject_id = int(subject_selection.split(':')[0])

                data = (subject_id, day, start, end, room)

                schedule_id = self.db_manager.add_schedule(data)
                if schedule_id:
                    messagebox.showinfo("Успех", f"Занятие добавлено! ID: {schedule_id}")
                    dialog.destroy()
                    self.manage_schedule()

            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при добавлении: {e}")

        # Кнопки
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Сохранить", command=save_schedule).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Отмена", command=dialog.destroy).pack(side='right', padx=5)

    def edit_schedule_dialog(self, schedule_id):
        # Получаем данные расписания
        schedule_items = self.db_manager.get_schedule()
        schedule_item = None
        for item in schedule_items:
            if item[0] == schedule_id:
                schedule_item = item
                break

        if not schedule_item:
            messagebox.showerror("Ошибка", "Занятие не найдено")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Редактирование занятия")
        dialog.geometry("400x400")

        ttk.Label(dialog, text="Редактирование занятия",
                  font=("Arial", 14, "bold")).pack(pady=10)

        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill='both', expand=True)

        # ID (только чтение)
        ttk.Label(form_frame, text="ID:").grid(row=0, column=0, sticky='w', pady=5)
        id_entry = ttk.Entry(form_frame, width=30)
        id_entry.insert(0, str(schedule_item[0]))
        id_entry.config(state='readonly')
        id_entry.grid(row=0, column=1, pady=5, padx=10)

        # Предмет (только чтение)
        ttk.Label(form_frame, text="Предмет:").grid(row=1, column=0, sticky='w', pady=5)
        subject_label = ttk.Label(form_frame, text=schedule_item[4], font=("Arial", 10))
        subject_label.grid(row=1, column=1, sticky='w', pady=5, padx=10)

        # День недели
        ttk.Label(form_frame, text="День недели*:").grid(row=2, column=0, sticky='w', pady=5)
        day_combo = ttk.Combobox(form_frame, values=['пн', 'вт', 'ср', 'чт', 'пт', 'сб'])
        # Преобразуем русское название дня в английское сокращение
        day_map = {
            'Понедельник': 'пн',
            'Вторник': 'вт',
            'Среда': 'ср',
            'Четверг': 'чт',
            'Пятница': 'пт',
            'Суббота': 'сб'
        }
        current_day = schedule_item[1]
        day_combo.set(day_map.get(current_day, current_day))
        day_combo.grid(row=2, column=1, pady=5, padx=10)

        # Время начала
        ttk.Label(form_frame, text="Начало* (ЧЧ:ММ):").grid(row=3, column=0, sticky='w', pady=5)
        start_entry = ttk.Entry(form_frame, width=30)
        start_entry.insert(0, schedule_item[2])
        start_entry.grid(row=3, column=1, pady=5, padx=10)

        # Время окончания
        ttk.Label(form_frame, text="Окончание* (ЧЧ:ММ):").grid(row=4, column=0, sticky='w', pady=5)
        end_entry = ttk.Entry(form_frame, width=30)
        end_entry.insert(0, schedule_item[3])
        end_entry.grid(row=4, column=1, pady=5, padx=10)

        # Аудитория
        ttk.Label(form_frame, text="Аудитория:").grid(row=5, column=0, sticky='w', pady=5)
        room_entry = ttk.Entry(form_frame, width=30)
        room_entry.insert(0, schedule_item[6])
        room_entry.grid(row=5, column=1, pady=5, padx=10)

        def update_schedule():
            try:
                day = day_combo.get()
                start = start_entry.get().strip()
                end = end_entry.get().strip()
                room = room_entry.get().strip()

                if not day or not start or not end:
                    messagebox.showwarning("Ошибка", "Заполните все обязательные поля!")
                    return

                # Получаем ID предмета из оригинальных данных
                # Нужно получить subject_id из базы данных
                self.db_manager.cursor.execute('SELECT subject_id FROM schedule WHERE id = ?', (schedule_id,))
                result = self.db_manager.cursor.fetchone()
                if not result:
                    messagebox.showerror("Ошибка", "Не удалось получить ID предмета")
                    return

                subject_id = result[0]

                data = (subject_id, day, start, end, room)

                result = self.db_manager.update_schedule(schedule_id, data)
                if result:
                    messagebox.showinfo("Успех", "Занятие обновлено!")
                    dialog.destroy()
                    self.manage_schedule()

            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при обновлении: {e}")

        # Кнопки
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Сохранить", command=update_schedule).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Отмена", command=dialog.destroy).pack(side='right', padx=5)

    def delete_schedule_dialog(self, schedule_id):

        if messagebox.askyesno("Подтверждение", "Удалить занятие из расписания?"):
            if self.db_manager.delete_schedule(schedule_id):
                messagebox.showinfo("Успех", "Занятие удалено")
                self.manage_schedule()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить занятие")

    def show_reports(self):
        """Показать отчеты"""
        self.clear_content()

        title = ttk.Label(self.content_frame, text="Отчеты и аналитика",
                          style='Title.TLabel')
        title.pack(pady=10)

        # Фрейм с отчетами
        reports_frame = ttk.Frame(self.content_frame)
        reports_frame.pack(fill='both', expand=True, padx=20, pady=10)

        reports = [
            ("Успеваемость по группам", self.show_group_performance),
            ("Рейтинг студентов", self.show_student_rating),
            ("Нагрузка преподавателей", self.show_teacher_workload),
            ("График занятий", self.show_schedule_chart)
        ]

        for i, (text, command) in enumerate(reports):
            btn = ttk.Button(reports_frame, text=text, command=command, width=30)
            btn.grid(row=i // 2, column=i % 2, padx=10, pady=10, sticky='nsew')

    def show_group_performance(self):

        dialog = tk.Toplevel(self.root)
        dialog.title("Успеваемость по группам")
        dialog.geometry("600x400")

        self.db_manager.cursor.execute('''
            SELECT s.group_name, COUNT(DISTINCT s.id) as students,
                   COUNT(g.id) as grades_count, 
                   ROUND(AVG(g.grade), 2) as avg_grade,
                   SUM(CASE WHEN g.grade = 5 THEN 1 ELSE 0 END) as excellent,
                   SUM(CASE WHEN g.grade = 2 THEN 1 ELSE 0 END) as failed
            FROM students s
            LEFT JOIN grades g ON s.id = g.student_id
            GROUP BY s.group_name
            ORDER BY avg_grade DESC
        ''')

        data = self.db_manager.cursor.fetchall()

        # Таблица
        tree_frame = ttk.Frame(dialog)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)

        columns = ('Группа', 'Студентов', 'Оценок', 'Средний балл', 'Отлично', 'Неуд')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor='center')

        for row in data:
            tree.insert('', 'end', values=row)

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def show_student_rating(self):

        dialog = tk.Toplevel(self.root)
        dialog.title("Рейтинг студентов")
        dialog.geometry("700x400")

        self.db_manager.cursor.execute('''
            SELECT s.last_name || ' ' || s.first_name as student_name,
                   s.group_name,
                   COUNT(g.id) as grades_count,
                   ROUND(AVG(g.grade), 2) as avg_grade,
                   RANK() OVER (ORDER BY AVG(g.grade) DESC) as rating
            FROM students s
            JOIN grades g ON s.id = g.student_id
            GROUP BY s.id
            HAVING COUNT(g.id) >= 3
            ORDER BY avg_grade DESC
            LIMIT 20
        ''')

        data = self.db_manager.cursor.fetchall()

        # Таблица
        tree_frame = ttk.Frame(dialog)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)

        columns = ('Рейтинг', 'Студент', 'Группа', 'Оценок', 'Средний балл')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor='center')

        for row in data:
            tree.insert('', 'end', values=(row[4], row[0], row[1], row[2], row[3]))

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def show_teacher_workload(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Нагрузка преподавателей")
        dialog.geometry("600x400")

        self.db_manager.cursor.execute('''
            SELECT t.last_name || ' ' || t.first_name as teacher_name,
                   COUNT(DISTINCT s.id) as subjects_count,
                   SUM(s.hours) as total_hours,
                   COUNT(DISTINCT g.id) as grades_count,
                   ROUND(AVG(g.grade), 2) as avg_grade
            FROM teachers t
            LEFT JOIN subjects s ON t.id = s.teacher_id
            LEFT JOIN grades g ON t.id = g.teacher_id
            GROUP BY t.id
            ORDER BY total_hours DESC
        ''')

        data = self.db_manager.cursor.fetchall()

        # Таблица
        tree_frame = ttk.Frame(dialog)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)

        columns = ('Преподаватель', 'Предметов', 'Часов', 'Оценок', 'Средний балл')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor='center')

        for row in data:
            tree.insert('', 'end', values=row)

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def show_schedule_chart(self):
        messagebox.showinfo("График занятий",
                            "Здесь будет графическое представление расписания")

    def show_settings(self):
        messagebox.showinfo("Настройки",
                            "Настройки системы:\n"
                            "• Версия: 1.0\n"
                            "• Разработчик: Лабораторная работа\n"
                            "• База данных: SQLite\n"
                            "• Интерфейс: Tkinter")

    def add_grade_teacher(self):

        self.add_grade_dialog(self.user_data['teacher_id'])

    def show_my_students(self):

        self.clear_content()

        title = ttk.Label(self.content_frame, text=" Мои студенты",
                          style='Title.TLabel')
        title.pack(pady=10)

        # Получаем студентов преподавателя
        self.db_manager.cursor.execute('''
            SELECT DISTINCT s.*
            FROM students s
            JOIN student_subjects ss ON s.id = ss.student_id
            JOIN subjects sub ON ss.subject_id = sub.id
            WHERE sub.teacher_id = ?
            ORDER BY s.last_name, s.first_name
        ''', (self.user_data['teacher_id'],))

        students = self.db_manager.cursor.fetchall()

        # Таблица
        tree_frame = ttk.Frame(self.content_frame)
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)

        columns = ('ID', 'Фамилия', 'Имя', 'Отчество', 'Группа', 'Телефон', 'Email', 'Статус')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        tree.column('Email', width=150)

        for student in students:
            tree.insert('', 'end', values=student)

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def show_my_subjects(self):
        """Показать мои предметы"""
        self.clear_content()

        title = ttk.Label(self.content_frame, text="Мои предметы",
                          style='Title.TLabel')
        title.pack(pady=10)

        # Получаем предметы преподавателя
        self.db_manager.cursor.execute('''
            SELECT s.*, COUNT(DISTINCT ss.student_id) as students_count
            FROM subjects s
            LEFT JOIN student_subjects ss ON s.id = ss.subject_id
            WHERE s.teacher_id = ?
            GROUP BY s.id
            ORDER BY s.semester, s.name
        ''', (self.user_data['teacher_id'],))

        subjects = self.db_manager.cursor.fetchall()

        # Таблица
        tree_frame = ttk.Frame(self.content_frame)
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)

        columns = ('ID', 'Название', 'Часы', 'Семестр', 'Тип', 'Студентов')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor='center')

        tree.column('Название', width=200)

        for subject in subjects:
            tree.insert('', 'end', values=(subject[0], subject[1], subject[2],
                                           subject[3] if subject[3] else '-',
                                           subject[4], subject[5]))

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def show_performance(self):

        self.clear_content()

        title = ttk.Label(self.content_frame, text="Успеваемость студентов",
                          style='Title.TLabel')
        title.pack(pady=10)

        # Получаем успеваемость по предметам преподавателя
        self.db_manager.cursor.execute('''
            SELECT s.name as subject_name,
                   st.last_name || ' ' || st.first_name as student_name,
                   st.group_name,
                   COUNT(g.id) as grades_count,
                   ROUND(AVG(g.grade), 2) as avg_grade,
                   MAX(g.date) as last_grade_date
            FROM subjects s
            JOIN grades g ON s.id = g.subject_id
            JOIN students st ON g.student_id = st.id
            WHERE s.teacher_id = ?
            GROUP BY s.id, st.id
            ORDER BY s.name, avg_grade DESC
        ''', (self.user_data['teacher_id'],))

        data = self.db_manager.cursor.fetchall()

        # Таблица
        tree_frame = ttk.Frame(self.content_frame)
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)

        columns = ('Предмет', 'Студент', 'Группа', 'Оценок', 'Средний балл', 'Последняя оценка')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        tree.column('Предмет', width=150)
        tree.column('Студент', width=150)

        for row in data:
            # Форматируем дату для отображения
            last_date = row[5]
            if last_date:
                try:
                    date_obj = datetime.strptime(last_date, '%Y-%m-%d')
                    last_date = date_obj.strftime('%d.%m.%Y')
                except:
                    pass

            tree.insert('', 'end', values=(row[0], row[1], row[2], row[3], row[4], last_date))

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    # ============== ФУНКЦИИ СТУДЕНТА ==============
    def show_my_grades(self):

        self.clear_content()

        title = ttk.Label(self.content_frame, text=" Мои оценки",
                          style='Title.TLabel')
        title.pack(pady=10)

        # Получаем оценки студента
        grades = self.db_manager.get_grades(self.user_data['student_id'])

        # Таблица
        tree_frame = ttk.Frame(self.content_frame)
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)

        columns = ('ID', 'Предмет', 'Оценка', 'Тип работы', 'Преподаватель', 'Дата', 'Комментарий')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        tree.column('ID', width=50)
        tree.column('Предмет', width=150)
        tree.column('Оценка', width=100, anchor='center')
        tree.column('Преподаватель', width=150)
        tree.column('Дата', width=100, anchor='center')
        tree.column('Комментарий', width=200)

        for grade in grades:
            # Форматируем дату для отображения
            date_str = grade[6]
            if date_str:
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    date_str = date_obj.strftime('%d.%m.%Y')
                except:
                    pass

            tree.insert('', 'end', values=(grade[0], grade[2], grade[3],
                                           grade[4], grade[5], date_str, grade[7]))

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Статистика
        if grades:
            # Извлекаем числовые оценки из текстовых значений
            numeric_grades = []
            for grade in grades:
                grade_text = grade[3]
                if grade_text and grade_text[0].isdigit():
                    numeric_grades.append(int(grade_text[0]))

            if numeric_grades:
                avg_grade = sum(numeric_grades) / len(numeric_grades)
                excellent = sum(1 for g in numeric_grades if g == 5)

                stats_frame = ttk.Frame(self.content_frame)
                stats_frame.pack(pady=10)

                ttk.Label(stats_frame,
                          text=f"Статистика: Средний балл: {avg_grade:.2f} | Отличных оценок: {excellent}",
                          font=("Arial", 11)).pack()

    def show_my_schedule(self):
        self.clear_content()

        title = ttk.Label(self.content_frame, text=" Мое расписание",
                          style='Title.TLabel')
        title.pack(pady=10)

        # Получаем расписание студента
        self.db_manager.cursor.execute('''
            SELECT DISTINCT sch.day_of_week, sch.start_time, sch.end_time, 
                   sub.name, t.last_name, t.first_name, sch.room
            FROM schedule sch
            JOIN subjects sub ON sch.subject_id = sub.id
            JOIN student_subjects ss ON sub.id = ss.subject_id
            LEFT JOIN teachers t ON sub.teacher_id = t.id
            WHERE ss.student_id = ?
            ORDER BY 
                CASE sch.day_of_week
                    WHEN 'пн' THEN 1
                    WHEN 'вт' THEN 2
                    WHEN 'ср' THEN 3
                    WHEN 'чт' THEN 4
                    WHEN 'пт' THEN 5
                    WHEN 'сб' THEN 6
                    ELSE 7
                END,
                sch.start_time
        ''', (self.user_data['student_id'],))

        schedule = self.db_manager.cursor.fetchall()

        # Таблица
        tree_frame = ttk.Frame(self.content_frame)
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)

        columns = ('День', 'Начало', 'Конец', 'Предмет', 'Преподаватель', 'Аудитория')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        tree.column('Предмет', width=150)
        tree.column('Преподаватель', width=150)

        days_russian = {'пн': 'Понедельник', 'вт': 'Вторник', 'ср': 'Среда',
                        'чт': 'Четверг', 'пт': 'Пятница', 'сб': 'Суббота'}

        for item in schedule:
            day_russian = days_russian.get(item[0], item[0])
            teacher_name = f"{item[4]} {item[5]}" if item[4] else "Не назначен"
            tree.insert('', 'end', values=(day_russian, item[1], item[2],
                                           item[3], teacher_name, item[6]))

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def show_my_info(self):
        """Показать мои данные"""
        self.clear_content()

        title = ttk.Label(self.content_frame, text="👤 Мои данные",
                          style='Title.TLabel')
        title.pack(pady=20)

        # Получаем данные студента
        self.db_manager.cursor.execute('''
            SELECT * FROM students WHERE id = ?
        ''', (self.user_data['student_id'],))

        student = self.db_manager.cursor.fetchone()

        if student:
            info_frame = ttk.Frame(self.content_frame, padding=20)
            info_frame.pack()

            # Форматируем дату поступления
            enrollment_date = student[8]
            if enrollment_date:
                try:
                    date_obj = datetime.strptime(enrollment_date, '%Y-%m-%d')
                    enrollment_date = date_obj.strftime('%d.%m.%Y')
                except:
                    pass

            info_text = f"""
            Личная информация:

            ФИО: {student[1]} {student[2]} {student[3] or ''}
            Группа: {student[4]}
            Телефон: {student[5] or 'Не указан'}
            Email: {student[6] or 'Не указан'}
            Статус: {student[7]}
            Дата поступления: {enrollment_date}
            """

            ttk.Label(info_frame, text=info_text,
                      font=("Arial", 12), justify='left').pack()

    def show_my_performance(self):

        self.clear_content()

        title = ttk.Label(self.content_frame, text="Моя успеваемость",
                          style='Title.TLabel')
        title.pack(pady=10)

        # Получаем статистику по предметам
        self.db_manager.cursor.execute('''
            SELECT sub.name, 
                   COUNT(g.id) as grades_count,
                   ROUND(AVG(g.grade), 2) as avg_grade,
                   MIN(g.grade) as min_grade,
                   MAX(g.grade) as max_grade,
                   COUNT(CASE WHEN g.grade = 5 THEN 1 END) as excellent_count
            FROM subjects sub
            JOIN grades g ON sub.id = g.subject_id
            WHERE g.student_id = ?
            GROUP BY sub.id
            ORDER BY avg_grade DESC
        ''', (self.user_data['student_id'],))

        data = self.db_manager.cursor.fetchall()

        # Таблица
        tree_frame = ttk.Frame(self.content_frame)
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)

        columns = ('Предмет', 'Оценок', 'Средний балл', 'Минимум', 'Максимум', 'Отлично')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings')

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor='center')

        tree.column('Предмет', width=150)

        for row in data:
            tree.insert('', 'end', values=row)

        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    # ============== ОБЩИЕ ФУНКЦИИ ==============
    def clear_content(self):
        """Очистка контентной области"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def logout(self):
        """Выход из системы"""
        if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти?"):
            self.root.destroy()
            start_application()


def start_application():
    """Запуск приложения"""
    # Создаем главное окно
    root = tk.Tk()

    # Создаем менеджер базы данных
    db_manager = DatabaseManager()

    # Функция для обработки успешного входа
    def on_login_success(user_data):
        # Закрываем окно входа
        for widget in root.winfo_children():
            widget.destroy()

        # Запускаем главное приложение
        app = MainApplication(root, db_manager, user_data)

    # Показываем окно входа
    login_window = LoginWindow(root, db_manager, on_login_success)

    root.mainloop()


def main():
    """Главная функция"""
    print("=" * 60)
    print("СИСТЕМА ОНЛАЙН-ОБУЧЕНИЯ")
    print("Электронный журнал с полным CRUD функционалом")
    print("=" * 60)
    print()
    print("Особенности системы:")
    print("• 3 роли: Студент, Преподаватель, Администратор")
    print("• Полный CRUD для всех сущностей")
    print("• База данных SQLite с тестовыми данными")
    print("• Графический интерфейс на Tkinter")
    print("• Статистика и отчеты")
    print("• Поиск и фильтрация данных")
    print()

    start_application()


if __name__ == "__main__":
    main()