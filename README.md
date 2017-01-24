# tamagopnik

Игра, сценарий которой творит общество!
Пожалуйста, ознакомьтесь с содержимым файла about.md.

Здесь описывается формирование сценария для игры в вид, который будет понятен движку. Используемый язык - python (в нем нет точек с запятой для разделения текста, текст разделяется табуляцией)

## Типичный вид румы :

````python
class FirstRoom(room):
    quest = ["Привет, хехе",
             "Make a wish and become a mohou shoujo",
             ["choose", {"Okay, Kubei, make me a mahou shoujo": "quest1",
                         "No, Inkubeta!":"quest1"}]
             ]
    quest1 = ["Вы почуствовали невероятный прилив сил",
              ['end', 'Вжух! Вы умерли, для старта сначала нажмите /start']
              ]
````
    
Класс представляет собой саму комнату. Квесты, переменные комнаты, являются листами, которые хранят в себе либо обычную строку, либо еще один некий лист.
Обычный текст выводится игроку. Листы внутри квестов являются функциями квестов (в примере можно увидеть `choose` и `end`).

## Всего на данный момент существуют данные типы функций квестов:

1. ['end', 'text'] - Окончание игры. Выводит text, стирает данные об игроке из базы. Будьте осторожны с его использованием. Я не думаю, что большинство игроков будут играть на хардкоре, всё-таки потерять все данные в середине игры - удовольствие не из приятных
2. ['goto', 'X', 'Y']- перемещает в комнату X, диалог-массив Y
3. ['сhoose', {"text1": "quest1",..., "textN":"questN"}] - предлагает игроку выбрать один из предложенных ответов. В зависимости от ответа, его переносит в определенный квест, принадлежащий текущей комнате.
4. ['take', 'X' (,'Y')]- вещь X поднимается и заносится в инвентарь игрока. Игрок не имеет возможности смотреть содержимое инвентаря, так что можно хранить в нем флаги выполнения определенных условий (например, поговорить с Паханом можно только при условии, что ты получишь "Согласие от Саши" и "Красная кепка"). Текст Y произносится, если он определен.
5. ['drop', 'X' (,'Y')] - вещь изымается из инвентаря. Если ее нет в инвентаре, игроку показывается оповещение, которое он должен показать автору, это оповещение не дает данному игроку продолжить игру.
6. ['item_exist', 'item_name', 'quest1', 'quest2'] - если вещь есть в инвентаре, то переход на квест1, иначе - квест2
7. ['random', 'A', 'B', 'C', ..., 'Z'] - случайно выбирает один из перечисленых вариантов диалог-массивов и переходит к нему.
8. ['compile', 'some text, {one}, {two}, sometext', 'params'] - печатает форматированный текст.

                          На самом деле, оно делает вот что : ans = eval('"'+text+'".format('+params+')')
                          То есть используется функция format для строк, чтобы форматировать текст.
                          
                          Что можно с этим делать :
                          - с помощью random  шаманить с текстами. Пример :
                              ['compile', "В лесу родилась {name}, {nya}", 'name=["Ёлочка", "Собачка"].random.randrange(2)', nya = "meow"' ]
                          - показывать какую-нибудь техническую информацию, связанную с телеграммом. Например, id текущего игрока (bot.chat.id)
                          - соединять слова. Например, name="Елочка"+str(str(random.randrange(3000,4000)))
                          
                          
## Так выглядит две связаные комнаты, представляющие собой законченный и неизбежный квест :
````python
class teststartroom(room):
    quest = ["Привет, хехе",
             "Make a wish and become a mohou shoujo",
             ["choose", {"Okay, Kubei, make me a mahou shoujo": "quest1",
                         "No, Inkubeta!":"quest1"}]
             ]
    quest1 = ["Вы почуствовали невероятный прилив сил",
              ["goto", "endo", "quest"]]
    quest2 = [[""]]

class endo(room):
    quest = ["Силы до сих пор наполняют тебя",
             ["take", "серебряная ложка", "Вы подняли серебряную ложку"],
             ["compile", "Это оказалась серебряная ложка {}", "'изменника'"],
             ["random", "quest1", "quest2"]]
    quest1 = ["magic fairy",
              ['end', "Удача убила тебя!"]]
    quest2 = ["maggle, no magic for you!",
              ["end", "Умер как обычный человек!"]]
````

## Комментирование:
````python
class teststartroom(room):
    quest = ["Привет, хехе", #комментарий 1
             "Make a wish and become a mohou shoujo",
             '''
             Мне кажется, или этот бело-фиолетовый кот что-то замышляет
             Но я всего лишь комментарий, поэтому ничего не могу поделать
             '''
             ["choose", {"Okay, Kubei, make me a mahou shoujo": "quest1",
                         "No, Inkubeta!":"quest1"}]
             ]
    quest1 = ["Вы почуствовали невероятный прилив сил",
              ["goto", "endo", "quest"]]
    quest2 = [[""]]
````

## Каким образом можно внести изменение в проект?
Пользуйтесь всем, что вам доступно!
Создавайте issue, делайте ветки, пилите pool request'ы, пишите на почту, вызывайте на пикабу. Я еще не полностью разобрался с гитхабом, но вижу, тут есть элементы "народного голосования", что, несомненно, можно использовать. Нет проблем, если вы не можете/не хотите оформлять румы и квесты по по канону.

## Немного о тексте.
1. Не допускаются мат, чернуха. Да, жизнь нелегка, но использование мата может повлечь определенные проблемы.
2. Не стоит религиозные издевательские темы поднимать. У меня (в России) законы о защите чувств верующих суровы, любой чих в сторону тех, кого опекает сам Бог, будет караться судом, штрафами и тюрьмой.
3. Можно использовать актуальные события (пример : террор МГУ и палисадников на внедорожниках в конце 2016 - начале 2017), но с расчетом на то, что через пару лет информация может потерять значимость.

## Где ты держишь игру, старче?
 Игра хостится на моем компьютере, поэтому могут быть проблемы

## Общий сюжет
#### Не читайте, если еще не играли в текущую версию игры, тут спойлеры, полагаю
Общий сюжет необходим, чтобы был хоть какой-нибудь план для работы. В него можно предлагать правки, он служит лишь ориентиром для дальнейшей работы. Тут только план, если есть в тебе писательская жилка - смело стучись в "сценарий.txt".
#### Глава 1
1. Рума 1. Разговор с богиней гопников.
2. Рума 2. Задний двор, Черноголовка. Серебряный петух.
3. Рума 3.0. Игрок ловит попутку в Москву. Ему случайным образом предлагается три варианта (есть возможность отказаться):
   Рума 3.1. Игрок поймал затонированный гелик. Там сидят немногословные люди в костюмах и солнцезащитных очках. Dead end - продажа на органы. Богиня возвращает в руму 3.0 с цитаткой.
   Рума 3.2. Игрок поймал десятку, в которой сидят 3 гопника. Тут необходим разговорный баттл между гопниками, по итогам которого его либо выкидывают из машины (опять ловить машину), либо спокойно довозят до Москвы.
   Рума 3.3. Игрок ловит Москвич со стариком. Машина хоть и старая, но аккуратная. Тут будет монолог старика о том, как в СССР жилось хорошо. 100% успешный шанс добраться до Москвы.
   
#### Глава 2
1. Игрок находится в Москве. Богиня советует пойти в местное представительство Гопников России. Там он получает квест - разобраться с ???, после чего они народом скидываются на билет на поезд, едущему по Транссибу.

#### Глава 3
1. Его высаживают за то, что поругался с кондуктором. Станция маленького городка. Всюду снег, снег, снег.


#### Глава N
1. Он должен добраться до этого За***ска
