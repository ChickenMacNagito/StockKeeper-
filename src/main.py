"""StockKeeper - Центрированный интерфейс, без значков."""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle

from models import Item
from storage import save_data, load_data

Window.clearcolor = (0.95, 0.95, 0.96, 1)

COL_NAME = 0.40
COL_QTY = 0.12
COL_PRICE = 0.15
COL_SUM = 0.15
COL_ACTIONS = 0.18


class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(30)  # Увеличены отступы для центрирования
        self.spacing = dp(20)
        self.items = []
        self.editing_item = None
        self.table_body = BoxLayout(orientation='vertical', spacing=dp(1))
        self._init_ui()
        Clock.schedule_once(self._load_data, 0.1)

    def _init_ui(self):
        """Создание интерфейса приложения."""
        
        # 1. Заголовок приложения (по центру)
        self.add_widget(Label(
            text='STOCKKEEPER',
            font_size=dp(26),
            bold=True,
            size_hint_y=None,
            height=dp(50),
            color=(0.1, 0.15, 0.25, 1),
            halign='center'
        ))

        # 2. Панель ввода данных (центрированная)
        input_panel = BoxLayout(
            orientation='vertical', 
            spacing=dp(10), 
            size_hint_y=None, 
            height=dp(140),
            padding=(dp(40), 0)  # Отступы по бокам для центрирования
        )
        
        self.name_input = TextInput(
            hint_text='Название товара',
            multiline=False,
            font_size=dp(15),
            size_hint_y=None,
            height=dp(45),
            background_color=(1, 1, 1, 1),
            foreground_color=(0.1, 0.15, 0.25, 1),
            cursor_color=(0.2, 0.4, 0.8, 1)
        )
        input_panel.add_widget(self.name_input)

        row_inputs = BoxLayout(spacing=dp(15))
        self.qty_input = TextInput(
            hint_text='Количество',
            input_filter='int',
            multiline=False,
            font_size=dp(15),
            size_hint_y=None,
            height=dp(45),
            background_color=(1, 1, 1, 1),
            foreground_color=(0.1, 0.15, 0.25, 1)
        )
        self.price_input = TextInput(
            hint_text='Цена за единицу',
            input_filter='float',
            multiline=False,
            font_size=dp(15),
            size_hint_y=None,
            height=dp(45),
            background_color=(1, 1, 1, 1),
            foreground_color=(0.1, 0.15, 0.25, 1)
        )
        row_inputs.add_widget(self.qty_input)
        row_inputs.add_widget(self.price_input)
        input_panel.add_widget(row_inputs)
        self.add_widget(input_panel)

        # 3. Кнопка "Добавить товар" (по центру)
        btn_container = BoxLayout(
            size_hint_y=None, 
            height=dp(50),
            padding=(dp(60), 0)  # Большие отступы для центрирования кнопки
        )
        
        self.action_btn = Button(
            text='ДОБАВИТЬ ТОВАР',
            font_size=dp(15),
            bold=True,
            background_color=(0.2, 0.5, 0.8, 1),
            background_normal='',
            background_down='',
            color=(1, 1, 1, 1)
        )
        self.action_btn.bind(on_release=self._on_action)
        
        btn_container.add_widget(self.action_btn)
        self.add_widget(btn_container)

        # Кнопка отмены (скрыта по умолчанию)
        self.cancel_btn = Button(
            text='ОТМЕНА РЕДАКТИРОВАНИЯ',
            font_size=dp(14),
            background_color=(0.7, 0.7, 0.75, 1),
            background_normal='',
            background_down='',
            color=(0.1, 0.1, 0.1, 1),
            size_hint_y=None,
            height=dp(40),
            opacity=0
        )
        self.cancel_btn.bind(on_release=self._cancel_edit)
        self.add_widget(self.cancel_btn)

        # 🔍 4. ПОЛЕ ПОИСКА (без значков, по центру)
        search_container = BoxLayout(
            size_hint_y=None,
            height=dp(45),
            padding=(dp(40), 0)
        )
        
        self.search_input = TextInput(
            hint_text='Поиск по названию...',
            multiline=False,
            font_size=dp(14),
            size_hint_y=None,
            height=dp(45),
            background_color=(0.97, 0.98, 1, 1),
            foreground_color=(0.1, 0.15, 0.25, 1),
            cursor_color=(0.2, 0.4, 0.8, 1)
        )
        self.search_input.bind(text=self._apply_search)
        search_container.add_widget(self.search_input)
        self.add_widget(search_container)

        # 5. Заголовок Таблицы (по центру с отступами)
        header_container = BoxLayout(
            size_hint_y=None, 
            height=dp(35), 
            padding=(dp(15), 0)
        )
        with header_container.canvas.before:
            Color(0.85, 0.87, 0.90, 1)
            Rectangle(pos=header_container.pos, size=header_container.size)
        
        headers = [
            ('Наименование', COL_NAME, 'left'),
            ('Кол-во', COL_QTY, 'center'),
            ('Цена', COL_PRICE, 'center'),
            ('Сумма', COL_SUM, 'center'),
            ('Действия', COL_ACTIONS, 'center')
        ]
        
        for text, size, align in headers:
            header_container.add_widget(Label(
                text=text,
                font_size=dp(13),
                bold=True,
                color=(0.1, 0.1, 0.1, 1),
                halign=align,
                size_hint_x=size
            ))
        self.add_widget(header_container)

        # 6. Тело Таблицы (по центру с отступами)
        table_container = BoxLayout(
            size_hint_y=0.5,
            padding=(dp(15), 0)
        )
        scroll = ScrollView()
        scroll.add_widget(self.table_body)
        table_container.add_widget(scroll)
        self.add_widget(table_container)

        # 7. Итоговая панель (по центру)
        summary_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(60),
            padding=(dp(20), dp(10), dp(20), dp(10))
        )
        with summary_container.canvas.before:
            Color(0.92, 0.94, 0.96, 1)
            Rectangle(pos=summary_container.pos, size=summary_container.size)

        self.total_label = Label(
            text='ОБЩАЯ СТОИМОСТЬ: 0.00 РУБ.',
            font_size=dp(20),
            bold=True,
            color=(0.1, 0.2, 0.5, 1),
            halign='center'
        )
        summary_container.add_widget(self.total_label)
        self.add_widget(summary_container)

    def _load_data(self, *args):
        try:
            self.items = load_data()
            self._refresh_view()
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            self.items = []

    def _on_action(self, *args):
        if self.editing_item:
            self._save_edit()
        else:
            self._add_item()

    def _add_item(self):
        name = self.name_input.text.strip()
        qty_text = self.qty_input.text.strip()
        price_text = self.price_input.text.strip()

        if not name:
            self._show_error('Введите название')
            return
        if not qty_text or not price_text:
            self._show_error('Заполните количество и цену')
            return
        
        try:
            qty = int(qty_text)
            price = float(price_text)
            if qty <= 0 or price <= 0:
                raise ValueError
        except ValueError:
            self._show_error('Значения должны быть числами больше нуля')
            return

        item = Item(name, qty, price)
        self.items.append(item)
        save_data(self.items)
        self._clear_inputs()
        self.search_input.text = ''
        self._refresh_view()

    def _edit_item(self, item):
        self.editing_item = item
        self.name_input.text = item.name
        self.qty_input.text = str(item.quantity)
        self.price_input.text = str(item.price)
        
        self.action_btn.text = 'СОХРАНИТЬ ИЗМЕНЕНИЯ'
        self.action_btn.background_color = (0.9, 0.6, 0.1, 1)
        self.cancel_btn.opacity = 1
        self.name_input.focus = True

    def _save_edit(self):
        name = self.name_input.text.strip()
        qty_text = self.qty_input.text.strip()
        price_text = self.price_input.text.strip()

        if not name or not qty_text or not price_text:
            self._show_error('Заполните все поля')
            return
        
        try:
            qty = int(qty_text)
            price = float(price_text)
            if qty <= 0 or price <= 0: raise ValueError
        except ValueError:
            self._show_error('Некорректные числа')
            return

        self.editing_item.name = name
        self.editing_item.quantity = qty
        self.editing_item.price = price
        
        save_data(self.items)
        self._cancel_edit()
        self._refresh_view()

    def _cancel_edit(self, *args):
        self.editing_item = None
        self._clear_inputs()
        self.action_btn.text = 'ДОБАВИТЬ ТОВАР'
        self.action_btn.background_color = (0.2, 0.5, 0.8, 1)
        self.cancel_btn.opacity = 0

    def _delete_item(self, item):
        if item in self.items:
            self.items.remove(item)
            save_data(self.items)
            self._refresh_view()

    def _apply_search(self, instance, value):
        """Фильтрация товаров по названию."""
        if not value.strip():
            self._refresh_view()
            return
        
        filtered = [item for item in self.items if value.lower() in item.name.lower()]
        self._refresh_view(filtered)

    def _refresh_view(self, items_list=None):
        """Построение таблицы и подсчет суммы."""
        self.table_body.clear_widgets()
        
        data = items_list if items_list is not None else self.items
        
        grand_total = 0.0

        if not data:
            msg = 'Ничего не найдено' if self.search_input.text.strip() else 'Список пуст'
            self.table_body.add_widget(Label(
                text=msg,
                color=(0.5, 0.5, 0.6, 1),
                italic=True,
                size_hint_y=None,
                height=dp(60)
            ))
        else:
            for idx, item in enumerate(data):
                row_sum = item.quantity * item.price
                grand_total += row_sum

                row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(1))
                
                bg_color = (1, 1, 1, 1) if idx % 2 == 0 else (0.96, 0.97, 0.99, 1)
                with row.canvas.before:
                    Color(*bg_color)
                    Rectangle(pos=row.pos, size=row.size)

                row.add_widget(Label(
                    text=item.name,
                    font_size=dp(14),
                    color=(0.1, 0.1, 0.1, 1),
                    halign='left',
                    size_hint_x=COL_NAME
                ))
                
                row.add_widget(Label(
                    text=str(item.quantity),
                    font_size=dp(13),
                    color=(0.3, 0.3, 0.3, 1),
                    halign='center',
                    size_hint_x=COL_QTY
                ))
                
                row.add_widget(Label(
                    text=f"{item.price:,.0f}".replace(',', ' '),
                    font_size=dp(13),
                    color=(0.3, 0.3, 0.3, 1),
                    halign='center',
                    size_hint_x=COL_PRICE
                ))
                
                row.add_widget(Label(
                    text=f"{row_sum:,.0f}".replace(',', ' '),
                    font_size=dp(14),
                    bold=True,
                    color=(0.1, 0.2, 0.5, 1),
                    halign='center',
                    size_hint_x=COL_SUM
                ))
                
                btn_box = BoxLayout(spacing=dp(8), size_hint_x=COL_ACTIONS)
                
                edit_btn = Button(
                    text='ИЗМЕНИТЬ',
                    font_size=dp(11),
                    background_color=(0.75, 0.85, 0.95, 1),
                    background_normal='',
                    background_down='',
                    color=(0.1, 0.1, 0.1, 1)
                )
                edit_btn.bind(on_release=lambda x, i=item: self._edit_item(i))
                
                del_btn = Button(
                    text='УДАЛИТЬ',
                    font_size=dp(11),
                    background_color=(0.95, 0.80, 0.80, 1),
                    background_normal='',
                    background_down='',
                    color=(0.5, 0.1, 0.1, 1)
                )
                del_btn.bind(on_release=lambda x, i=item: self._delete_item(i))
                
                btn_box.add_widget(edit_btn)
                btn_box.add_widget(del_btn)
                row.add_widget(btn_box)
                
                self.table_body.add_widget(row)

        self.total_label.text = f'ОБЩАЯ СТОИМОСТЬ СКЛАДА: {grand_total:,.2f} РУБ.'.replace(',', ' ')

    def _clear_inputs(self):
        self.name_input.text = ''
        self.qty_input.text = ''
        self.price_input.text = ''
        self.name_input.focus = True

    def _show_error(self, msg):
        Popup(
            title='Внимание',
            content=Label(text=msg, color=(0.8, 0.1, 0.1, 1), font_size=dp(16)),
            size_hint=(0.6, 0.3),
            auto_dismiss=True
        ).open()


class StockKeeperApp(App):
    def build(self):
        self.title = 'StockKeeper'
        return MainScreen()

if __name__ == '__main__':
    StockKeeperApp().run()