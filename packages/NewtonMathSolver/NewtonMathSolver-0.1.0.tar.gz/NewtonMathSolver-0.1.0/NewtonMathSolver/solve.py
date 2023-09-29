import json
import re

from sympy import diff
from sympy.core.symbol import symbols, sympify, Symbol


class MathCompile:
    equalSign = re.compile(r'(.*?)=(.*)')


class Types:
    class ToleranceType(type):
        def __repr__(self):
            return "<class 'Tolerance'>"

    class MathEquationType(type):
        def __repr__(self):
            return "<class 'math equation'>"

    class MathResultType(type):
        def __repr__(self):
            return "<class 'math result'>"

    class NewtonMathSolverType(type):
        def __repr__(self):
            return "<class 'math solver for newton method'>"


class Tolerance(metaclass=Types.ToleranceType):
    def __init__(self, tolerance=None, level=None):
        if tolerance is not None:
            self.tolerance = tolerance

        elif level is not None:
            self.tolerance = 10 ** -level

    def more(self, level=1):
        self.tolerance /= 10 ** level

    def less(self, level=1):
        self.tolerance *= 10 ** level

    def __repr__(self):
        return f'<Tolerance {self.tolerance}>'

    def __str__(self):
        return str(self.tolerance)

    def __eq__(self, other):
        return self.tolerance == other

    def __lt__(self, other):
        return self.tolerance < other

    def __le__(self, other):
        return self.tolerance <= other

    def __gt__(self, other):
        return self.tolerance > other

    def __ge__(self, other):
        return self.tolerance >= other

    def __add__(self, other):
        if isinstance(other, int):
            self.tolerance += other
        return self.tolerance

    def __sub__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            self.tolerance -= other
        return self.tolerance

    def __mul__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            self.tolerance *= other
        return self.tolerance

    def __truediv__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            self.tolerance /= other
        return self.tolerance

    def __pow__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            self.tolerance **= other
        return self.tolerance


class MathEquation(metaclass=Types.MathEquationType):
    def __init__(self, function, unknown):
        """
        Parameters:
            function(str): eg. "x + 1", "sin(x)", "sin(x) + 1 = 0", "cos(x) + 1 / 2 = 0.5"

            unknown(str or Symbol): eg. "x", "t", "i", symbols("x")
        """
        self.raw = function
        self.function = None
        self.unknown = None
        self.initialize(function, unknown)

    def initialize(self, function, unknown):
        self.function = self.process(function)
        self.unknown = self.symbol(unknown)

    @staticmethod
    def process(function):
        if MathCompile.equalSign.match(function) is not None:
            function = f'{MathCompile.equalSign.match(function)[1]} - ({MathCompile.equalSign.match(function)[2]})'

        return sympify(function)

    @staticmethod
    def symbol(unknown):
        if isinstance(unknown, Symbol):
            return unknown
        else:
            if isinstance(unknown, str):
                return symbols(unknown)
            else:
                raise TypeError(f'Disallowed type "{type(unknown)}", should be string or Symbol.')

    def eval(self, x):
        return self.function.subs(self.unknown, x)


class DerivativeFunctionEquation(MathEquation):
    def __init__(self, function, unknown):
        """
        Parameters:
            function(str): eg. "x + 1", "sin(x)", "sin(x) + 1 = 0", "cos(x) + 1 / 2 = 0.5"

            unknown(str or Symbol): eg. "x", "t", "i", symbols("x")
        """
        MathEquation.__init__(self, function, unknown)

        self.derivativeFunction = diff(self.function, self.unknown)

    def derivative(self, x):
        return self.derivativeFunction.subs(self.unknown, x)


class NewtonMathMethod(DerivativeFunctionEquation):
    def __init__(self, function, unknown, guess=0.0, tolerance=1e-6):
        """
        Parameters:
            function(str): eg. "x + 1", "sin(x)", "sin(x) + 1 = 0", "cos(x) + 1 / 2 = 0.5"

            unknown(str or Symbol): eg. "x", "t", "i", symbols("x")

            guess(float): eg. 1, 0.1, 999 * 999, 999 ** 2, 666 / 2, 1e+6

            tolerance(Tolerance or float): eg. 1, 100, 999 ** 999, 1e-5 , 1e-6, 1e-999,
                Tolerance(1e-6), Tolerance(level=6)
        """
        DerivativeFunctionEquation.__init__(self, function, unknown)

        self.guess = guess
        if isinstance(tolerance, Tolerance):
            self.tolerance = tolerance
        else:
            self.tolerance = Tolerance(tolerance)

    def result(self):
        return NewtonMathMethodResult(
            guess=self.guess,
            value=self.eval(self.guess),
            derivative=self.derivative(self.guess),
            tolerance=self.tolerance
        )


class NewtonMathMethodResult(metaclass=Types.MathResultType):
    def __init__(self, guess, value, derivative, tolerance):
        """
        Parameters:
            guess(float): eg. 1, 0.1, 999 * 999, 999 ** 2, 666 / 2, 1e+6

            value(int or float): x value of function. value = f(x)

            derivative(int or float): x value of derivative function. derivative = f'(x)

            tolerance(Tolerance or float): eg. 1, 100, 999 ** 999, 1e-5 , 1e-6, 1e-999,
                Tolerance(1e-6), Tolerance(level=6)
        """
        self.guess = guess
        self.value = value
        self.derivative = derivative

        if isinstance(tolerance, Tolerance):
            self.tolerance = tolerance
        else:
            self.tolerance = Tolerance(tolerance)

        self.xn = self.guess - self.value / self.derivative
        self.error = abs(self.xn - self.guess)

        self.result = self.error < self.tolerance

    def dict(self):
        return {
            'guess': self.guess,
            'value': self.value,
            'derivative': self.derivative,
            'tolerance': self.tolerance,
            'xn': self.xn,
            'error': self.error,
            'result': self.result
        }

    def __repr__(self):
        return ' '.join(
            [
                '<' + 'NewtonMathMethodResult',
                f'guess={self.guess}',
                f'value={self.value}',
                f'derivative={self.derivative}',
                f'tolerance={self.tolerance}',
                f'xn={self.xn}',
                f'error={self.error}',
                f'result={self.result}' + '>'
            ]
        )

    def __str__(self):
        return json.dumps(
            {
                'guess': str(self.guess),
                'value': str(self.value),
                'derivative': str(self.derivative),
                'tolerance': str(self.tolerance),
                'xn': str(self.xn),
                'error': str(self.error),
                'result': str(self.result)
            },
            indent=4
        )


class NewtonMathSolver(metaclass=Types.NewtonMathSolverType):
    def __init__(self, function, unknown, guess=0.0, tolerance=1e-6):
        """
        Parameters:
            function(str): eg. "x + 1", "sin(x)", "sin(x) + 1 = 0", "cos(x) + 1 / 2 = 0.5"

            unknown(str or Symbol): eg. "x", "t", "i", symbols("x")

            guess(float): eg. 1, 0.1, 999 * 999, 999 ** 2, 666 / 2, 1e+6

            tolerance(Tolerance or float): eg. 1, 100, 999 ** 999, 1e-5 , 1e-6, 1e-999,
                Tolerance(1e-6), Tolerance(level=6)
        """
        self.newton = NewtonMathMethod(function, unknown, guess, tolerance)
        self.result = None

    def iterate(self, number=1):
        for _ in range(number):
            self.result = self.newton.result()
            if self.result.result:
                return self.result.xn
            self.newton.guess = self.result.xn
        return False


if __name__ == "__main__":
    n = NewtonMathSolver('x - 1 = 10', 'x', 2, Tolerance(level=6))
    print(n.iterate(10))
    print(n.result)
