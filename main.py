import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import matplotlib.pyplot as plt
from db import Database
from data_generator import *

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
        self.rel_tab = RelationTab(tab, self.db)
        self.view_tab = ViewTab(tab, self.db)
        self.chart_tab = ChartTab(tab, self.db)
        self.query_tab = QueryTab(tab, self.db)

        tab.add(self.table_tab, text="Таблицы")
        tab.add(self.rel_tab, text="Связи 1-N")
        tab.add(self.view_tab, text="Представления")
        tab.add(self.chart_tab, text="Диаграмма")
        tab.add(self.query_tab, text="Запросы")
        tab.pack(fill='both', expand=True)

# --- TableTab (без изменений) ---
class TableTab(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.table_names = [r['table_name'] for r in db.fetch_all(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='public';")]
        self.current_data = []
        self.create_ui()

    def create_ui(self):
        top = ttk.Frame(self)
        top.pack(fill='x', pady=5)
        self.table_cb = ttk.Combobox(top, values=self.table_names, state='readonly')
        self.table_cb.current(0)
        self.table_cb.bind('<<ComboboxSelected>>', self.load_data)
        self.table_cb.pack(side='left', padx=5)
        self.search_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.search_var).pack(side='left', padx=5)
        ttk.Button(top, text="Поиск", command=self.search).pack(side='left', padx=5)
        ttk.Button(top, text="Добавить", command=self.add_record).pack(side='left', padx=5)
        ttk.Button(top, text="Редактировать", command=self.edit_record).pack(side='left', padx=5)
        ttk.Button(top, text="Удалить", command=self.delete_record).pack(side='left', padx=5)
        self.tree = ttk.Treeview(self, show='headings')
        self.tree.pack(fill='both', expand=True)
        self.load_data()

    def load_data(self, event=None):
        table = self.table_cb.get()
        rows = self.db.fetch_all(f"SELECT * FROM {table};")
        self.current_data = rows
        self.display_data(rows)

    def display_data(self, data):
        self.tree.delete(*self.tree.get_children())
        if not data:
            self.tree['columns'] = []
            return
        all_cols = list(data[0].keys())
        display_cols = [c for c in all_cols if not c.endswith('_id')]
        self.tree['columns'] = display_cols
        for c in display_cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=100)
        for row in data:
            values = [row[c] for c in display_cols]
            self.tree.insert('', 'end', values=values)

    def search(self):
        term = self.search_var.get().strip()
        table = self.table_cb.get()
        func_name = f"search_{table}_by_name"
        try:
            rows = self.db.call_function(func_name, [f"%{term}%"])
        except Exception:
            pattern = term.lower()
            rows = [r for r in self.current_data if any(
                isinstance(v, str) and pattern in v.lower() for v in r.values())]
        self.display_data(rows)

    def add_record(self):
        table = self.table_cb.get()
        cols = [col['column_name'] for col in self.db.fetch_all(
            "SELECT column_name FROM information_schema.columns WHERE table_name=%s;", [table])]
        data_cols = [c for c in cols if not c.endswith('_id')]
        dlg = tk.Toplevel(self)
        dlg.title(f"Добавить запись в {table}")
        entries = {}
        for i, c in enumerate(data_cols):
            ttk.Label(dlg, text=c).grid(row=i, column=0, sticky='w')
            ent = ttk.Entry(dlg)
            ent.grid(row=i, column=1)
            entries[c] = ent
        def save_new():
            cols_sql = ','.join(data_cols)
            vals_sql = ','.join(['%s']*len(data_cols))
            params = [entries[c].get() for c in data_cols]
            self.db.execute(f"INSERT INTO {table} ({cols_sql}) VALUES ({vals_sql});", params)
            dlg.destroy(); self.load_data()
        ttk.Button(dlg, text="Сохранить", command=save_new).grid(row=len(data_cols), column=0, columnspan=2)

    def edit_record(self):
        sel = self.tree.selection()
        if not sel: return
        idx = self.tree.index(sel[0])
        orig = self.current_data[idx]
        table = self.table_cb.get()
        cols = [col['column_name'] for col in self.db.fetch_all(
            "SELECT column_name FROM information_schema.columns WHERE table_name=%s;", [table])]
        data_cols = [c for c in cols if not c.endswith('_id')]
        dlg = tk.Toplevel(self)
        dlg.title(f"Редактировать запись {table}")
        entries = {}
        for i, c in enumerate(data_cols):
            ttk.Label(dlg, text=c).grid(row=i, column=0, sticky='w')
            ent = ttk.Entry(dlg); ent.insert(0, orig[c]); ent.grid(row=i, column=1)
            entries[c] = ent
        def save_edit():
            set_sql = ','.join([f"{c}=%s" for c in data_cols])
            params = [entries[c].get() for c in data_cols]
            key = table + '_id'; params.append(orig[key])
            self.db.execute(f"UPDATE {table} SET {set_sql} WHERE {key}=%s;", params)
            dlg.destroy(); self.load_data()
        ttk.Button(dlg, text="Сохранить", command=save_edit).grid(row=len(data_cols), column=0, columnspan=2)

    def delete_record(self):
        sel = self.tree.selection()
        if not sel: return
        idx = self.tree.index(sel[0]); orig = self.current_data[idx]
        table = self.table_cb.get(); key = table + '_id'
        if messagebox.askyesno("Подтвердить", "Удалить выбранную запись?"):
            self.db.execute(f"DELETE FROM {table} WHERE {key}=%s;", [orig[key]])
            self.load_data()

# --- RelationTab ---
class RelationTab(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        ttk.Label(self, text="Составная форма пока не реализована").pack(padx=10, pady=10)

# --- ViewTab ---
class ViewTab(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        views = [r['table_name'] for r in db.fetch_all(
            "SELECT table_name FROM information_schema.views WHERE table_schema='public';")]
        self.view_cb = ttk.Combobox(self, values=views, state='readonly')
        self.view_cb.current(0); self.view_cb.pack(padx=5, pady=5)
        ttk.Button(self, text="Показать", command=self.show_view).pack()
        self.tree = ttk.Treeview(self, show='headings')
        self.tree.pack(fill='both', expand=True)

    def show_view(self):
        v = self.view_cb.get()
        data = self.db.fetch_all(f"SELECT * FROM {v};")
        self.tree.delete(*self.tree.get_children())
        if not data: return
        cols = list(data[0].keys()); self.tree['columns'] = cols
        for c in cols: self.tree.heading(c, text=c)
        for row in data: self.tree.insert('', 'end', values=[row[c] for c in cols])

# --- ChartTab ---
class ChartTab(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        ttk.Button(self, text="Показать статистику курсов", command=self.plot_stats).pack(pady=5)
        ttk.Button(self, text="Экспорт в Excel", command=self.export_excel).pack(pady=5)

    def plot_stats(self):
        data = self.db.call_function('get_course_statistics')
        df = pd.DataFrame(data)
        plt.figure()
        plt.bar(df.index, df['total_courses'])
        plt.title("Общее число курсов")
        plt.show()

    def export_excel(self):
        data = self.db.call_function('get_school_course_stats')
        df = pd.DataFrame(data)
        file = filedialog.asksaveasfilename(defaultextension='.xlsx')
        if file:
            df.to_excel(file, index=False)
            messagebox.showinfo("Экспорт", "Данные экспортированы")

# --- QueryTab (новая вкладка) ---
class QueryTab(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.functions = self.get_functions()
        self.func_cb = ttk.Combobox(self, values=self.functions, state='readonly')
        self.func_cb.current(0)
        self.func_cb.pack(padx=5, pady=5)
        ttk.Button(self, text="Выполнить", command=self.execute_function).pack(pady=5)
        self.tree = ttk.Treeview(self, show='headings')
        self.tree.pack(fill='both', expand=True)

    def get_functions(self):
        # Получение пользовательских функций из базы данных
        rows = self.db.fetch_all("""
            SELECT routine_name
            FROM information_schema.routines
            WHERE routine_schema = 'public' AND routine_type = 'FUNCTION';
        """)
        return [r['routine_name'] for r in rows]

    def execute_function(self):
        func = self.func_cb.get()
        try:
            data = self.db.call_function(func)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при выполнении функции:\n{e}")
            return

        self.tree.delete(*self.tree.get_children())
        if not data:
            self.tree['columns'] = []
            return
        cols = list(data[0].keys())
        self.tree['columns'] = cols
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=120)
        for row in data:
            self.tree.insert('', 'end', values=[row[c] for c in cols])

# --- Запуск приложения ---
if __name__ == '__main__':
    DSN = "host=localhost dbname=kurs_bd user=postgres password=admin2005"
    app = App(DSN)
    app.mainloop()
