"""
gui.py — весь GUI-код приложения «Random Quote Generator» на tkinter.
"""

import tkinter as tk
from tkinter import ttk, messagebox

import history as hist_module
import quotes as quotes_module

# Размеры окна по умолчанию
DEFAULT_WIDTH = 850
DEFAULT_HEIGHT = 700
MIN_WIDTH = 700
MIN_HEIGHT = 600
# Отступ для переноса текста цитаты (оставляем поля по ~55px с каждой стороны)
QUOTE_WRAP_LENGTH = DEFAULT_WIDTH - 110


class App(tk.Tk):
    """Главное окно приложения."""

    def __init__(self):
        super().__init__()
        self.title("Random Quote Generator")
        self.geometry(f"{DEFAULT_WIDTH}x{DEFAULT_HEIGHT}")
        self.minsize(MIN_WIDTH, MIN_HEIGHT)
        self.resizable(True, True)

        # Пул цитат
        self.pool = quotes_module.QuotePool()

        # История (загружаем из файла)
        self.history: list = hist_module.load_history()

        self._build_ui()
        self._refresh_filters()
        self._reload_history_list()

    # ------------------------------------------------------------------ #
    #  Построение интерфейса                                               #
    # ------------------------------------------------------------------ #

    def _build_ui(self):
        """Строит все виджеты."""
        self.configure(bg="#f0f4f8")

        # --- Заголовок ---
        title_lbl = tk.Label(
            self,
            text="✨ Random Quote Generator",
            font=("Helvetica", 20, "bold"),
            bg="#f0f4f8",
            fg="#2d3748",
        )
        title_lbl.pack(pady=(18, 6))

        # --- Фреймы ---
        top_frame = tk.Frame(self, bg="#f0f4f8")
        top_frame.pack(fill="x", padx=20)

        center_frame = tk.LabelFrame(
            self, text="Цитата", font=("Helvetica", 11, "bold"),
            bg="#f0f4f8", fg="#4a5568", padx=12, pady=12,
        )
        center_frame.pack(fill="x", padx=20, pady=(8, 4))

        mid_frame = tk.Frame(self, bg="#f0f4f8")
        mid_frame.pack(fill="x", padx=20, pady=4)

        bottom_frame = tk.LabelFrame(
            self, text="История цитат", font=("Helvetica", 11, "bold"),
            bg="#f0f4f8", fg="#4a5568", padx=8, pady=8,
        )
        bottom_frame.pack(fill="both", expand=True, padx=20, pady=(4, 8))

        # --- Фильтры (top_frame) ---
        self._build_filters(top_frame)

        # --- Отображение цитаты (center_frame) ---
        self._build_quote_display(center_frame)

        # --- Кнопка генерации + форма добавления (mid_frame) ---
        self._build_action_buttons(mid_frame)

        # --- История (bottom_frame) ---
        self._build_history(bottom_frame)

    def _build_filters(self, parent):
        """Строит виджеты фильтрации."""
        tk.Label(parent, text="Фильтр по автору:", bg="#f0f4f8", fg="#4a5568").grid(
            row=0, column=0, sticky="w", padx=(0, 4), pady=4
        )
        self.author_var = tk.StringVar(value="Все")
        self.author_cb = ttk.Combobox(
            parent, textvariable=self.author_var, state="readonly", width=28
        )
        self.author_cb.grid(row=0, column=1, sticky="w", padx=(0, 20), pady=4)

        tk.Label(parent, text="Фильтр по теме:", bg="#f0f4f8", fg="#4a5568").grid(
            row=0, column=2, sticky="w", padx=(0, 4), pady=4
        )
        self.topic_var = tk.StringVar(value="Все")
        self.topic_cb = ttk.Combobox(
            parent, textvariable=self.topic_var, state="readonly", width=20
        )
        self.topic_cb.grid(row=0, column=3, sticky="w", padx=(0, 20), pady=4)

        reset_btn = tk.Button(
            parent,
            text="Сбросить фильтры",
            command=self._reset_filters,
            bg="#e2e8f0",
            fg="#2d3748",
            relief="flat",
            cursor="hand2",
            padx=8,
        )
        reset_btn.grid(row=0, column=4, sticky="w", pady=4)

    def _build_quote_display(self, parent):
        """Строит область отображения цитаты."""
        self.quote_text_lbl = tk.Label(
            parent,
            text="Нажмите «Сгенерировать цитату»",
            font=("Helvetica", 15, "italic"),
            bg="#ffffff",
            fg="#2d3748",
            wraplength=QUOTE_WRAP_LENGTH,
            justify="center",
            relief="flat",
            padx=16,
            pady=16,
        )
        self.quote_text_lbl.pack(fill="x", pady=(0, 8))

        self.quote_info_lbl = tk.Label(
            parent,
            text="",
            font=("Helvetica", 11),
            bg="#f0f4f8",
            fg="#718096",
        )
        self.quote_info_lbl.pack()

    def _build_action_buttons(self, parent):
        """Строит кнопку генерации и форму добавления цитаты."""
        gen_btn = tk.Button(
            parent,
            text="🎲  Сгенерировать цитату",
            command=self._generate_quote,
            font=("Helvetica", 13, "bold"),
            bg="#4299e1",
            fg="white",
            relief="flat",
            cursor="hand2",
            padx=18,
            pady=8,
        )
        gen_btn.pack(side="left", padx=(0, 20))

        # --- Форма добавления цитаты ---
        add_frame = tk.LabelFrame(
            parent, text="Добавить новую цитату",
            font=("Helvetica", 10, "bold"),
            bg="#f0f4f8", fg="#4a5568", padx=8, pady=6,
        )
        add_frame.pack(side="left", fill="x", expand=True)

        # Поле «Текст»
        tk.Label(add_frame, text="Текст:", bg="#f0f4f8", fg="#4a5568").grid(
            row=0, column=0, sticky="w"
        )
        self.new_text_var = tk.StringVar()
        tk.Entry(add_frame, textvariable=self.new_text_var, width=38).grid(
            row=0, column=1, sticky="ew", padx=(4, 8)
        )

        # Поле «Автор»
        tk.Label(add_frame, text="Автор:", bg="#f0f4f8", fg="#4a5568").grid(
            row=0, column=2, sticky="w"
        )
        self.new_author_var = tk.StringVar()
        tk.Entry(add_frame, textvariable=self.new_author_var, width=18).grid(
            row=0, column=3, sticky="ew", padx=(4, 8)
        )

        # Поле «Тема»
        tk.Label(add_frame, text="Тема:", bg="#f0f4f8", fg="#4a5568").grid(
            row=0, column=4, sticky="w"
        )
        self.new_topic_var = tk.StringVar()
        tk.Entry(add_frame, textvariable=self.new_topic_var, width=14).grid(
            row=0, column=5, sticky="ew", padx=(4, 8)
        )

        tk.Button(
            add_frame,
            text="Добавить",
            command=self._add_quote,
            bg="#48bb78",
            fg="white",
            relief="flat",
            cursor="hand2",
            padx=8,
        ).grid(row=0, column=6, padx=(4, 0))

    def _build_history(self, parent):
        """Строит прокручиваемый список истории."""
        scrollbar = tk.Scrollbar(parent, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        self.history_listbox = tk.Listbox(
            parent,
            yscrollcommand=scrollbar.set,
            font=("Courier", 10),
            bg="#ffffff",
            fg="#2d3748",
            selectbackground="#bee3f8",
            activestyle="none",
            relief="flat",
            bd=0,
        )
        self.history_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.history_listbox.yview)

    # ------------------------------------------------------------------ #
    #  Логика                                                              #
    # ------------------------------------------------------------------ #

    def _refresh_filters(self):
        """Обновляет выпадающие списки фильтров на основе текущего пула."""
        authors = ["Все"] + self.pool.get_authors()
        topics = ["Все"] + self.pool.get_topics()
        self.author_cb["values"] = authors
        self.topic_cb["values"] = topics

    def _reset_filters(self):
        """Сбрасывает фильтры на «Все»."""
        self.author_var.set("Все")
        self.topic_var.set("Все")

    def _generate_quote(self):
        """Генерирует случайную цитату с учётом фильтров и добавляет в историю."""
        author_filter = self.author_var.get()
        topic_filter = self.topic_var.get()

        author = None if author_filter == "Все" else author_filter
        topic = None if topic_filter == "Все" else topic_filter

        quote = self.pool.get_random_quote(author=author, topic=topic)

        if quote is None:
            messagebox.showwarning(
                "Нет цитат",
                "По выбранным фильтрам не найдено ни одной цитаты.\n"
                "Попробуйте изменить фильтры или добавить новую цитату.",
            )
            return

        # Отображаем цитату
        self.quote_text_lbl.config(text=f'"{quote["text"]}"')
        self.quote_info_lbl.config(
            text=f'— {quote["author"]}   |   Тема: {quote["topic"]}'
        )

        # Добавляем в историю и сохраняем
        entry = hist_module.make_entry(
            text=quote["text"],
            author=quote["author"],
            topic=quote["topic"],
        )
        self.history.append(entry)
        hist_module.save_history(self.history)
        self._append_history_item(entry)

    def _add_quote(self):
        """Добавляет новую цитату, введённую пользователем."""
        text = self.new_text_var.get().strip()
        author = self.new_author_var.get().strip()
        topic = self.new_topic_var.get().strip()

        if not text or not author or not topic:
            messagebox.showerror(
                "Ошибка валидации",
                "Все поля (Текст, Автор, Тема) обязательны для заполнения.",
            )
            return

        self.pool.add_quote(text=text, author=author, topic=topic)
        self._refresh_filters()

        # Очищаем поля
        self.new_text_var.set("")
        self.new_author_var.set("")
        self.new_topic_var.set("")

        messagebox.showinfo("Успех", "Цитата успешно добавлена в пул!")

    def _append_history_item(self, entry: dict):
        """Добавляет одну запись в конец виджета истории."""
        line = (
            f"[{entry.get('timestamp', '')}]  "
            f"{entry['author']} | {entry['topic']}\n"
            f"   «{entry['text']}»"
        )
        self.history_listbox.insert("end", line)
        self.history_listbox.insert("end", "")  # пустая строка-разделитель
        self.history_listbox.yview("end")

    def _reload_history_list(self):
        """Заполняет виджет истории при запуске из загруженных данных."""
        self.history_listbox.delete(0, "end")
        for entry in self.history:
            self._append_history_item(entry)
