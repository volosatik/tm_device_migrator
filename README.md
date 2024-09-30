# Tm Device Migrator

Назначение: удаленное переключение УСПД ТМ-3 (подробнее тут - https://megawiki.megafon.ru/x/o7olN)

Рекомендуется перед запуском скрипта проверить права на исполнение скрипта, создание папок и файлов либо выполнить из под root УЗ.
Запустить скрипт
- ./script.sh &> log.txt &  - запуск скрипта и запись лога в файл;
- tail -f log.txt - просмотр лог файла.

Результатом выполнения скрипта будет папка с текущей датой, в которой:
- файл log.txt - лог переключения,
- файлы ip.txt с конфигурациями УСПД до момента переключения (в них находится uspd_id)
- conn_timeout_ip_list.txt - список ip, по которым не удалось подключиться.

# По питону:
- входные данные csv с 3 полями (адрес, ID, тип) (+)
- входные данные Конфига содержащая интерфейс с которого до девайсов будут стучаться переключатели и порт  (+)
- формирование файла который потом заливается в sh скрипт на конечный девайс (+) 
- выходные - результат работы каждого воркера по переключению (сохраняется конфига каждого девайса после переключения) (+)
- общий лог где будет success и failure (+) 
