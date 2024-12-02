from telebot import types
token = None
admin = None
heroes_list_link = "https://telegra.ph/Spisok-geroev-02-17"

b_1_text = "Список героев"
b_1_inline = types.InlineKeyboardMarkup()
b_1 = types.InlineKeyboardButton(text=b_1_text, url=heroes_list_link)
b_1_inline.add(b_1)

b_2 = "Профиль 👤"
b_3 = "Мета 🔝"
b_4 = "Список героев📋"
b_5 = "Помощь 🔎"

def userpanel():
    menu_inline = types.ReplyKeyboardMarkup(True)
    key1 = types.KeyboardButton(b_2)
    key2 = types.KeyboardButton(b_3)
    key3 = types.KeyboardButton(b_4)
    key4 = types.KeyboardButton(b_5)
    menu_inline.add(key1, key2)
    menu_inline.add(key3, key4)
    return menu_inline
