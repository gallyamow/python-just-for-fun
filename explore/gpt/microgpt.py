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

for i in range(n_layer):
  state_dict[f'layer{i}.attn_wq'] = matrix(n_embd, n_embd)
  state_dict[f'layer{i}.attn_wk'] = matrix(n_embd, n_embd)
  state_dict[f'layer{i}.attn_wv'] = matrix(n_embd, n_embd)
  state_dict[f'layer{i}.attn_wo'] = matrix(n_embd, n_embd)
  state_dict[f'layer{i}.mlp_fc1'] = matrix(4 * n_embd, n_embd)
  state_dict[f'layer{i}.mlp_fc2'] = matrix(n_embd, 4 * n_embd)
params = [p for mat in state_dict.values() for row in mat for p in row]  # flatten params into a single list[Value]
print(f"num params: {len(params)}")


# Define the model architecture: a function mapping tokens and parameters to logits over what comes next
# Follow GPT-2, blessed among the GPTs, with minor differences: layernorm -> rmsnorm, no biases, GeLU -> ReLU
def linear(x, w):
  return [sum(wi * xi for wi, xi in zip(wo, x)) for wo in w]


def softmax(logits):
  max_val = max(val.data for val in logits)
  exps = [(val - max_val).exp() for val in logits]
  total = sum(exps)
  return [e / total for e in exps]


def rmsnorm(x):
  ms = sum(xi * xi for xi in x) / len(x)
  scale = (ms + 1e-5) ** -0.5
  return [xi * scale for xi in x]


def gpt(token_id, pos_id, keys, values):
  tok_emb = state_dict['wte'][token_id]  # token embedding
  pos_emb = state_dict['wpe'][pos_id]  # position embedding
  x = [t + p for t, p in zip(tok_emb, pos_emb)]  # joint token and position embedding
  x = rmsnorm(x)  # note: not redundant due to backward pass via the residual connection

  for li in range(n_layer):
      # 1) Multi-head Attention block
      x_residual = x
      x = rmsnorm(x)
      q = linear(x, state_dict[f'layer{li}.attn_wq'])
      k = linear(x, state_dict[f'layer{li}.attn_wk'])
      v = linear(x, state_dict[f'layer{li}.attn_wv'])
      keys[li].append(k)
      values[li].append(v)
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
      # 2) MLP block
      x_residual = x
      x = rmsnorm(x)
      x = linear(x, state_dict[f'layer{li}.mlp_fc1'])
      x = [xi.relu() for xi in x]
      x = linear(x, state_dict[f'layer{li}.mlp_fc2'])
      x = [a + b for a, b in zip(x, x_residual)]

  logits = linear(x, state_dict['lm_head'])
  return logits


# Let there be Adam, the blessed optimizer and its buffers
learning_rate, beta1, beta2, eps_adam = 0.01, 0.85, 0.99, 1e-8
m = [0.0] * len(params)  # first moment buffer
v = [0.0] * len(params)  # second moment buffer

# Repeat in sequence
num_steps = 1000  # number of training steps
for step in range(num_steps):

  # Take single document, tokenize it, surround it with BOS special token on both sides
  doc = docs[step % len(docs)]
  tokens = [BOS] + [uchars.index(ch) for ch in doc] + [BOS]
  n = min(block_size, len(tokens) - 1)

  # Forward the token sequence through the model, building up the computation graph all the way to the loss
  keys, values = [[] for _ in range(n_layer)], [[] for _ in range(n_layer)]
  losses = []
  for pos_id in range(n):
      token_id, target_id = tokens[pos_id], tokens[pos_id + 1]
      logits = gpt(token_id, pos_id, keys, values)
      probs = softmax(logits)
      loss_t = -probs[target_id].log()
      losses.append(loss_t)
  loss = (1 / n) * sum(losses)  # final average loss over the document sequence. May yours be low.

  # Backward the loss, calculating the gradients with respect to all model parameters
  loss.backward()

  # Adam optimizer update: update the model parameters based on the corresponding gradients
  lr_t = learning_rate * (1 - step / num_steps)  # linear learning rate decay
  for i, p in enumerate(params):
      m[i] = beta1 * m[i] + (1 - beta1) * p.grad
      v[i] = beta2 * v[i] + (1 - beta2) * p.grad ** 2
      m_hat = m[i] / (1 - beta1 ** (step + 1))
      v_hat = v[i] / (1 - beta2 ** (step + 1))
      p.data -= lr_t * m_hat / (v_hat ** 0.5 + eps_adam)
      p.grad = 0

  print(f"step {step + 1:4d} / {num_steps:4d} | loss {loss.data:.4f}", end='\r')

# Inference: may the model babble back to us
temperature = 0.5  # in (0, 1], control the "creativity" of generated text, low to high
print("\n--- inference (new, hallucinated names) ---")
for sample_idx in range(20):
  keys, values = [[] for _ in range(n_layer)], [[] for _ in range(n_layer)]
  token_id = BOS
  sample = []
  for pos_id in range(block_size):
      logits = gpt(token_id, pos_id, keys, values)
      probs = softmax([l / temperature for l in logits])
      token_id = random.choices(range(vocab_size), weights=[p.data for p in probs])[0]
      if token_id == BOS:
          break
      sample.append(uchars[token_id])
  print(f"sample {sample_idx + 1:2d}: {''.join(sample)}")
