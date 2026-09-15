M = 10
N = 100
DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


if M < 2 or M > len(DIGITS):
    raise ValueError("M must be between 2 and 36")


# Removes insignificant leading zero digits.
def normalize(digits):
    while len(digits) > 1 and digits[-1] == 0:
        digits = digits[:-1]
    return digits


# Creates a normalized number from a sign and a list of digits.
def make_number(sign, digits):
    digits = normalize(digits)
    if digits == [0]:
        sign = 1
    return [sign, digits]


# Converts text into the internal number representation.
def read_number(text):
    text = text.strip().upper()

    if not text:
        raise ValueError("empty number")

    sign = 1

    if text[0] in "+-":
        if text[0] == "-":
            sign = -1
        text = text[1:]

    if not text:
        raise ValueError("number has no digits")

    digits = []
    for symbol in reversed(text):
        if symbol not in DIGITS[:M]:
            raise ValueError("invalid digit: " + symbol)
        digits.append(DIGITS.index(symbol))

    return make_number(sign, digits)


# Converts an internal number representation into text.
def number_to_text(number):
    sign = number[0]
    digits = number[1]
    text = "".join(DIGITS[digit] for digit in reversed(digits))

    if sign == -1:
        text = "-" + text

    return text


# Compares magnitudes and returns -1, 0, or 1.
def compare_abs(a, b):
    if len(a) < len(b):
        return -1
    if len(a) > len(b):
        return 1

    i = len(a) - 1
    while i >= 0:
        if a[i] < b[i]:
            return -1
        if a[i] > b[i]:
            return 1
        i = i - 1

    return 0


# Adds two magnitudes digit by digit.
def add_abs(a, b):
    result = []
    carry = 0
    i = 0

    while i < len(a) or i < len(b) or carry > 0:
        value = carry

        if i < len(a):
            value = value + a[i]
        if i < len(b):
            value = value + b[i]

        result.append(value % M)
        carry = value // M
        i = i + 1

    return result


# Subtracts magnitude b from a, assuming a is not smaller than b.
def subtract_abs(a, b):
    result = []
    borrow = 0
    i = 0

    while i < len(a):
        value = a[i] - borrow

        if i < len(b):
            value = value - b[i]

        if value < 0:
            value = value + M
            borrow = 1
        else:
            borrow = 0

        result.append(value)
        i = i + 1

    return normalize(result)


# Adds two signed numbers.
def add(a, b):
    if a[0] == b[0]:
        return make_number(a[0], add_abs(a[1], b[1]))

    comparison = compare_abs(a[1], b[1])

    if comparison == 0:
        return [1, [0]]
    if comparison > 0:
        return make_number(a[0], subtract_abs(a[1], b[1]))
    return make_number(b[0], subtract_abs(b[1], a[1]))


# Subtracts signed number b from a.
def subtract(a, b):
    opposite_b = [-b[0], b[1]]
    return add(a, opposite_b)


# Multiplies two magnitudes digit by digit.
def multiply_abs(a, b):
    result = [0] * (len(a) + len(b))
    i = 0

    while i < len(a):
        j = 0
        while j < len(b):
            result[i + j] = result[i + j] + a[i] * b[j]
            j = j + 1
        i = i + 1

    carry = 0
    i = 0
    while i < len(result):
        value = result[i] + carry
        result[i] = value % M
        carry = value // M
        i = i + 1

    if carry > 0:
        result.append(carry)

    return normalize(result)


# Multiplies two signed numbers.
def multiply(a, b):
    sign = a[0] * b[0]
    return make_number(sign, multiply_abs(a[1], b[1]))


# Divides two magnitudes and returns the quotient and remainder.
def divide_abs(a, b):
    if b == [0]:
        raise ZeroDivisionError("division by zero")

    quotient = []
    remainder = [0]
    i = len(a) - 1

    while i >= 0:
        remainder = normalize([a[i]] + remainder)
        quotient_digit = 0

        while compare_abs(remainder, b) >= 0:
            remainder = subtract_abs(remainder, b)
            quotient_digit = quotient_digit + 1

        quotient.append(quotient_digit)
        i = i - 1

    quotient.reverse()
    return [normalize(quotient), remainder]


# Performs floor division on two signed numbers.
def floor_divide(a, b):
    division = divide_abs(a[1], b[1])
    quotient = division[0]
    remainder = division[1]

    if a[0] == b[0]:
        return make_number(1, quotient)

    # With different signs, // rounds down.
    if remainder != [0]:
        quotient = add_abs(quotient, [1])

    return make_number(-1, quotient)


print("Основание M =", M)
print("Максимальное количество разрядов N =", N)

try:
    first = read_number(input("Первое целое число: "))
    operation = input("Операция (+, -, *, //): ")
    second = read_number(input("Второе целое число: "))
except ValueError as error:
    print("Ошибка:", error)
    raise SystemExit

result = []

if len(first[1]) > N or len(second[1]) > N:
    print("Ошибка: в числе больше", N, "разрядов")
elif operation == "+":
    result = add(first, second)
elif operation == "-":
    result = subtract(first, second)
elif operation == "*":
    result = multiply(first, second)
elif operation == "//":
    if second[1] == [0]:
        print("Ошибка: деление на ноль")
    else:
        result = floor_divide(first, second)
else:
    print("Ошибка: неизвестная операция")

if result != []:
    if len(result[1]) > N:
        print("Ошибка: результат содержит больше", N, "разрядов")
    else:
        print("Результат:", number_to_text(result))
