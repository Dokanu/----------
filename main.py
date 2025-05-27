import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import matplotlib.pyplot as plt
from db import Database

class App(tk.Tk):
    def __init__(self, db_dsn):
        super().__init__()
        self.title("Автошкола")
        self.geometry("1000x700")
        self.db = Database(db_dsn)
        self.create_widgets()

    def create_widgets(self):
        tab = ttk.Notebook(self)
        self.table_tab = TableTab(tab, self.db)
        self.rel_tab   = RelationTab(tab, self.db)
        self.view_tab  = ViewTab(tab, self.db)
        self.chart_tab = ChartTab(tab, self.db)
        self.query_tab = QueryTab(tab, self.db)

        tab.add(self.table_tab, text="Таблицы")
        tab.add(self.rel_tab,   text="Связи 1-N")
        tab.add(self.view_tab,  text="Представления")
        tab.add(self.chart_tab, text="Диаграмма")
        tab.add(self.query_tab, text="Запросы")
        tab.pack(fill='both', expand=True)

class TableTab(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.table_names = self._load_table_names()
        self.current_data = []
        self.create_ui()

    def _load_table_names(self):
        rows = self.db.fetch_all(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='public';"
        )
        allowed = []
        for r in rows:
            t = r['table_name']
            cols = self.db.fetch_all(
                "SELECT column_name FROM information_schema.columns WHERE table_name=%s;", [t]
            )
            if any(not c['column_name'].endswith('_id') for c in cols):
                allowed.append(t)
        return allowed

    def create_ui(self):
        top = ttk.Frame(self); top.pack(fill='x', pady=5)
        self.table_cb = ttk.Combobox(top, values=self.table_names, state='readonly')
        self.table_cb.current(0); self.table_cb.bind('<<ComboboxSelected>>', self.load_data)
        self.table_cb.pack(side='left', padx=5)

        self.search_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.search_var).pack(side='left', padx=5)
        ttk.Button(top, text="Поиск", command=self.search).pack(side='left', padx=5)
        ttk.Button(top, text="Добавить", command=self.add_record).pack(side='left', padx=5)
        ttk.Button(top, text="Редактировать", command=self.edit_record).pack(side='left', padx=5)
        ttk.Button(top, text="Удалить", command=self.delete_record).pack(side='left', padx=5)

        # Добавим скроллируемую таблицу
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill='both', expand=True)

        y_scroll = ttk.Scrollbar(tree_frame, orient='vertical')
        x_scroll = ttk.Scrollbar(tree_frame, orient='horizontal')

        self.tree = ttk.Treeview(tree_frame, show='headings', yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        self.tree.pack(side='left', fill='both', expand=True)

        y_scroll.config(command=self.tree.yview)
        y_scroll.pack(side='right', fill='y')

        x_scroll.config(command=self.tree.xview)
        x_scroll.pack(side='bottom', fill='x')

        self.load_data()

    def load_data(self, event=None):
        table = self.table_cb.get()
        self.current_data = self.db.fetch_all(f"SELECT * FROM {table};")
        self._display(self.current_data)

    def _display(self, data):
        self.tree.delete(*self.tree.get_children())
        if not data:
            self.tree['columns'] = []; return
        cols = [c for c in data[0].keys() if not c.endswith('_id')]
        self.tree['columns'] = cols
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=120)
        for row in data:
            self.tree.insert('', 'end', values=[row[c] for c in cols])

    def search(self):
        term, table = self.search_var.get().lower(), self.table_cb.get()
        try:
            rows = self.db.call_function(f"search_{table}_by_name", [f"%{term}%"])
        except:
            rows = [r for r in self.current_data
                    if any(isinstance(v,str) and term in v.lower() for v in r.values())]
        self._display(rows)

    def add_record(self):
        ...

    def edit_record(self):
        ...

    def delete_record(self):
        ...

class RelationTab(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        ttk.Label(self, text="Составная форма 1-N пока не реализована").pack(padx=10, pady=10)

class ViewTab(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        views = [r['table_name'] for r in db.fetch_all(
            "SELECT table_name FROM information_schema.views WHERE table_schema='public';"
        )]
        self.view_cb = ttk.Combobox(self, values=views, state='readonly')
        self.view_cb.current(0); self.view_cb.pack(padx=5, pady=5)
        ttk.Button(self, text="Показать", command=self.show).pack()

        # Слайдеры
        frame = ttk.Frame(self)
        frame.pack(fill='both', expand=True)

        y_scroll = ttk.Scrollbar(frame, orient='vertical')
        x_scroll = ttk.Scrollbar(frame, orient='horizontal')

        self.tree = ttk.Treeview(frame, show='headings', yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        self.tree.pack(side='left', fill='both', expand=True)

        y_scroll.config(command=self.tree.yview)
        y_scroll.pack(side='right', fill='y')

        x_scroll.config(command=self.tree.xview)
        x_scroll.pack(side='bottom', fill='x')

    def show(self):
        v = self.view_cb.get()
        data = self.db.fetch_all(f"SELECT * FROM {v};")
        self.tree.delete(*self.tree.get_children())
        if not data: return
        cols = list(data[0].keys()); self.tree['columns'] = cols
        for c in cols: self.tree.heading(c, text=c)
        for r in data: self.tree.insert('', 'end', values=[r[c] for c in cols])

class ChartTab(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        ttk.Button(self, text="Статистика курсов", command=self.plot).pack(pady=5)
        ttk.Button(self, text="Экспорт в Excel", command=self.export).pack(pady=5)

    def plot(self):
        df = pd.DataFrame(self.db.call_function('get_course_statistics'))
        plt.figure(); plt.bar(df.index, df['total_courses']); plt.title("Всего курсов"); plt.show()

    def export(self):
        df = pd.DataFrame(self.db.call_function('get_school_course_stats'))
        path = filedialog.asksaveasfilename(defaultextension='.xlsx')
        if path:
            df.to_excel(path, index=False)
            messagebox.showinfo("Экспорт", "Данные экспортированы")

class QueryTab(ttk.Frame):
    ALLOWED = [
        'get_lessons_for_course',
        'get_students_for_stream',
        'get_lessons_by_date_range',
        'get_reviews_by_date_range',
        'get_car_and_brand',
        'get_course_and_school',
        'get_enrollment_and_group',
        'get_all_courses_with_enrollments',
        'get_all_streams_with_groups',
        'get_active_course_details',
        'get_course_statistics',
        'get_school_course_stats',
        'get_courses_above_price',
        'get_students_by_name_mask',
        'get_courses_using_index',
        'get_courses_no_index',
        'get_course_counts_by_district',
        'get_top_rated_long_courses',
        'get_top_instructors',
        'get_school_year_stats',
        'get_all_districts_and_schools',
        'get_applications_by_school_and_district',
        'get_applications_income',
        'get_review_summary'
    ]
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        allf = [r['routine_name'] for r in db.fetch_all(
            "SELECT routine_name FROM information_schema.routines "
            "WHERE routine_schema='public' AND routine_type='FUNCTION';"
        )]
        self.functions = [f for f in allf if f in self.ALLOWED]
        self.func_cb = ttk.Combobox(self, values=self.functions, state='readonly')
        if self.functions: self.func_cb.current(0)
        self.func_cb.pack(padx=5, pady=5)
        ttk.Button(self, text="Выполнить", command=self.run).pack(pady=5)

        # Слайдеры
        frame = ttk.Frame(self)
        frame.pack(fill='both', expand=True)

        y_scroll = ttk.Scrollbar(frame, orient='vertical')
        x_scroll = ttk.Scrollbar(frame, orient='horizontal')

        self.tree = ttk.Treeview(frame, show='headings', yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        self.tree.pack(side='left', fill='both', expand=True)

        y_scroll.config(command=self.tree.yview)
        y_scroll.pack(side='right', fill='y')

        x_scroll.config(command=self.tree.xview)
        x_scroll.pack(side='bottom', fill='x')

    def run(self):
        fn = self.func_cb.get()
        try:
            data = self.db.call_function(fn)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e)); return
        self.tree.delete(*self.tree.get_children())
        if not data:
            self.tree['columns'] = []; return
        cols = list(data[0].keys()); self.tree['columns'] = cols
        for c in cols:
            self.tree.heading(c, text=c); self.tree.column(c, width=120)
        for r in data:
            self.tree.insert('', 'end', values=[r[c] for c in cols])

if __name__ == '__main__':
    DSN = "host=localhost dbname=kurs_bd user=postgres password=admin2005"
    App(DSN).mainloop()
