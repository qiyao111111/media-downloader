"""Logical-pixel metrics and semantic palettes for the desktop UI."""
SPACING = (4, 8, 12, 16, 20, 24, 32)
RADIUS = (6, 8, 12)
CONTROL = {'small': 32, 'normal': 40, 'large': 44}
SIDEBAR = 200
PAGE_X, PAGE_Y, CARD, GAP, SECTION = 24, 20, 16, 16, 24
TYPE = {'page': 24, 'section': 17, 'card': 15, 'body': 13, 'secondary': 12, 'caption': 11}
PALETTES = {
    'light': dict(background='#f5f5f5', surface='#ffffff', hover='#f0f2f4', selected='#e8f0fa', text='#20242a', secondary='#56616e', disabled='#727b87', border='#d9dde3', divider='#e6e8ec', accent='#2468bc', accent_hover='#1d5ba8', accent_pressed='#174a8c', success='#237348', warning='#876000', danger='#b32632', info='#2468bc', on_accent='#ffffff'),
    'dark': dict(background='#202124', surface='#292b30', hover='#34373d', selected='#283f5a', text='#f1f3f5', secondary='#b8c0cc', disabled='#939caa', border='#494e58', divider='#3c4149', accent='#86b8f4', accent_hover='#9ac6fa', accent_pressed='#6aa5ed', success='#83d6a4', warning='#efc66c', danger='#ff9ca5', info='#86b8f4', on_accent='#17283e'),
}
