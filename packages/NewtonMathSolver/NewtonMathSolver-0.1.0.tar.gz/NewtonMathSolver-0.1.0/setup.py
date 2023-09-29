from setuptools import setup, find_packages

LICENSE = '''MIT License

Copyright (c) 2023 MoYeRanQianZhi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

md = r'''# NewtonMathSolver

> 使用牛顿法无限迭代求任意方程近似解

## 基础调用

```python
from NewtonMathSolver import Tolerance, NewtonMathSolver

n = NewtonMathSolver('x - 1 = 10', 'x', 2, Tolerance(level=6))
print(n.iterate(10))
print(n.result)

```

与之等效的是

```python
from NewtonMathSolver import Tolerance, NewtonMathSolver

n = NewtonMathSolver('x - 1 = 10', 'x', 2, 1e-6)
print(n.iterate(10))
print(n.result)

```

## 进一步探究

这样可以看到计算步骤

```python
from NewtonMathSolver import Tolerance, NewtonMathSolver

n = NewtonMathSolver('x - 1 = 10', 'x', 2, Tolerance(level=6))

while 1 + 1 == 2:
    n.iterate()
    print(n.result)
    if n.result.result:
        break

```

### 容忍与误差

使用牛顿法通常会有误差，于是我们会将误差与设定的容忍度进行对比，容忍度即误差允许的最大值

这样可以设定一个可操作的误差

```python
from NewtonMathSolver import Tolerance

t = Tolerance(1e-6)

```

与之等价的是

```python
from NewtonMathSolver import Tolerance

t = Tolerance(level=6)

```

以及

```python
from NewtonMathSolver import Tolerance

t = Tolerance(1e-6, 666)
# 若是同时存在两个参数，则tolerance优先

```

其可以进行多种操作

### 自增

```python
from NewtonMathSolver import Tolerance

t = Tolerance(level=6)
```

以下操作均允许

```python
t + 1
print('t + 1', t)
```

t + 1 1.000001

```python
t - 1
print('t - 1', t)
```

t - 1 9.999999999177334e-07

```python
t * 2
print('t * 2', t)
```

t * 2 1.9999999998354667e-06

```python
t / 2
print('t / 2', t)
```

t / 2 9.999999999177334e-07

```python
t ** 2
print('t ** 2', t)
```

t ** 2 9.999999998354668e-13

```python
t ** (1 / 2)
print('t ** (1 / 2)', t)
```

t ** (1 / 2) 9.999999999177334e-07

```python
t.more()
print('more', t)
```

more 9.999999999177333e-08

```python
t.less()
print('less', t)
```

less 9.999999999177334e-07

### 逻辑运算

```python
print(t == 0)
print(t > 0)
print(t >= 0)
print(t < 1)
print(t <= 1e-7)
```

False

True

True

True

False
'''

setup(
    name='NewtonMathSolver',
    version='0.1.0',
    packages=find_packages(),
    url='https://github.com/MoYeRanqianzhi/NewtonMathSolver',
    license=LICENSE,
    author='MoYeRanQianZhi',
    author_email='moyeranqianzhi@gmail.com',
    description='Use newton method to iterate infinitely to find an approximate solution to any equation.',
    long_description=md,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    python_requires='>=3.6.0',
    requires=[
        'sympy'
    ]
)

