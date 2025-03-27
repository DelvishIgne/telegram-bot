import sys
import requests
from bs4 import BeautifulSoup
from PySide2.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QTextEdit, QPushButton,
    QLabel, QFileDialog, QHBoxLayout
)
from PySide2.QtGui import QTextCharFormat, QColor


class HtmlParser(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('HTML Parser')
        self.setGeometry(100, 100, 900, 700)

        layout = QVBoxLayout()

        self.url_label = QLabel('URL статьи:')
        self.url_input = QLineEdit()
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_input)

        self.selector_label = QLabel('CSS-селектор:')
        self.selector_input = QLineEdit()
        layout.addWidget(self.selector_label)
        layout.addWidget(self.selector_input)

        parse_button = QPushButton('Спарсить')
        parse_button.clicked.connect(self.parse_html)
        layout.addWidget(parse_button)

        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)
        self.text_edit.textChanged.connect(self.highlight_text)

        button_layout = QHBoxLayout()

        part_button = QPushButton('[PART]')
        part_button.clicked.connect(lambda: self.insert_marker('[PART]'))
        button_layout.addWidget(part_button)

        image_button = QPushButton('[IMAGE]')
        image_button.clicked.connect(lambda: self.insert_marker('[IMAGE]'))
        button_layout.addWidget(image_button)

        bold_button = QPushButton('Жирный')
        bold_button.clicked.connect(lambda: self.wrap_selected_text('b'))
        button_layout.addWidget(bold_button)

        italic_button = QPushButton('Курсив')
        italic_button.clicked.connect(lambda: self.wrap_selected_text('i'))
        button_layout.addWidget(italic_button)

        underline_button = QPushButton('Подчеркнутый')
        underline_button.clicked.connect(lambda: self.wrap_selected_text('u'))
        button_layout.addWidget(underline_button)

        strike_button = QPushButton('Зачеркнутый')
        strike_button.clicked.connect(lambda: self.wrap_selected_text('s'))
        button_layout.addWidget(strike_button)

        link_button = QPushButton('Ссылка')
        link_button.clicked.connect(self.insert_link)
        button_layout.addWidget(link_button)

        layout.addLayout(button_layout)

        self.char_count_label = QLabel('Символов выделено: 0')
        layout.addWidget(self.char_count_label)

        self.text_edit.selectionChanged.connect(self.update_char_count)

        save_button = QPushButton('Сохранить как TXT')
        save_button.clicked.connect(self.save_as_txt)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def parse_html(self):
        url = self.url_input.text()
        selector = self.selector_input.text()
        allowed_tags = ['b', 'strong', 'i', 'em', 'u', 'ins', 's', 'strike', 'del', 'a']

        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            element = soup.select_one(selector)
            if element:
                for tag in element.find_all(True):
                    if tag.name not in allowed_tags:
                        tag.unwrap()
                html_content = ''.join(str(e) for e in element.contents)
                self.text_edit.setPlainText(html_content)
            else:
                self.text_edit.setPlainText('Элемент с указанным селектором не найден.')

        except requests.exceptions.RequestException as e:
            self.text_edit.setPlainText(f'Ошибка: {e}')

    def insert_marker(self, marker):
        cursor = self.text_edit.textCursor()
        cursor.insertText(marker)

    def wrap_selected_text(self, tag):
        cursor = self.text_edit.textCursor()
        selected_text = cursor.selectedText()
        if selected_text:
            cursor.insertText(f'<{tag}>{selected_text}</{tag}>')

    def insert_link(self):
        cursor = self.text_edit.textCursor()
        url = self.url_input.text()
        cursor.insertText(f'<a href="{url}">ПРОЧЕСТЬ НА САЙТЕ</a>')

    def update_char_count(self):
        cursor = self.text_edit.textCursor()
        count = len(cursor.selectedText())
        self.char_count_label.setText(f'Символов выделено: {count}')

    def highlight_text(self):
        text = self.text_edit.toPlainText()
        parts = text.split('[PART]')

        self.text_edit.blockSignals(True)

        cursor = self.text_edit.textCursor()
        cursor.select(cursor.Document)
        cursor.setCharFormat(QTextCharFormat())

        position = 0
        for part in parts:
            fmt = QTextCharFormat()
            if len(part) <= 4000:
                fmt.setBackground(QColor('#ccffcc'))  # Зеленый
            else:
                fmt.setBackground(QColor('#ffcccc'))  # Розовый

            cursor.setPosition(position)
            cursor.movePosition(cursor.Right, cursor.KeepAnchor, len(part))
            cursor.setCharFormat(fmt)
            position += len(part) + len('[PART]')

        self.text_edit.blockSignals(False)

    def save_as_txt(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить файл", "", "Текстовый файл (*.txt);;Все файлы (*)", options=options)
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(self.text_edit.toPlainText())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    parser_app = HtmlParser()
    parser_app.show()
    sys.exit(app.exec_())
