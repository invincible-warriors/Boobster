from types import SimpleNamespace

from telegram import ReplyKeyboardMarkup

Markups = SimpleNamespace()
Markups.keyboards = SimpleNamespace()

Markups.keyboards.default_reply = [
    ["/nudes", "/aesthetics"],
    ["/nude_photo", "/aesthetic_photo"],
]
Markups.keyboards.admin_default_reply = [
    *Markups.keyboards.default_reply,
    ["/client_stats", "/sorter_stats"],
    ["/clients_stats", "/sorters_stats"],
    ["/photo_stats"],
    ["/start_sorting"]
]
Markups.keyboards.sorting = [
    ["delete", "aesthetics", "nudes", "full_nudes"],
    ["/exit"]
]

Markups.default = ReplyKeyboardMarkup(Markups.keyboards.default_reply, resize_keyboard=True)
Markups.admin_default = ReplyKeyboardMarkup(Markups.keyboards.admin_default_reply, resize_keyboard=True)
Markups.sorting = ReplyKeyboardMarkup(Markups.keyboards.sorting, resize_keyboard=True)
