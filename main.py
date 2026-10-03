import sqlite3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.recycleview import RecycleView
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.core.text import LabelBase

# استيراد مكتبة تشكيل الحروف العربية
import arabic_reshaper

# تسجيل خط ويندوز العربي (Tahoma)
try:
    LabelBase.register(name='ArabicFont', fn_regular='C:\\Windows\\Fonts\\tahoma.ttf')
except:
    try:
        LabelBase.register(name='ArabicFont', fn_regular='C:\\Windows\\Fonts\\arial.ttf')
    except:
        pass

# دالة مخصصة لضبط النصوص العربية لتظهر بشكل سليم 100% مع محرك Kivy الـ LTR
def fix_arabic(text):
    if not text:
        return ""
    try:
        # تشكيل الحروف لتقوم بالاتصال الصحيح ثم عكسها لتناسب عرض Kivy
        reshaped_text = arabic_reshaper.reshape(str(text))
        return reshaped_text[::-1]
    except:
        return text

# تهيئة قاعدة البيانات SQLite
def init_db():
    conn = sqlite3.connect("store.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

KV = '''
<Label>:
    font_name: 'ArabicFont'
<Button>:
    font_name: 'ArabicFont'
<TextInput>:
    font_name: 'ArabicFont'
    halign: 'right'

BoxLayout:
    orientation: 'vertical'
    padding: dp(15)
    spacing: dp(10)

    Label:
        text: app.title_text
        font_size: '22sp'
        bold: True
        size_hint_y: None
        height: dp(40)
        color: 0.1, 0.4, 0.8, 1

    TextInput:
        id: name_input
        hint_text: app.hint_name
        multiline: False
        size_hint_y: None
        height: dp(45)

    TextInput:
        id: price_input
        hint_text: app.hint_price
        input_filter: 'float'
        multiline: False
        size_hint_y: None
        height: dp(45)

    TextInput:
        id: stock_input
        hint_text: app.hint_stock
        input_filter: 'int'
        multiline: False
        size_hint_y: None
        height: dp(45)

    BoxLayout:
        size_hint_y: None
        height: dp(45)
        spacing: dp(10)
        Button:
            text: app.btn_add
            background_color: 0.1, 0.7, 0.3, 1
            on_press: app.add_product()
        Button:
            text: app.btn_update
            background_color: 0.1, 0.4, 0.8, 1
            on_press: app.update_product()

    BoxLayout:
        size_hint_y: None
        height: dp(45)
        spacing: dp(10)
        Button:
            text: app.btn_delete
            background_color: 0.8, 0.2, 0.2, 1
            on_press: app.delete_product()
        Button:
            text: app.btn_clear
            background_color: 0.5, 0.5, 0.5, 1
            on_press: app.clear_form()

    Label:
        id: status_label
        text: ""
        font_size: '14sp'
        bold: True
        size_hint_y: None
        height: dp(30)

    TextInput:
        id: search_input
        hint_text: app.hint_search
        multiline: False
        size_hint_y: None
        height: dp(40)
        on_text: app.load_data(self.text)

    RecycleView:
        id: rv
        viewclass: 'SelectableButton'
        RecycleBoxLayout:
            default_size: None, dp(50)
            default_size_hint: 1, None
            size_hint_y: None
            height: self.minimum_height
            orientation: 'vertical'
'''

class SelectableButton(Button):
    pass

class YasserStoreApp(App):
    selected_id = None
    title_text = fix_arabic("نظام ياسر لإدارة المخازن والمبيعات")
    
    # النصوص الثابتة والأزرار معالجة بالكامل
    btn_add = fix_arabic("إضافة جديد")
    btn_update = fix_arabic("تعديل المحدد")
    btn_delete = fix_arabic("حذف المحدد")
    btn_clear = fix_arabic("إفراغ الحقول")
    
    hint_name = fix_arabic("اسم المنتج")
    hint_price = fix_arabic("السعر ($)")
    hint_stock = fix_arabic("الكمية في المخزن")
    hint_search = fix_arabic("بحث عن منتج...")

    def build(self):
        self.title = "Yasser Store"
        return Builder.load_string(KV)

    def on_start(self):
        self.load_data()

    def load_data(self, search_query=""):
        conn = sqlite3.connect("store.db")
        cursor = conn.cursor()
        if search_query:
            cursor.execute("SELECT id, name, price, stock FROM products WHERE name LIKE ?", ('%' + search_query + '%',))
        else:
            cursor.execute("SELECT id, name, price, stock FROM products")
        rows = cursor.fetchall()
        conn.close()

        data = []
        for r in rows:
            prod_id, name, price, stock = r
            raw_text = f"ID: {prod_id} | الاسم: {name} | السعر: {price}$ | الكمية: {stock}"
            fixed_text = fix_arabic(raw_text)
            data.append({'text': fixed_text, 'on_press': lambda pid=prod_id, n=name, p=price, s=stock: self.select_product(pid, n, p, s)})
        
        self.root.ids.rv.data = data

    def select_product(self, pid, name, price, stock):
        self.selected_id = pid
        self.root.ids.name_input.text = name
        self.root.ids.price_input.text = str(price)
        self.root.ids.stock_input.text = str(stock)
        self.root.ids.status_label.text = fix_arabic(f"جاهز للتعديل: {name}")

    def clear_form(self):
        self.selected_id = None
        self.root.ids.name_input.text = ""
        self.root.ids.price_input.text = ""
        self.root.ids.stock_input.text = ""
        self.root.ids.status_label.text = ""
        self.load_data()

    def add_product(self):
        name = self.root.ids.name_input.text
        price = self.root.ids.price_input.text
        stock = self.root.ids.stock_input.text

        if not name or not price or not stock:
            self.root.ids.status_label.text = fix_arabic("الرجاء تعبئة كافة الحقول!")
            return

        conn = sqlite3.connect("store.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", (name, float(price), int(stock)))
        conn.commit()
        conn.close()

        self.root.ids.status_label.text = fix_arabic("تمت إضافة المنتج بنجاح!")
        self.clear_form()

    def update_product(self):
        if not self.selected_id:
            self.root.ids.status_label.text = fix_arabic("الرجاء اختيار منتج للتعديل أولاً!")
            return

        name = self.root.ids.name_input.text
        price = self.root.ids.price_input.text
        stock = self.root.ids.stock_input.text

        conn = sqlite3.connect("store.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE products SET name = ?, price = ?, stock = ? WHERE id = ?", (name, float(price), int(stock), self.selected_id))
        conn.commit()
        conn.close()

        self.root.ids.status_label.text = fix_arabic("تم تعديل المنتج بنجاح!")
        self.clear_form()

    def delete_product(self):
        if not self.selected_id:
            self.root.ids.status_label.text = fix_arabic("الرجاء اختيار منتج للحذف أولاً!")
            return

        conn = sqlite3.connect("store.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = ?", (self.selected_id,))
        conn.commit()
        conn.close()

        self.root.ids.status_label.text = fix_arabic("تم حذف المنتج بنجاح!")
        self.clear_form()

if __name__ == '__main__':
    YasserStoreApp().run()