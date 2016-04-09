#!/usr/bin/env python
from cmd import Cmd
import sys

HOURS_IN_DAY = 8
DAYS_IN_WEEK = 5
WEEKS_IN_MONTH = 4
MONTHS_IN_YEAR = 12

HOURS_IN_WEEK = HOURS_IN_DAY * DAYS_IN_WEEK
HOURS_IN_MONTH = HOURS_IN_WEEK * WEEKS_IN_MONTH
HOURS_IN_YEAR = HOURS_IN_MONTH * MONTHS_IN_YEAR


class Token:
    def __init__(self, token_type, value, column):
        self.token_type = token_type
        self.value = value
        self.column = column

    def __str__(self):
        if self.token_type == TokenType.NUMBER:
            if self.value == None: return "NUMBER"
            return "NUMBER(%d)" % (self.value)

        if self.token_type == TokenType.PERIOD:
            val = ""
            if self.value == None: return "PERIOD"
            elif self.value == Period.HOUR: val = 'HOUR'
            elif self.value == Period.DAY: val = 'DAY'
            elif self.value == Period.WEEK: val = 'WEEK'
            elif self.value == Period.MONTH: val = 'MONTH'
            elif self.value == Period.YEAR: val = 'YEAR'
            return "PERIOD(%s)" % (val)

        if self.token_type == TokenType.OPERATOR:
            val = ""
            if self.value == None: return "OPERATOR"
            elif self.value == Operator.PLUS: val = 'PLUS'
            elif self.value == Operator.MINUS: val = 'MINUS'
            return "OPERATOR(%s)" % (val)

        return ""

class TokenType:
    """Token types"""
    NUMBER = 0
    PERIOD = 1
    OPERATOR = 2

class Period:
    """Represents a time estimation period, d (day), w (week) etc."""
    HOUR = 0
    DAY = 1
    WEEK = 2
    MONTH = 3
    YEAR = 4

class Operator:
    """Operator types"""
    PLUS = 0
    MINUS = 1


def in_hours(value, period):
    if period == Period.HOUR: return value
    if period == Period.DAY: return value * HOURS_IN_DAY
    if period == Period.WEEK: return value * HOURS_IN_WEEK
    if period == Period.MONTH: return value * HOURS_IN_MONTH
    if period == Period.YEAR: return value * HOURS_IN_YEAR
    raise ValueError("Unknown period type " + period)

def hours_to_string(value, prefix=""):
    if value == 0: return ""
    if value < HOURS_IN_DAY: return prefix + str(value)+"h"
    if value < HOURS_IN_WEEK: return prefix + str(value/HOURS_IN_DAY) + "d" + hours_to_string(value % HOURS_IN_DAY, " ")
    if value < HOURS_IN_MONTH: return prefix + str(value/HOURS_IN_WEEK) + "w" + hours_to_string(value % HOURS_IN_WEEK, " ")
    if value < HOURS_IN_YEAR: return prefix + str(value/HOURS_IN_MONTH) + "m" + hours_to_string(value % HOURS_IN_MONTH, " ")
    return prefix + str(value/HOURS_IN_YEAR) + "y" + hours_to_string(value % HOURS_IN_YEAR, " ")


class InvalidCharError(Exception):
    def __init__(self, char):
        self.value = "Invalid character " + char

class UnexpectedTokenError(Exception):
    def __init__(self, token, expected):
        pr = (str(token), token.column, [str(Token(e, None, None)) for e in expected])
        self.value = "Unexpected token %s at col %d. Expected %s" % pr


class Tokenizer:
    """Breaks up an expression such as 2w + 3d into constituent tokens:
    NUMBER(2) PERIOD(WEEK) OPERATOR(PLUS) NUMBER(3) PERIOD(DAY)
    """
    def __init__(self, expr):
        self.expr = expr
        self.expr_l = len(expr)
        self.next_i = 0

    def next_char(self):
        if self.next_i >= self.expr_l:
            return None

        c = self.expr[self.next_i]
        self.next_i = self.next_i + 1

        if c.isspace():
            c = self.next_char()

        return c

    def next_token(self):
        """Get the next token in the expression"""

        col = self.next_i+1

        c = self.next_char()
        if c is None: return None

        if c.isdigit():
            val = c
            c = self.next_char()
            while c != None and c.isdigit():
                val = val + c
                c = self.next_char()

            if c != None:
                # un-pop the next char
                self.next_i = self.next_i - 1

            return Token(TokenType.NUMBER, int(val), col)


        if c == 'h': return Token(TokenType.PERIOD, Period.HOUR, col)
        if c == 'd': return Token(TokenType.PERIOD, Period.DAY, col)
        if c == 'w': return Token(TokenType.PERIOD, Period.WEEK, col)
        if c == 'm': return Token(TokenType.PERIOD, Period.MONTH, col)
        if c == 'y': return Token(TokenType.PERIOD, Period.YEAR, col)

        if c == '+': return Token(TokenType.OPERATOR, Operator.PLUS, col)
        if c == '-': return Token(TokenType.OPERATOR, Operator.MINUS, col)

        raise InvalidCharError(c)


class EstimateExpression:
    """Evaluator for time estimate expressions, such as 5w + 7d (which would result in 1m 2w 2d)"""

    def __init__(self, expr):
        self.expr = expr
        self.value = 0 # in hours
        self._eval()

    def _eval(self):
        cur_num = 0
        cur_op = Operator.PLUS
        tokenizer = Tokenizer(self.expr)

        t = tokenizer.next_token()
        expect = (TokenType.NUMBER,)

        while t != None:
            if t.token_type not in expect:
                raise UnexpectedTokenError(t, expect)

            if t.token_type == TokenType.NUMBER:
                cur_num = t.value
                expect = (TokenType.PERIOD,)

            elif t.token_type == TokenType.PERIOD:
                if cur_op == Operator.PLUS:
                    self.value = self.value + in_hours(cur_num, t.value)
                else:
                    self.value = self.value - in_hours(cur_num, t.value)

                cur_op = Operator.PLUS
                expect = (TokenType.OPERATOR, TokenType.NUMBER)

            elif t.token_type == TokenType.OPERATOR:
                cur_op = t.value
                expect = (TokenType.NUMBER,)

            t = tokenizer.next_token()


    def __str__(self):
        if self.value == 0: return "0h"
        return hours_to_string(self.value)


class CmdEstimateExpression(Cmd):
    prompt = "> "

    def do_help(self, line):
        print EstimateExpression.__doc__

    def quit(self, line):
        print 'Bye'
        sys.exit(0)

    do_exit = quit
    do_quit = quit

    def do_EOF(self, line):
        print
        self.quit(line)

    def emptyline(self): pass

    def default(self, line):
        try:
            print EstimateExpression(line.strip())
        except InvalidCharError as e:
            print e.value
        except UnexpectedTokenError as e:
            print e.value


if __name__ == '__main__':
    CmdEstimateExpression().cmdloop()
