"""
The most atomic way to train and run inference for a GPT in pure, dependency-free Python.
This file is the complete algorithm.
Everything else is just efficiency.

@karpathy
"""
import os  # os.path.exists
import math  # math.log, math.exp
import random  # random.seed, random.choices, random.gauss, random.shuffle

random.seed(42)  # Let there be order among chaos

# Let there be a Dataset `docs`: list[str] of documents (e.g. a list of names)
if not os.path.exists('input.txt'):
    import urllib.request

    names_url = 'https://raw.githubusercontent.com/karpathy/makemore/988aa59/names.txt'
    urllib.request.urlretrieve(names_url, 'input.txt')

"""
Все имена из файла
"""
docs = [line.strip() for line in open('input.txt') if line.strip()]
random.shuffle(docs)
print(f"num docs: {len(docs)}")

# Let there be a Tokenizer to translate strings to sequences of integers ("tokens") and back
"""
Все уникальные буквы из имен, каждой присвоен какой то номер.
"""
uchars = sorted(set(''.join(docs)))  # unique characters in the dataset become token ids 0..n-1
BOS = len(uchars)  # token id for a special Beginning of Sequence (BOS) token
vocab_size = len(uchars) + 1  # total number of unique tokens, +1 is for BOS
print(f"vocab size: {vocab_size}")

# Let there be Autograd to recursively apply the chain rule through a computation graph
"""
Autograd — это система, которая автоматически считает производные (градиенты).
Это позволяет определить на сколько сильно изменение входа влияет на результат.
Т.е. считать градиенты, чтобы обновить веса.

Производная работает только локально, и дает ожидаемый dy изменение только для маленьких dx.

Как он работает:
1) Запоминает все операции (строит граф вычислений)
2) Идёт назад по этому графу
3) Применяет правило цепочки
4) Вычисляет градиенты для каждой переменной


Правило цепочки — это способ находить производную сложной функции, которая состоит из нескольких вложенных частей.
Если что-то зависит от промежуточной переменной, а та — ещё от чего-то, ты умножаешь производные по цепочке:
Дано:
- x влияет на y
- y влияет на z
Нужно:
как x влияет на z = (как y влияет на z) * (как x влияет на y)
dz/dx = dz/dy * dy/dx

Пример:
y = x^2
z = y^3
dz/dx = 3y^2 * 2x
"""


class Value:
    __slots__ = ('data', 'grad', '_children', '_local_grads')  # Python optimization for memory usage

    def __init__(self, data, children=(), local_grads=()):
        self.data = data  # scalar value of this node calculated during forward pass
        """
        Производная функции потерь по данному узлу, вычисленная на обратном проходе.
        Показывает насколько изменится ошибка (loss), если чуть изменить значение этого узла.
        """
        self.grad = 0  # derivative of the loss w.r.t. this node, calculated in backward pass
        self._children = children  # children of this node in the computation graph
        """
        Производная функции потерь по данному узлу, вычисленная относительно детей.
        
        Пример:
        Пусть есть ф-я z=(x * y) + b
        Узел 1: q = x * y
        Узел 2: z = q + b
        
        Шаг 1: локальные производные
        Узел 2: z = q + b
        dz/dq = 1
        dz/db = 1
        Узел 1: q = x * y
        dq/dx = y
        dq/dy = x
        
        Шаг 2: backpropagation (обратный проход)
        local derivative = “как этот узел реагирует на свои входы”
        backprop = “как ошибка проходит назад через граф”
        по x: dz/dx = dz/dq * dq/dx = 1 * y = y
        по y: dz/dy = dz/db * dq/dy = 1 * x = x
        по z: dz/db = 1 
        """
        self._local_grads = local_grads  # local derivative of this node w.r.t. its children

    def __add__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        return Value(self.data + other.data, (self, other), (1, 1))

    def __mul__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        return Value(self.data * other.data, (self, other), (other.data, self.data))

    def __pow__(self, other):
        return Value(self.data ** other, (self,), (other * self.data ** (other - 1),))

    def log(self):
        return Value(math.log(self.data), (self,), (1 / self.data,))

    def exp(self):
        return Value(math.exp(self.data), (self,), (math.exp(self.data),))

    def relu(self):
        return Value(max(0, self.data), (self,), (float(self.data > 0),))

    def __neg__(self):
        return self * -1

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        return self + (-other)

    def __rsub__(self, other):
        return other + (-self)

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        return self * other ** -1

    def __rtruediv__(self, other):
        return other * self ** -1

    def backward(self):
        """
        Классическая реализация backpropagation (обратного прохода)

        Обход графа в глубину с контролем посещенных узлов.
        topo - будет содержать узлы в порядке от входов к выходу (loss)
        """
        topo = []
        visited = set()

        def build_topo(v):
            if v not in visited:
                visited.add(v)
                for child in v._children:
                    build_topo(child)
                topo.append(v)

        """
        Обходим своих детей
        """
        build_topo(self)

        """
        Ключевой момент: dL/dL = 1 - производная по самому себе
        """
        self.grad = 1

        """ 
        # Идем в обратном порядке, от детей к родителю:
        """
        for v in reversed(topo):
            """
            Распространяем градиенты:
            v.grad = dL/dv
            local_grad = dv/dChild
            
            Считаем:
            Прибавляем значение, потому что узел может влиять на loss через несколько путей.
            Мы накапливаем градиенты.
            dL/dChild += dl/dv + dv/dChild
            
            Пример:
            Цепное правило (правило дифференцирования сложной функции):
            Если
            y = f(u)
            u = g(t)
            dy/dx = dy/du*du/dx
            
            Пример на функции:
            z = (x * y +x)^2
            
            Нужно разбить ее на граф, чтобы каждый шаг была простая операция у которой легко взять производную.
            Для этого каждый шаг помечаем другой переменной/
            
            Введем промежуточные переменные:
            a = x * y
            b = a + x
            z = b ** 2
            Граф получается такой:
            x ----\
                   → a = x*y ----\
            y ----/               \
                                  → b = a + x → z = b^2
            x --------------------/
            Каждый узел знает своих детей (_children) и локальные производные (_local_grads).
            
            Готовый autograd (например в PyTorch) тоже это делает, но строит граф на этапе выполнения кода через анализ переменных.
            P.S. Тензор в PyTorch это данные (скаляр, вектор, матрица или другое с произвольным кол-во измерений) + информация для автодифференцирования.
            """
            for child, local_grad in zip(v._children, v._local_grads):
                child.grad += local_grad * v.grad


# Initialize the parameters, to store the knowledge of the model
"""
Это глубина модели — сколько слоёв трансформера подряд.
Т.е. глубина (насколько "умная" по шагам)
"""
n_layer = 1  # depth of the transformer neural network (number of layers)

"""
Это размер embedding (ширина модели): в вектор из скольки чисел превращается токен.
Т.е. ширина (насколько "богато" представление)
"""
n_embd = 16  # width of the network (embedding dimension)

"""
Это максимальная длина контекста, которую модель видит за раз.
Т.е. размер окна внимания. Тут значения 16 хватает с учетом max длины имени
"""
block_size = 16  # maximum context length of the attention window (note: the longest name is 15 characters)

"""
Это количество “голов внимания” (attention heads).
Каждая голова смотрит на текст по своему, учит различные зависимости: например одна ловит грамматику, другая порядок слов, третья дальние связи.
"""
n_head = 4  # number of attention heads

"""
Делим окно внимания на кол-во голов и получаем что каждая голова работает с кусочком длины 4.
"""
head_dim = n_embd // n_head  # derived dimension of each head

"""
Функция для создания матрицы весов размера nout на nin.
random.gauss(0, std) 
"""
matrix = lambda nout, nin, std=0.08: [[Value(random.gauss(0, std)) for _ in range(nin)] for _ in range(nout)]

"""
Основные веса модели:
wte = word token embeddings = это словарь модели, каждому символу/слову свой вектор
wpe = positional embeddings = кодирует позицию токена (трансформер сам по себе не знает порядок, позиция добавляется вручную)
lm_head = преобразует скрытое состояние в вероятности токенов

Итого:
Этот минимальный GPT-подобный трансформер, он делает следующее:
1) преобразует токен в wte (т.е. делает embedding = встраивание в пространство числе (в векторное пространство) = способ представить объект в виде чисел)
2) добавляем позицию в wpe
3) прогон через attention (с n_head)
4) выход в lm_head получаем вероятности
"""
state_dict = {'wte': matrix(vocab_size, n_embd), 'wpe': matrix(block_size, n_embd),
              'lm_head': matrix(vocab_size, n_embd)}

"""
Инициализация весов для каждого слоя трансформера:
- attn_wq - Query = матрица для получения запросов в attention 
- attn_wk - Key = матрица для получения ключей в attention
- attn_wv - Value = матрица для получения значений в attention
- attn_wo - Output = матрица для получения выходов из attention
- mlp_fc1 - первая матрица в MLP блоке (обычно расширяет размерность, например 4*n_embd)
- mlp_fc2 - вторая матрица в MLP блоке (обычно сужает обратно до n_embd), это стандарт в трансформерах: сначала расширяем, потом сжимаем → лучше обучается

Вся архитектура слоя (упрощённо):
Один слой =
- Attention (Q, K, V, O)
- MLP (расширение → сжатие)
"""
for i in range(n_layer):
    state_dict[f'layer{i}.attn_wq'] = matrix(n_embd, n_embd)
    state_dict[f'layer{i}.attn_wk'] = matrix(n_embd, n_embd)
    state_dict[f'layer{i}.attn_wv'] = matrix(n_embd, n_embd)
    state_dict[f'layer{i}.attn_wo'] = matrix(n_embd, n_embd)
    state_dict[f'layer{i}.mlp_fc1'] = matrix(4 * n_embd, n_embd)
    state_dict[f'layer{i}.mlp_fc2'] = matrix(n_embd, 4 * n_embd)

"""
Все параметры модели в виде одного списка.
"""
params = [p for mat in state_dict.values() for row in mat for p in row]  # flatten params into a single list[Value]
print(f"num params: {len(params)}")


# Define the model architecture: a function mapping tokens and parameters to logits over what comes next
# Follow GPT-2, blessed among the GPTs, with minor differences: layernorm -> rmsnorm, no biases, GeLU -> ReLU

def linear(x, w):
    """
    Базовая линейная операция: Умножает вектор x на матрицу весов w, на выходе новый вектор.
    Применяется базовая алгебра: строка из матрицы весов умножается на входной вектор, и результатом является сумма для каждой строки, формируя новый вектор.
    (При применении к Value использует перегруженные операции в классе Value)
    """
    return [sum(wi * xi for wi, xi in zip(wo, x)) for wo in w]


def softmax(logits):
    """
    Нормализация через softmax.
    Ее используют, потому что она позволяет интерпретировать выход модели как вероятности для каждого токена.

    В отличие от жесткого максимума (Hardmax), который выдает 1 для самого высокого числа и 0 для остальных,
    Softmax — это «мягкая» функция, имеющая непрерывный градиент.
    Это позволяет обучать нейронные сети с использованием градиентного спуска.
    """
    max_val = max(val.data for val in logits)
    # считает e^(v - max)
    exps = [(val - max_val).exp() for val in logits]
    total = sum(exps)
    # нормализует, деля на сумму, чтобы получить вероятности
    return [e / total for e in exps]


def rmsnorm(x):
    """
    RMSNorm — метод нормализации, который масштабирует вектор по среднеквадратичному значению без вычитания среднего.

    Без нормализации:
    - значения могут "взрываться"
    - обучение становится нестабильным
    """
    # Считает средний квадратный корень
    ms = sum(xi * xi for xi in x) / len(x)
    # Нормализует вектор x, деля на средний квадратный корень, с добавлением маленького числа для стабильности чисел.
    # Обрати внимание на отрицательную степень - деление.
    # (добавление 1e-5 предотвращает деление на ноль и обеспечивает численную стабильность)
    scale = (ms + 1e-5) ** -0.5
    # Масштабирует нормализованный вектор, умножая на scale, чтобы сохранить масштаб представлений
    return [xi * scale for xi in x]


def gpt(token_id, pos_id, keys, values):
    """
    Вход: token_id — текущий токен, pos_id — его позиция, keys, values — память (контекст прошлых токенов)
    Выход: logits — «насколько вероятен каждый следующий токен»

    Берем смысл токена (wte) и его позицию (wpe), складываем их, чтобы получить начальное представление токена в контексте его позиции.
    Таким образом модели передается ЧТО ЭТО и ГДЕ ЭТО расположено в последовательности.
    В конце нормируем.
    """
    tok_emb = state_dict['wte'][token_id]  # token embedding
    pos_emb = state_dict['wpe'][pos_id]  # position embedding
    x = [t + p for t, p in zip(tok_emb, pos_emb)]  # joint token and position embedding
    x = rmsnorm(x)  # note: not redundant due to backward pass via the residual connection

    # Цикл по слоям трансформера:
    for li in range(n_layer):
        # 1) Multi-head Attention block
        """
        1) ЧАСТЬ 1: Внимание с multi-head:
        - Сначала сохраняем вход в x_residual для использования в остаточной связи (residual connection) после внимания.
        - Нормализуем x с помощью RMSNorm, чтобы стабилизировать обучение.
        - Вычисляем запросы (q), ключи (k) и значения (v) с помощью линейных преобразований от x.
        - Сохраняем ключи и значения в памяти для текущего слоя, чтобы они были доступны для будущих токенов.
        - Для каждой головы внимания:
          - Извлекаем соответствующие части q, k и v для этой головы.
          - Вычисляем логиты внимания, используя скаляное произведение между запросами и ключами, нормируя их по размеру головы.
          - Применяем softmax к логитам, чтобы получить веса внимания.
          - Вычисляем выход головы, взвешивая значения v с помощью весов внимания и суммируя их.
        - Объединяем выходы всех голов и пропускаем их через линейное преобразование, чтобы получить итоговый выход внимания.
        - Добавляем остаточную связь, складывая выход внимания с x_residual, чтобы сохранить информацию от входа и облегчить обучение.  
        
        Делят на головы, чтобы модель могла смотреть на информацию разными способами одновременно. Если будет одна голова, 
        то она уловит только один тип зависимости, а с несколькими головами модель может уловить разные типы зависимостей в тексте.
        
        """
        x_residual = x
        x = rmsnorm(x)
        """
        Q — «что я ищу»
        K — «что есть»
        V — «что брать»
        """
        q = linear(x, state_dict[f'layer{li}.attn_wq'])
        k = linear(x, state_dict[f'layer{li}.attn_wk'])
        v = linear(x, state_dict[f'layer{li}.attn_wv'])

        # Сохраняем ключи и значения в памяти, накапливаем прошлые токены для текущего слоя.
        keys[li].append(k)
        values[li].append(v)

        """
        Делим вектора Q, K, V на головы.
        Считаем внимание по этим кускам: 
        - attn_logits - насколько текущий токен связан с каждым прошлым, 
        - attn_weights - нормализованные веса внимания из attn_logits, 
        - head_out - берём важную информацию из прошлого, взвешивая значения V с помощью attn_weights и суммируя их.
        
        Склеиваем головы обратно в один вектор и пропускаем через линейное преобразование, чтобы получить итоговый выход внимания - x.
        Прибавляем к нему остаточную связь - x_residual, чтобы сохранить информацию от входа и облегчить обучение.
        """
        x_attn = []
        for h in range(n_head):
            hs = h * head_dim
            q_h = q[hs:hs + head_dim]
            k_h = [ki[hs:hs + head_dim] for ki in keys[li]]
            v_h = [vi[hs:hs + head_dim] for vi in values[li]]
            attn_logits = [sum(q_h[j] * k_h[t][j] for j in range(head_dim)) / head_dim ** 0.5 for t in range(len(k_h))]
            attn_weights = softmax(attn_logits)
            head_out = [sum(attn_weights[t] * v_h[t][j] for t in range(len(v_h))) for j in range(head_dim)]
            x_attn.extend(head_out)
        x = linear(x_attn, state_dict[f'layer{li}.attn_wo'])
        x = [a + b for a, b in zip(x, x_residual)]

        """
        ЧАСТЬ 2: MLP (простая нейросеть)
        """
        """
        1) Сохраняем старое значение
        """
        x_residual = x
        """
        2) Приводим значения к стабильному масштабу
        """
        x = rmsnorm(x)
        """
        3) Расширяем размерность с помощью первой линейной матрицы (обычно 4*n_embd)
        """
        x = linear(x, state_dict[f'layer{li}.mlp_fc1'])
        """
        4) Обнуляем всё отрицательное (ReLU), relu = max(0, x) - он обнуляет отрицательные значения, чтобы модель могла 
        учиться на положительных активациях и не застревать в негативных.
        """
        x = [xi.relu() for xi in x]
        """
        5) Сжимаем обратно до n_embd с помощью второй линейной матрицы
        """
        x = linear(x, state_dict[f'layer{li}.mlp_fc2'])
        """
        6) Добавляем остаточную связь, чтобы сохранить информацию от входа и облегчить обучение.
        """
        x = [a + b for a, b in zip(x, x_residual)]

    """
    В финале: делается предсказание: logits = linear(x, state_dict['lm_head'])
    Где x - это результат прохождения через все слои трансформера (понимание), 
    а state_dict['lm_head'] - это матрица весов, которая преобразует скрытое состояние в вероятности токенов.
    Модель продумала и сжала это в 1 вектор.
        
    Очень важная идея:
    lm_head имеет размер [vocab_size * n_embd] - модель сравнивает своё состояние x со всеми словами сразу.
    Аналогия: у тебя есть смысл предложения * список слов и ты проверяешь какое слово лучше подходит. 
    """
    logits = linear(x, state_dict['lm_head'])
    return logits


# Let there be Adam, the blessed optimizer and its buffers
"""
Здесь начинается обучение модели.
Это веса оптимизатора Adam, который будет обновлять параметры модели на основе градиентов, вычисленных в обратном проходе.
- learning_rate = 0.01 - насколько сильно менять веса, большое = быстро и нестабильно, маленькое - медленно и стабильно 
  (0.01 - это довольно агрессивная скорость обучения, но с учетом того, что мы делаем всего 1000 шагов, это может работать) 
- beta1 = 0.85 - насколько мы учитываем прошлые шаги, коэффициент для первого момента (скользящее среднее градиентов), 
  обычно 0.9, но 0.85 может работать лучше для такой маленькой модели
- beta2 = 0.99 - насколько мы учитываем прошлые шаги, коэффициент для второго момента (скользящее среднее квадратов градиентов), 
  это нужно чтобы понимать, насколько градиенты шумные
- eps_adam = 1e-8 - маленькое число для предотвращения деления на ноль в формуле обновления Adam
"""
learning_rate, beta1, beta2, eps_adam = 0.01, 0.85, 0.99, 1e-8

"""
Память для каждого параметра, чтобы хранить скользящее среднее градиентов (m) и скользящее среднее квадратов градиентов (v) для оптимизатора Adam.
Представь, ты спускаешься с горы:

Обычный SGD: просто идёшь вниз
Adam:
- помнит, куда шёл раньше
- замедляется, если трясёт
- ускоряется, если всё ровно

Без хорошего оптимизатора: модель плохо обучается или вообще не сходится
"""
m = [0.0] * len(params)  # first moment buffer
v = [0.0] * len(params)  # second moment buffer

# Repeat in sequence
"""
Обучаем на 1000 шагах. На каждом шаге:
"""
num_steps = 1000  # number of training steps
for step in range(num_steps):
    # Take single document, tokenize it, surround it with BOS special token on both sides
    """
    1) Берем один документ,  Слова перебираются по кругу, независимо от кол-ва шагов и слов.
    Слова перебираются по кругу, независимо от кол-ва шагов и слов.
    """
    doc = docs[step % len(docs)]
    """
    2) Токенизируем его, добавляем специальный токен BOS в начале и в конце, чтобы модель понимала, 
    где начинается и заканчивается последовательность.
    """
    tokens = [BOS] + [uchars.index(ch) for ch in doc] + [BOS]

    """
    3) Ограничиваем длину (контекст)
    """
    n = min(block_size, len(tokens) - 1)

    # Forward the token sequence through the model, building up the computation graph all the way to the loss
    """
    4) готовим память для attention
    """
    keys, values = [[] for _ in range(n_layer)], [[] for _ in range(n_layer)]
    losses = []

    """
    5) Проходим по каждому символу в токенизированной последовательности, предсказывая следующий символ и вычисляя ошибку (loss) для каждого предсказания.
    """
    for pos_id in range(n):
        """
        token_id - текущий токен, который мы подаем на вход модели
        target_id - следующий токен, который модель должна предсказать (цель) 
        """
        token_id, target_id = tokens[pos_id], tokens[pos_id + 1]

        """
        Прогон через модель
        """
        logits = gpt(token_id, pos_id, keys, values)
        probs = softmax(logits)
        """
        Считаем ошибку (loss) для текущего предсказания, используя отрицательный логарифм вероятности правильного следующего токена.
        Это cross-entropy loss, если модель угадала - маленькая ошибка, иначе большая.
        """
        loss_t = -probs[target_id].log()

        """
        Сохраняем ошибку для текущего предсказания, чтобы потом усреднить по всей последовательности.
        """
        losses.append(loss_t)

    """
    Усредняем ошибку по всей последовательности, чтобы получить итоговую ошибку для этого документа.
    """
    loss = (1 / n) * sum(losses)  # final average loss over the document sequence. May yours be low.

    # Backward the loss, calculating the gradients with respect to all model parameters
    """
    6) Вызываем backward() на итоговой ошибке, чтобы запустить обратный проход и вычислить градиенты для всех параметров модели.
    """
    loss.backward()

    # Adam optimizer update: update the model parameters based on the corresponding gradients
    """"
    7) Обновляем параметры модели с помощью оптимизатора Adam, используя вычисленные градиенты.
     - Сначала вычисляем текущую скорость обучения с линейным затуханием (learning rate decay), чтобы постепенно уменьшать скорость обучения по мере обучения модели.
     - Затем для каждого параметра обновляем скользящее среднее градиентов (m) и скользящее среднее квадратов градиентов (v) с помощью коэффициентов beta1 и beta2.
     - Вычисляем bias-corrected версии m и v (m_hat и v_hat), чтобы компенсировать начальное смещение в начале обучения.
     - Наконец, обновляем параметр, вычитая из него нормализованный градиент, масштабированный текущей скоростью обучения, и обнуляем градиент для следующего шага.
     - Печатаем текущий шаг и ошибку, чтобы отслеживать процесс обучения.
     - В конце цикла печатаем итоговую ошибку для текущего документа.
     - Этот процесс повторяется для каждого документа в течение заданного количества шагов обучения.
     - В итоге модель учится предсказывать следующий символ в последовательности, улучшая свои представления о данных с каждым шагом.
     - После обучения модель может генерировать новые последовательности, используя приобретенные знания о структуре данных.
     - Это базовый цикл обучения для GPT-подобной модели на уровне отдельных операций без использования фреймворков глубокого обучения.
     - Он демонстрирует ключевые компоненты: прямой проход, вычисление ошибки, обратный проход и обновление параметров с помощью оптимизатора Adam.
     - Такой подход позволяет глубоко понять внутреннюю работу трансформера и оптимизатора на самом базовом уровне.
     - В реальных приложениях обычно используются более сложные архитектуры и оптимизации для ускорения обучения и улучшения производительности модели.
    """
    lr_t = learning_rate * (1 - step / num_steps)  # linear learning rate decay
    for i, p in enumerate(params):
        """
        Запоминаем средний градиент и его силу для каждого параметра, чтобы оптимизатор Adam мог адаптировать шаг обучения для каждого параметра индивидуально.
        """
        m[i] = beta1 * m[i] + (1 - beta1) * p.grad
        v[i] = beta2 * v[i] + (1 - beta2) * p.grad ** 2
        """
        Корректируем смещение в начале обучения, чтобы получить более точные оценки для m и v, особенно на первых шагах, когда они еще не накопили достаточно информации.
         - m_hat - это скорректированное скользящее среднее градиентов, которое учитывает количество шагов обучения, чтобы компенсировать начальное смещение.
         - v_hat - это скорректированное скользящее среднее квадратов градиентов, которое также учитывает количество шагов обучения для компенсации начального смещения.    
        """
        m_hat = m[i] / (1 - beta1 ** (step + 1))
        v_hat = v[i] / (1 - beta2 ** (step + 1))

        """
        Обновление веса модели: вычитаем из параметра нормализованный градиент, масштабированный текущей скоростью обучения.
        """
        p.data -= lr_t * m_hat / (v_hat ** 0.5 + eps_adam)
        p.grad = 0

    print(f"step {step + 1:4d} / {num_steps:4d} | loss {loss.data:.4f}", end='\r')

# Inference: may the model babble back to us
"""
Генерация результата после обучения модели. 
Здесь мы используем модель для генерации новых последовательностей, которые могут быть похожи на те, 
что были в обучающем наборе данных, но не обязательно совпадать с ними.

temperature - управляет случайностью:
- <1 - более уверено, меньше хаоса
- =1 - как есть
- >1 - более хаотично, больше креативности, может выдавать неожиданные результаты
"""
temperature = 0.5  # in (0, 1], control the "creativity" of generated text, low to high
print("\n--- inference (new, hallucinated names) ---")
for sample_idx in range(20):
    """
    1) Очищаем контекст, каждый sample генерируется с нуля
    """
    keys, values = [[] for _ in range(n_layer)], [[] for _ in range(n_layer)]

    """
    2) Начинаем с BOS
    """
    token_id = BOS
    sample = []
    for pos_id in range(block_size):
        """
        3) Прогоняем текущий токен через модель, чтобы получить логиты для следующего токена, 
        нормализуем их в вероятности и выбираем следующий токен на основе этих вероятностей.
        """
        logits = gpt(token_id, pos_id, keys, values)

        """
        4) Делим логиты на 0.5 → увеличиваем различия, сильные становятся сильнее, слабые - слабее, делая выбор более уверенным.
        """
        probs = softmax([l / temperature for l in logits])

        """
        5) Выбираем следующий токен на основе вероятностей, используя random.choices, который позволяет делать выбор с учетом весов (вероятностей).
        """
        token_id = random.choices(range(vocab_size), weights=[p.data for p in probs])[0]

        """
        Генерация закончилась
        """
        if token_id == BOS:
            break

        sample.append(uchars[token_id])

    print(f"sample {sample_idx + 1:2d}: {''.join(sample)}")
