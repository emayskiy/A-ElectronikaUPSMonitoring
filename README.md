# Мониторинг UPS А-Электроника Страж-3000 через Bluetooth-модуль

## Настройка UPS

Для настройки инвертера запускаем скрипт 

        ./configureups.py.

Он отобразит текущее состояние и значение параметров UPS.
Для изменения значения параметра вводим имя параметра и значение.
После изменения параметров нужно запустить снова и проверить корректность установки параметров.
Параметры заряда рекомендуется устанавливать в зависимости от подключенного АКБ.
Можно посмотреть в документации на АКБ на сайте производителя

Ток заряда рекомендуется устанавливать как 1/10 емкости АКБ. Например для АКБ емкость 100А/ч необходимо поставить 10А

## Контроль UPS

В крон добавляем расписание для запуска скрипта 

crontab -e


	./main.py 

Данный скрипт контролирует параметры ИБП, выполняет оповещение по email и СМС, а так же отключает сервер при низком заряде АКБ.
Все настройки хранятся в файле ups.conf
При работе пишутся логи в файл ups_log.txt c текущем состоянием


## Протокол обмена данными с ИБП СТРАЖ-3000

```
?vbat напряжение аккумулятора
?cur сила тока аккумулятора
?vin напряжение сети
?tpri температура первичной части
?tsec температура вторичной части
?curin сила тока на сетевом входе
?pwr полная мощность нагрузки
?apwr активная мощность нагрузки
?pf коэффициент мощности нагрузки
?allmode режим работы инвертора
?frq частота сети
```

Команды запроса и изменения настроек инвертора
запрос изменение Элемент меню программирования
```
?vlo_off vlo_off= напряжение отключения
?vlo_start vlo_start= напряжение переподключения
?vlo_warn vlo_warn= напряжение предупреждения
?slp slp= разрешение спящего режима
?offline offline= разрешение переключения на сеть
?vout vout= выходное напряжение
?vch vch= напряжение заряда
?ich ich= ток заряда
?vfl vfl= напряжение поддерживающей стадии заряда
?ifl ifl= ток переключения на поддерживающую стадию заряда
?pwr_slp pwr_slp= мощность нагрузки для выхода из спящего режима
?snd snd= разрешение звуковой индикации
?podk podk= разрешение гибридного режима
?vline_lo vline_lo= минимальное напряжение сети
?vline_hi vline_hi= максимальное напряжение сети
?frq_lo frq_lo= минимальная частота сети
?frq_hi frq_hi= максимальная частота сети 
?fast fast = контроль формы сетевого напряжения
?sell sell= разрешение продажи энергии в сеть
?eco eco= разрешение приоритетного использования аккумулятора
?veco_lo veco_lo= напряжение заряда АКБ, при котором происходит отключение от сети и переход на работу от аккумулятора
?veco_hi veco_hi= напряжение разряда АКБ, при котором происходит переключение на сеть 
```

Команды управления включением инвертора
```
INV_ON -включает инвертор,
INV_OFF -выключает инвертор
```

Ответы инвертора
```
ОК - инвертор распознал команду
error -инвертор не распознал команду
equ - устанавливаемое значение совпадает с записанным в настройках инвертора
```