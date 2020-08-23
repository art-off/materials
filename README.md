# Вот эта статья если с email снова что-то не так: #
https://www.twilio.com/blog/2018/03/send-email-programmatically-with-gmail-python-and-flask.html

## Шо пофиксить: ##

- Добавить вкладку контроля за просмотром       DONE
- Сделать так, чтобы входить мог только admin   DONE
- Сделать название разделов в нижнем регистре   DONE
- Сделать странички ошибок                      DONE
- Исправить парсинг ключевых слов               DONE
- Корректировать разрешеные типо файлов         -
- Сделать нормальный адресс сайта в письме


## БЕЗ ИЗМЕНЕНИЯ: ##

- Дата останется в формате (ГГГГ-ММ-ДД)



## Шо разработать: ##

- РАССЫЛКА НА ПОЧТУ                                                         DONE
- Возвращение по GET всего списка материалов в JSON  (/api/materials)
[
    {
        "id": <int>,
        "name": <str>,
        "section": <std>,
        "date": <ГГГГ-ММ-ДД>,
        "keywords": [
            "keywords1",
            "keywords2"
        ],
        "files": [
            "file1.png",
            "file2.mp3",
        ]
    },
    {
        "id": <int>,
        "name": <str>,
        "section": <std>,
        "date": <ГГГГ-ММ-ДД>,
        "keywords": [
            "keywords1",
            "keywords2"
        ],
        "files": [
            "file1.png",
            "file2.mp3",
        ]
    }
]
- Возвращение по GET материала по id (api/materials/<id>)
- POST с email и паролем, и если такой пользователь есть, то возвратить этого пользователя в JSON (api/login)
- POST с пройденными материалами (api/add_material)
