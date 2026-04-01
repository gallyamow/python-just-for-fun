"""
LSTM - Long Short-Term Memory

Это такая версия RNN, которая умеет:
- решать, что запомнить, а что забыть
- делает это через специальный механизм gates

Как будто у сети есть:
- блокнот (долгая память)
- краткая мысль (текущее состояние)
- фильтры (что пускать дальше)

Внутри, на каждом шаге:
1) Forget Gate - решается что забыть.
2) Input Gate - решает что записать
3) Output Gate - что использовать

Упрощенно:
вход (буква)
   ↓
[ забыть ] → [ добавить ] → [ показать ]
   ↓
обновлённая память

Почему лучше, чем RNN:
Проблема RNN: градиенты “затухают” → модель забывает начало
LSTM - решает это через: cell state (долгую память). Она: проходит через всю последовательность почти без изменений
изменяется только через гейты
"""
import torch
import torch.nn as nn  # модуль нейросетей
import torch.nn.functional as F  # функции нейросетей

EPOCH = 200
START = '<'
END = '>'

"""
1) Данные
"""
docs = [line.lower().strip() for line in open('input.txt') if line.strip()]
# random.shuffle(names)
print(f"docs: {len(docs)}")

"""
2) Словарь
stoi = Символ => Индекс символа
itos = Индекс символа => Символ
"""
chars = sorted(list(set("".join(docs))) + [START, END])
stoi = {ch: i for i, ch in enumerate(chars)}
itos = {i: ch for ch, i in stoi.items()}

vocab_size = len(chars)
print(f"vocab_size: {vocab_size}")

"""
3) Подготовка обучающих примеров.
(Обычно добавляют еще padding + batching)
"""
bos_names = [START + name + END for name in docs]


def build_dataset(names: list):
    X, Y = [], []

    for name in names:
        for i in range(len(name) - 1):
            """
            language modeling:
            X - Что видим (начало строки). Например, для <anna>, <a. В конце "<anna"
            Y - Что хотим (след. символы). Например, для <anna>, an. То есть после "a" идет "n". В конце "anna>".
            
            X = [
              [<],
              [<,a],
              [<,a,n],
              ...
            ]
            
            Y = [
              [a],
              [a,n],
              [a,n,n],
              ...
            ]
            """
            x_seq = name[:i + 1]
            y_seq = name[1:i + 2]
            # print(x_seq, y_seq)

            X.append([stoi[c] for c in x_seq])
            Y.append([stoi[c] for c in y_seq])
    return X, Y


X, Y = build_dataset(bos_names)
# print(X, Y)

"""
4) МОДЕЛЬ (одна — меняем только GRU/LSTM)
"""

class NameModel(nn.Module):
    """
    nn.Module — базового класса всех моделей в PyTorch
    Параметры:
    - vocab_size — сколько у тебя символов (например: a,b,n,<,>)
    - hidden_size — размер “памяти” модели
    - use_lstm — переключатель LSTM / GRU
    """
    def __init__(self, vocab_size, hidden_size=64, use_lstm=True):
        super().__init__()

        # Инициализация embedding-слоя - который превращает символы в вектор
        self.embed = nn.Embedding(vocab_size, 32)

        # RNN или LSTM слой - который читает последовательность и запоминает контекст
        # 32 → размер embedding
        # hidden_size → размер памяти
        if use_lstm:
            self.rnn = nn.LSTM(32, hidden_size, batch_first=True)
        else:
            self.rnn = nn.GRU(32, hidden_size, batch_first=True)

        # Линейный слой - принимает вектор размера a и превращает его в размер b
        # Тут у нас есть некий «смысловой вектор» размера hidden_size, его надо преобразовать в [оценки для каждого слова]
        self.fc = nn.Linear(hidden_size, vocab_size)

    def forward(self, x):
        """
        Главный проход данных через модель.
        1) Embedding - преобразует в векторы
        2) Прогоняет данные через рекуррентную сеть (RNN / LSTM / GRU)
        out - выход на каждом шаге, _ - скрытое состояние которое игнорим
        3) fc = fully connected слой (линейный) - Преобразует выход RNN в нужный формат (например, классы)
        Обычно это шаг, где получаются логиты для классификации или предсказаний.
        """
        x = self.embed(x)
        out, _ = self.rnn(x)
        out = self.fc(out)
        return out


"""
5) Обучение
"""
model = NameModel(vocab_size, use_lstm=True)  # LSTM
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
criterion = nn.CrossEntropyLoss()

for epoch in range(EPOCH):
    total_loss = 0

    for x, y in zip(X, Y):
        x = torch.tensor([x])
        y = torch.tensor([y])

        logits = model(x)

        loss = criterion(
            logits.view(-1, vocab_size),
            y.view(-1)
        )

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    if epoch % 20 == 0:
        print(f"epoch {epoch}, loss {total_loss:.2f}")

"""
6) Генерация имен
"""


def generate(model, max_len=10):
    model.eval()

    x = torch.tensor([[stoi[START]]])
    result = []

    for _ in range(max_len):
        logits = model(x)
        probs = F.softmax(logits[0, -1], dim=0)

        idx = torch.multinomial(probs, 1).item()
        char = itos[idx]

        if char == END:
            break

        result.append(char)
        x = torch.cat([x, torch.tensor([[idx]])], dim=1)

    return "".join(result)


for _ in range(10):
    print(generate(model))

"""
7) Сохраняем модель и словарь
"""
torch.save({
    "model": model.state_dict(),
    "stoi": stoi,
    "itos": itos
}, "model_full.pth")
