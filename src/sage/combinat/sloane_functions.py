r"""
Functions that compute some of the sequences in Sloane's tables

EXAMPLES:
   Type sloane.[tab] to see a list of the sequences that are defined.
   sage: d = sloane.A000005; d
    The integer sequence tau(n), which is the number of divisors of n.
    sage: d(1)
    1
    sage: d(6)
    4
    sage: d(100)
    9

Type \code{d._eval??} to see how the function that computes an individual
term of the sequence is implemented.

The input must be a positive integer:
    sage: d(0)
    Traceback (most recent call last):
    ...
    ValueError: input n (=0) must be a positive integer
    sage: d(1/3)
    Traceback (most recent call last):
    ...
    TypeError: no coercion of this rational to integer

You can also change how a sequence prints:
    sage: d = sloane.A000005; d
    The integer sequence tau(n), which is the number of divisors of n.
    sage: d.rename('(..., tau(n), ...)')
    sage: d
    (..., tau(n), ...)
    sage: d.reset_name()
    sage: d
    The integer sequence tau(n), which is the number of divisors of n.

AUTHORS:
    -- William Stein: framework
    -- Jaap Spies: most sequences
    -- Nick Alexander: updated framework
"""

########################################################################
#
# To add your own new sequence here, do the following:
#
# 1. Add a new class to Section II below, which you should
#    do by copying an existing class and modifying it.
#    Make sure to at least define _eval and _repr_.
#    NOTES:  (a) define the _eval method only, which you may
#                assume has as input a *positive* SAGE integer (offset > 0).
#                Each sequence in the OEIS has an offset >= 0, indicating the
#                value of the first index. The default offset = 1.
#            (b) define the list method if there is a faster
#                way to compute the terms of the sequence than
#                just calling _eval (which is the default definition
#                of list, note: the offset is counted for, it lists n numbers).
#            (c) *AVOID* using gp.method if possible!  Use pari(obj).method()
#            (d) In many cases the function that computes a given integer
#                sequence belongs elsewhere in SAGE.  Put it there and make
#                your class in this file just call it.
#            (e) _eval should always return a SAGE integer.
#
# 2. Add an instance of your class in Section III below.

#
# 3. Type "sage -br" to rebuild SAGE, then fire up the notebook and
#    try out your new sequence.  Click the text button to get a version
#    of your session that you then include as a docstring.
#    You can check your results with the entries of the OEIS:
#       sage: seq = sloane_sequence(45)
#       Searching Sloane's online database...
#       sage: print seq[1]
#       Fibonacci numbers: F(n) = F(n-1) + F(n-2), F(0) = 0, F(1) = 1, F(2) = 1, ...
#       sage: seq[2][:12]
#       [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
#
# 4. Send a patch using
#      sage: hg_sage.ci()
#      sage: hg_sage.send('patchname')
#    (Email it to sage-dev@groups.google.com or post it online.)
#
########################################################################

########################################################################
# I. Define the generic Sloane sequence class.
########################################################################

# just used for handy .load, .save, etc.

import inspect
from sage.structure.sage_object import SageObject
from sage.misc.misc import srange
from sage.rings.integer_ring import ZZ
Integer = ZZ

class SloaneSequence(SageObject):
    r"""Base class for a Slone integer sequence.

    EXAMPLES:
    We create a dummy sequence:

    """
    def __init__(self, offset=1):
        r"""
        A sequence starting at offset (=1 by default).
        """
        self.offset = ZZ(offset)

    def _repr_(self):
        raise NotImplementedError

    def __call__(self, n):
        m = ZZ(n)
        if m < self.offset:
            if self.offset == 1:
                raise ValueError, "input n (=%s) must be a positive integer" % (n)
            else:
                raise ValueError, "input n (=%s) must be an integer >= %s" % (n, self.offset)
        return self._eval(m)

    def _eval(self, n):
        # this is what you implement in the derived class
        # the input n is assumed to be a *SAGE* integer >= offset
        raise NotImplementedError

    def list(self, n):
        r"""Return n terms of the sequence: sequence[offset], sequence[offset+1], ... , sequence[offset+n-1].
        """
        return [self._eval(i) for i in srange(self.offset, n+self.offset)]

    # The Python default tries repeated __getitem__ calls, which will succeed,
    # but is probably not what is wanted.
    # This prevents list(sequence) from wandering off.
    def __iter__(self):
        raise NotImplementedError

    def __getitem__(self, n):
        r"""Return sequence[n].

        We interpret slices as best we can, but our sequences
        are infinite so we want to prevent some mis-incantations.

        Therefore, we abitrarily cap slices to be at most
        LENGTH=100000 elements long.  Since many Sloane sequences
        are costly to compute, this is probably not an unreasonable
        decision, but just in case, list does not cap length.
        """
        if not isinstance(n, slice):
            return self(n)

        LENGTH = 100000
        (start, stop, step) = n.indices(2*LENGTH)
        if abs(stop - start) > LENGTH:
            raise IndexError, "slice (=%s) too long"%n
        # The dirty work of generating indices is left to a range list
        # This could be slow but in practice seems fine
        # NOTE: n is a SLICE, not an index
        return [ self(i) for i in range(0, LENGTH)[n] if i >= self.offset ]

########################################################################
# II. Actual implementations of Sloane sequences.
########################################################################

# You may have to import more here when defining new sequences
import sage.rings.arith as arith
from sage.rings.integer_ring import ZZ
from sage.matrix.matrix_space import MatrixSpace
from sage.rings.rational_field import QQ
from sage.libs.pari.gen import pari
from sage.combinat import combinat
from sage.misc.misc import prod

class A000027(SloaneSequence):
    r"""
    The natural numbers. Also called the whole numbers, the counting
    numbers or the positive integers.

    The following examples are tests of SloaneSequence more than A000027.

    EXAMPLES:
    sage: s = sloane.A000027; s
    The natural numbers.
    sage: s(10)
    10

    Index n is interpreted as _eval(n):
    sage: s[10]
    10

    Slices are interpreted with absolute offsets, so the following returns the terms of the sequence up to but not including the third term:
    sage: s[:3]
    [1, 2]
    sage: s[3:6]
    [3, 4, 5]
    sage: s.list(5)
    [1, 2, 3, 4, 5]
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=1)

# is this a good idea to have a link for all sequences? Jaap
    link = "http://www.research.att.com/~njas/sequences/A000027"

    def _repr_(self):
        return "The natural numbers."

    def _eval(self, n):
        return n

class A000004(SloaneSequence):
    r"""
    The zero sequence.

    INPUT:
        n -- non negative integer

    OUTPUT:

    EXAMPLES:
        sage: a = sloane.A000004; a
        The zero sequence.
        sage: a(1)
        0
        sage: a(2007)
        0
        sage: a.list(12)
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)

    def _repr_(self):
        return "The zero sequence."

    def _eval(self, n):
        return 0


class A000005(SloaneSequence):
    r"""
    The sequence $tau(n)$, which is the number of divisors of $n$.

    This sequence is also denoted $d(n)$ (also called $\tau(n)$ or
    $\sigma_0(n)$), the number of divisors of n.

    INPUT:
        n -- positive integer

    OUTPUT:

    EXAMPLES:
        sage: d = sloane.A000005; d
        The integer sequence tau(n), which is the number of divisors of n.
        sage: d(1)
        1
        sage: d(6)
        4
        sage: d(51)
        4
        sage: d(100)
        9
        sage: d(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be a positive integer
        sage: d.list(10)
        [1, 2, 2, 3, 2, 4, 2, 4, 3, 4]

    AUTHOR:
        -- Jaap Spies (2006-12-10)
        -- William Stein (2007-01-08)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=1)

    def _repr_(self):
        return "The integer sequence tau(n), which is the number of divisors of n."

    def _eval(self, n):
        return arith.number_of_divisors(n)

class A000010(SloaneSequence):
    r"""
    The integer sequence A000010 is Euler's totient function.

    Number of positive integers $i < n$ that are relative prime to $n$.
    Number of totatives of $n$.

    Euler totient function $\phi(n)$: count numbers < $n$ and prime to $n$.
    euler_phi is a standard SAGE function implemented in PARI


    INPUT:
        n -- positive integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000010; a
        Euler's totient function
        sage: a(1)
        1
        sage: a(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be a positive integer
        sage: a(11)
        10
        sage: a.list(12)
        [1, 1, 2, 2, 4, 2, 6, 4, 6, 4, 10, 4]
        sage: a(1/3)
        Traceback (most recent call last):
        ...
        TypeError: no coercion of this rational to integer


    AUTHOR:
        -- Jaap Spies (2007-01-12)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=1)

    def _repr_(self):
        return "Euler's totient function"

    def _eval(self, n):
        return arith.euler_phi(n)

# Theme: elementary functions

class A000007(SloaneSequence):
    r"""
    The characteristic function of 0: $a(n) = 0^n$.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000007;a
        The characteristic function of 0: a(n) = 0^n.
        sage: a(0)
        1
        sage: a(2)
        0
        sage: a(12)
        0
        sage: a.list(12)
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    AUTHOR:
        -- Jaap Spies (2007-01-12)

    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)

    def _repr_(self):
        return "The characteristic function of 0: a(n) = 0^n."

    def _eval(self, n):
        return Integer(0**n)

class A000169(SloaneSequence):
    r"""
    Number of labeled rooted trees with $n$ nodes: $n^{(n-1)}$.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000169;a
        Number of labeled rooted trees with n nodes: n^(n-1).
        sage: a(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be a positive integer
        sage: a(1)
        1
        sage: a(2)
        2
        sage: a(10)
        1000000000
        sage: a.list(11)
        [1, 2, 9, 64, 625, 7776, 117649, 2097152, 43046721, 1000000000, 25937424601]

    AUTHOR:
        -- Jaap Spies (2007-01-26)

    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=1)

    def _repr_(self):
        return "Number of labeled rooted trees with n nodes: n^(n-1)."

    def _eval(self, n):
        return Integer(n**(n-1))

class A000272(SloaneSequence):
    r"""
    Number of labeled rooted trees on $n$ nodes: $n^{(n-2)}$.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000272;a
        Number of labeled rooted trees with n nodes: n^(n-2).
        sage: a(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be a positive integer
        sage: a(1)
        1
        sage: a(2)
        1
        sage: a(10)
        100000000
        sage: a.list(11)
        [1, 1, 3, 16, 125, 1296, 16807, 262144, 4782969, 100000000, 2357947691]

    AUTHOR:
        -- Jaap Spies (2007-01-26)

    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=1)

    def _repr_(self):
        return "Number of labeled rooted trees with n nodes: n^(n-2)."

    def _eval(self, n):
        return Integer(n**(n-2))





class A000312(SloaneSequence):
    r"""
     Number of labeled mappings from $n$ points to themselves (endofunctions): $n^n$.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000312;a
        Number of labeled mappings from n points to themselves (endofunctions): n^n.
        sage: a(-1)
        Traceback (most recent call last):
        ...
        ValueError: input n (=-1) must be an integer >= 0
        sage: a(0)
        1
        sage: a(1)
        1
        sage: a(9)
        387420489
        sage: a.list(11)
        [1, 1, 4, 27, 256, 3125, 46656, 823543, 16777216, 387420489, 10000000000]

    AUTHOR:
        -- Jaap Spies (2007-01-26)

    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)

    def _repr_(self):
        return "Number of labeled mappings from n points to themselves (endofunctions): n^n."

    def _eval(self, n):
        return Integer(n**n)




class A001477(SloaneSequence):
    r"""
    The nonnegative integers.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A001477;a
        The nonnegative integers.
        sage: a(-1)
        Traceback (most recent call last):
        ...
        ValueError: input n (=-1) must be an integer >= 0
        sage: a(0)
        0
        sage: a(3382789)
        3382789
        sage: a(11)
        11
        sage: a.list(12)
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

    AUTHOR:
        -- Jaap Spies (2007-01-26)

    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)

    def _repr_(self):
        return "The nonnegative integers."

    def _eval(self, n):
        return Integer(n)

class A004526(SloaneSequence):
    r"""
    The nonnegative integers repeated`

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A004526;a
        The nonnegative integers repeated.
        sage: a(0)
        0
        sage: a(1)
        0
        sage: a(2)
        1
        sage: a(10)
        5
        sage: a.list(12)
        [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5]

    AUTHOR:
        -- Jaap Spies (2007-01-26)

    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)

    def _repr_(self):
        return "The nonnegative integers repeated."

    def _eval(self, n):
        return Integer(n//2)


class A000326(SloaneSequence):
    r"""
    Pentagonal numbers: $n(3n-1)/2$.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000326;a
        Pentagonal numbers: n(3n-1)/2.
        sage: a(0)
        0
        sage: a(1)
        1
        sage: a(2)
        5
        sage: a(10)
        145
        sage: a.list(12)
        [0, 1, 5, 12, 22, 35, 51, 70, 92, 117, 145, 176]
        sage: a(1/3)
        Traceback (most recent call last):
        ...
        TypeError: no coercion of this rational to integer

    AUTHOR:
        -- Jaap Spies (2007-01-26)

    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)

    def _repr_(self):
        return "Pentagonal numbers: n(3n-1)/2."

    def _eval(self, n):
        return Integer(n*(3*n-1)//2)





class A002378(SloaneSequence):
    r"""
    Oblong (or pronic, or heteromecic) numbers: $n(n+1)$.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A002378;a
        Oblong (or pronic, or heteromecic) numbers: n(n+1).
        sage: a(-1)
        Traceback (most recent call last):
        ...
        ValueError: input n (=-1) must be an integer >= 0
        sage: a(0)
        0
        sage: a(1)
        2
        sage: a(11)
        132
        sage: a.list(12)
        [0, 2, 6, 12, 20, 30, 42, 56, 72, 90, 110, 132]

    AUTHOR:
        -- Jaap Spies (2007-01-26)

    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)

    def _repr_(self):
        return "Oblong (or pronic, or heteromecic) numbers: n(n+1)."

    def _eval(self, n):
        return Integer(n*(n+1))

class A002620(SloaneSequence):
    r"""
    Quarter-squares: floor(n/2)*ceiling(n/2). Equivalently, $\lfloor n^2/4 \rfloor$.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A002620;a
        Quarter-squares: floor(n/2)*ceiling(n/2). Equivalently, floor(n^2/4).
        sage: a(0)
        0
        sage: a(1)
        0
        sage: a(2)
        1
        sage: a(10)
        25
        sage: a.list(12)
        [0, 0, 1, 2, 4, 6, 9, 12, 16, 20, 25, 30]

    AUTHOR:
        -- Jaap Spies (2007-01-26)

    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)

    def _repr_(self):
        return "Quarter-squares: floor(n/2)*ceiling(n/2). Equivalently, floor(n^2/4)."

    def _eval(self, n):
        return Integer(n**2 // 4)





class A005408(SloaneSequence):
    r"""
    The odd numbers a(n) = 2n + 1.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A005408;a
        The odd numbers a(n) = 2n + 1.
        sage: a(-1)
        Traceback (most recent call last):
        ...
        ValueError: input n (=-1) must be an integer >= 0
        sage: a(0)
        1
        sage: a(4)
        9
        sage: a(11)
        23
        sage: a.list(12)
        [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23]

    AUTHOR:
        -- Jaap Spies (2007-01-26)

    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)

    def _repr_(self):
        return "The odd numbers a(n) = 2n + 1."

    def _eval(self, n):
        return Integer(2*n+1)



class A000012(SloaneSequence):
    r"""
    The all 1's sequence.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000012; a
        The all 1's sequence.
        sage: a(1)
        1
        sage: a(2007)
        1
        sage: a.list(12)
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

    AUTHOR:
        -- Jaap Spies (2007-01-12)

    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)

    def _repr_(self):
        return "The all 1's sequence."

    def _eval(self, n):
        return 1

class A000120(SloaneSequence):
    r"""
    1's-counting sequence: number of 1's in binary expansion of $n$.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000120;a
        1's-counting sequence: number of 1's in binary expansion of n.
        sage: a(0)
        0
        sage: a(2)
        1
        sage: a(12)
        2
        sage: a.list(12)
        [0, 1, 1, 2, 1, 2, 2, 3, 1, 2, 2, 3]

    AUTHOR:
        -- Jaap Spies (2007-01-26)

    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)

    def _repr_(self):
        return "1's-counting sequence: number of 1's in binary expansion of n."

    def f(self,n):
        if n <= 1:
            return Integer(n)
        return self.f(n//2) + n%2

    def _eval(self, n):
        return self.f(n)



class A000290(SloaneSequence):
    r"""
    The squares: $a(n) = n^2$.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000290;a
        The squares: a(n) = n^2.
        sage: a(0)
        0
        sage: a(-1)
        Traceback (most recent call last):
        ...
        ValueError: input n (=-1) must be an integer >= 0
        sage: a(16)
        256
        sage: a.list(17)
        [0, 1, 4, 9, 16, 25, 36, 49, 64, 81, 100, 121, 144, 169, 196, 225, 256]

    AUTHOR:
        -- Jaap Spies (2007-01-25)

    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)

    def _repr_(self):
        return "The squares: a(n) = n^2."

    def _eval(self, n):
        return Integer(n**2)




class A000225(SloaneSequence):
    r"""
    $2^n - 1$.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000225;a
        2^n - 1.
        sage: a(0)
        0
        sage: a(-1)
        Traceback (most recent call last):
        ...
        ValueError: input n (=-1) must be an integer >= 0
        sage: a(12)
        4095
        sage: a.list(12)
        [0, 1, 3, 7, 15, 31, 63, 127, 255, 511, 1023, 2047]

    AUTHOR:
        -- Jaap Spies (2007-01-25)

    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)

    def _repr_(self):
        return "2^n - 1."

    def _eval(self, n):
        return Integer(2**n - 1)


class A000015(SloaneSequence):
    r"""
    Smallest prime power $\geq n$.

    INPUT:
        n -- positive integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000015; a
        Smallest prime power >= n.
        sage: a(1)
        1
        sage: a(8)
        8
        sage: a(305)
        307
        sage: a(-4)
        Traceback (most recent call last):
        ...
        ValueError: input n (=-4) must be a positive integer
        sage: a.list(12)
        [1, 2, 3, 4, 5, 7, 7, 8, 9, 11, 11, 13]
        sage: a(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be a positive integer

    AUTHOR:
        -- Jaap Spies (2007-01-18)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=1)

    def _repr_(self):
        return " Smallest prime power >= n."

    def _eval(self, n):
        if arith.is_prime_power(n):
            return n
        else:
            return arith.next_prime_power(n)

class A000016(SloaneSequence):
    r"""
    Sloane's A000016

    INPUT:
        n -- positive integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000016; a
        Sloane's A000016.
        sage: a(1)
        1
        sage: a(0)
        1
        sage: a(8)
        16
        sage: a(75)
        251859545753048193000
        sage: a(-4)
        Traceback (most recent call last):
        ...
        ValueError: input n (=-4) must be an integer >= 0
        sage: a.list(12)
        [1, 1, 1, 2, 2, 4, 6, 10, 16, 30, 52, 94]

    AUTHOR:
        -- Jaap Spies (2007-01-18)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)

    def _repr_(self):
        return "Sloane's A000016."

    def _eval(self, n):
        if n == 0:
            return 1
        return sum( (i%2)*arith.euler_phi(i)*2**(Integer(n/i))/(2*n) for i in arith.divisors(n) )

class A000030(SloaneSequence):
    r"""
    Initial digit of $n$.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000030; a
        Initial digit of n
        sage: a(0)
        0
        sage: a(1)
        1
        sage: a(8)
        8
        sage: a(454)
        4
        sage: a(-4)
        Traceback (most recent call last):
        ...
        ValueError: input n (=-4) must be an integer >= 0
        sage: a.list(12)
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 1, 1]

    AUTHOR:
        -- Jaap Spies (2007-01-18)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)

    def _repr_(self):
        return "Initial digit of n"

    def _eval(self, n):
        if n < 10:
            return n
        else:
            return self(n//10)

class A000032(SloaneSequence):
    r"""
    Lucas numbers (beginning at 2): $L(n) = L(n-1) + L(n-2)$.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000032; a
        Lucas numbers (beginning at 2): L(n) = L(n-1) + L(n-2).
        sage: a(0)
        2
        sage: a(1)
        1
        sage: a(8)
        47
        sage: a(200)
        627376215338105766356982006981782561278127
        sage: a(-4)
        Traceback (most recent call last):
        ...
        ValueError: input n (=-4) must be an integer >= 0
        sage: a.list(12)
        [2, 1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199]

    AUTHOR:
        -- Jaap Spies (2007-01-18)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)

    def _repr_(self):
        return "Lucas numbers (beginning at 2): L(n) = L(n-1) + L(n-2)."

    def _eval(self, n):
        if n == 0:
            return 2
        elif n == 1:
            return 1
        else:
            return sloane.A000045(n+1) + sloane.A000045(n-1)

# Theme: prime numbers
class A000040(SloaneSequence):
    r"""
    The prime numbers.

    INPUT:
        n -- positive integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000040; a
        The prime numbers.
        sage: a(1)
        2
        sage: a(8)
        19
        sage: a(305)
        2011
        sage: a.list(12)
        [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
        sage: a(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be a positive integer

    AUTHOR:
        -- Jaap Spies (2007-01-17)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=1)

    def _repr_(self):
        return "The prime numbers."

    def _precompute(self, so_far=1000):
        try:
            self._b
            n = self._n
        except AttributeError:
            self._b = []
            n = self.offset
            self._n = n
        self._b += arith.prime_range(self._n, self._n+so_far)
        self._n += so_far

    def _eval(self, n):
        try:
            return self._b[n-1]
        except (AttributeError, IndexError):
            self._precompute()
            # try again
            return self._eval(n)

    def list(self, n):
        try:
            if len(self._b) < n:
                raise IndexError
            else:
                return self._b[:n]
        except (AttributeError, IndexError):
            self._precompute()
            # try again
            return self.list(n)

class A002808(SloaneSequence):
    r"""
    The composite numbers: numbers $n$ of the form $xy$ for $x > 1$ and $y > 1$.

    INPUT:
        n -- positive integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A002808;a
        The composite numbers: numbers n of the form x*y for x > 1 and y > 1.
        sage: a(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be a positive integer
        sage: a(2)
        6
        sage: a(11)
        20
        sage: a.list(12)
        [4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21]

    AUTHOR:
        -- Jaap Spies (2007-01-26)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=1)
        self._b = [4]
        self._n = 5

    def _repr_(self):
        return "The composite numbers: numbers n of the form x*y for x > 1 and y > 1."

    def _precompute(self, how_many=150):
        self._b += [i for i in range(self._n, self._n+how_many) if not arith.is_prime(i)]
        self._n += how_many

    def _eval(self, n):
        try:
            return self._b[n-1]
        except (AttributeError, IndexError):
            self._precompute()
            # try again
            return self._eval(n)

    def list(self, n):
        try:
            if len(self._b) <= n:
                raise IndexError
            else:
                return self._b[:n]
        except (AttributeError, IndexError):
            self._precompute()
            # try again
            return self.list(n)

class A000043(SloaneSequence):
    r"""
    Primes $p$ such that $2^p - 1$ is prime. $2^p - 1$ is then called a Mersenne prime.

    INPUT:
        n -- positive integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000043;a
        Primes p such that 2^p - 1 is prime. 2^p - 1 is then called a Mersenne prime.
        sage: a(1)
        2
        sage: a(2)
        3
        sage: a(39)
        13466917
        sage: a(40)
        Traceback (most recent call last):
        ...
        IndexError: list index out of range
        sage: a.list(12)
        [2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127]

    AUTHOR:
        -- Jaap Spies (2007-01-26)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=1)

    def _repr_(self):
        return "Primes p such that 2^p - 1 is prime. 2^p - 1 is then called a Mersenne prime."

    def _eval(self, n):
        try:
            return Integer(self._b[n-1])
        except (AttributeError, IndexError):
            self._b = [2,3,5,7,13,17,19,31,61,89,107,127,521,607,1279,2203,2281,3217,4253,4423,9689,9941,11213,19937,21701,23209,44497,86243,110503,132049,216091,756839,859433,1257787,1398269,2976221,3021377,6972593,13466917]
            return Integer(self._b[n-1])

class A000668(SloaneSequence):
    r"""
    Mersenne primes (of form $2^p - 1$ where $p$ is a prime).

    (See A000043 for the values of $p$.)

    Warning: a(39) has 4,053,946 digits!

    INPUT:
        n -- positive integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000668;a
        Mersenne primes (of form 2^p - 1 where p is a prime). (See A000043 for the values of p.)
        sage: a(1)
        3
        sage: a(2)
        7
        sage: a(12)
        170141183460469231731687303715884105727

        Warning: a(39) has 4,053,946 digits!

        sage: a(40)
        Traceback (most recent call last):
        ...
        IndexError: list index out of range
        sage: a.list(8)
        [3, 7, 31, 127, 8191, 131071, 524287, 2147483647]

    AUTHOR:
        -- Jaap Spies (2007-01-25)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=1)

    def _repr_(self):
        return "Mersenne primes (of form 2^p - 1 where p is a prime). (See A000043 for the values of p.)"

    def _eval(self, n):
        return Integer(2**sloane.A000043(n) - 1)

class A000396(SloaneSequence):
    r"""
    Perfect numbers: equal to sum of proper divisors.

    INPUT:
        n -- positive integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000396;a
        Perfect numbers: equal to sum of proper divisors.
        sage: a(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be a positive integer
        sage: a(1)
        6
        sage: a(2)
        28
        sage: a(7)
        137438691328
        sage: a.list(7)
        [6, 28, 496, 8128, 33550336, 8589869056, 137438691328]

    AUTHOR:
        -- Jaap Spies (2007-01-25)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=1)

    def _repr_(self):
        return "Perfect numbers: equal to sum of proper divisors."

    def _eval(self, n):
        p = sloane.A000043(n)
        return Integer(2**(p-1) * (2**p - 1))

class A005100(SloaneSequence):
    r"""
    Deficient numbers: $\sigma(n) < 2n$.

    INPUT:
        n -- positive integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A005100;a
        Deficient numbers: sigma(n) < 2n
        sage: a(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be a positive integer
        sage: a(1)
        1
        sage: a(2)
        2
        sage: a(12)
        14
        sage: a.list(12)
        [1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 13, 14]

    AUTHOR:
        -- Jaap Spies (2007-01-26)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=1)
        self._b = [1]
        self._n = 2

    def _repr_(self):
        return "Deficient numbers: sigma(n) < 2n"

    def _precompute(self, how_many=150):
        self._b += [i for i in range(self._n, self._n+how_many) if arith.sigma(i) < 2*i]
        self._n += how_many

    def _eval(self, n):
        try:
            return self._b[n-1]
        except (AttributeError, IndexError):
            self._precompute()
            # try again
            return self._eval(n)

    def list(self, n):
        try:
            if len(self._b) <= n:
                raise IndexError
            else:
                return self._b[:n]
        except (AttributeError, IndexError):
            self._precompute()
            # try again
            return self.list(n)

class A005101(SloaneSequence):
    r"""
    Abundant numbers (sum of divisors of $n$ exceeds $2n$).

    INPUT:
        n -- positive integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A005101;a
        Abundant numbers (sum of divisors of n exceeds 2n).
        sage: a(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be a positive integer
        sage: a(1)
        12
        sage: a(2)
        18
        sage: a(12)
        60
        sage: a.list(12)
        [12, 18, 20, 24, 30, 36, 40, 42, 48, 54, 56, 60]

    AUTHOR:
        -- Jaap Spies (2007-01-26)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=1)
        self._b = [12]
        self._n = 18

    def _repr_(self):
        return "Abundant numbers (sum of divisors of n exceeds 2n)."

    def _precompute(self, how_many=150):
        self._b += [i for i in range(self._n, self._n+how_many) if arith.sigma(i) > 2*i]
        self._n += how_many

    def _eval(self, n):
        try:
            return self._b[n-1]
        except (AttributeError, IndexError):
            self._precompute()
            # try again
            return self._eval(n)

    def list(self, n):
        try:
            if len(self._b) <= n:
                raise IndexError
            else:
                return self._b[:n]
        except (AttributeError, IndexError):
            self._precompute()
            # try again
            return self.list(n)



class A002110(SloaneSequence):
    r"""
    Primorial numbers (first definition): product of first $n$ primes. Sometimes written $p\#$.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A002110;a
        Primorial numbers (first definition): product of first n primes. Sometimes written p#.
        sage: a(0)
        1
        sage: a(2)
        6
        sage: a(8)
        9699690
        sage: a(17)
        1922760350154212639070
        sage: a.list(9)
        [1, 2, 6, 30, 210, 2310, 30030, 510510, 9699690]

    AUTHOR:
        -- Jaap Spies (2007-01-25)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)

    def _repr_(self):
        return "Primorial numbers (first definition): product of first n primes. Sometimes written p#."

    def _eval(self, n):
        return prod([sloane.A000040(i) for i in range(1,n+1)]) #n-th prime = A000040(n)

class A000720(SloaneSequence):
    r"""
    $pi(n)$, the number of primes $\le n$. Sometimes called $PrimePi(n)$.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000720;a
        pi(n), the number of primes <= n. Sometimes called PrimePi(n)
        sage: a(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be a positive integer
        sage: a(2)
        1
        sage: a(8)
        4
        sage: a(1000)
        168
        sage: a.list(12)
        [0, 1, 2, 2, 3, 3, 4, 4, 4, 4, 5, 5]

    AUTHOR:
        -- Jaap Spies (2007-01-25)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=1)

    def _repr_(self):
        return "pi(n), the number of primes <= n. Sometimes called PrimePi(n)"

    def _eval(self, n):
        return arith.prime_pi(n)

class A006530(SloaneSequence):
    r"""
    Largest prime dividing $n$ (with $a(1)=1$).

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A006530;a
        Largest prime dividing n (with a(1)=1).
        sage: a(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be a positive integer
        sage: a(1)
        1
        sage: a(2)
        2
        sage: a(8)
        2
        sage: a(11)
        11
        sage: a.list(15)
        [1, 2, 3, 2, 5, 3, 7, 2, 3, 5, 11, 3, 13, 7, 5]

    AUTHOR:
        -- Jaap Spies (2007-01-25)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=1)

    def _repr_(self):
        return "Largest prime dividing n (with a(1)=1)."

    def _eval(self, n):
        if n == 1:
            return Integer(1)
        return max(p for p,_ in arith.factor(n))

class A000961(SloaneSequence):
    r"""
    Prime powers

    INPUT:
        n -- positive integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000961;a
        Prime powers.
        sage: a(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be a positive integer
        sage: a(2)
        2
        sage: a(12)
        17
        sage: a.list(12)
        [1, 2, 3, 4, 5, 7, 8, 9, 11, 13, 16, 17]

    AUTHOR:
        -- Jaap Spies (2007-01-25)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=1)
        self._b = [1]
        self._n = 2

    def _repr_(self):
        return "Prime powers."

    def _precompute(self, how_many=150):
        self._b += [i for i in range(self._n, self._n+how_many) if len([p for p,_ in arith.factor(i)]) == 1]
        self._n += how_many

    def _eval(self, n):
        try:
            return self._b[n-1]
        except (AttributeError, IndexError):
            self._precompute()
            # try again
            return self._eval(n)

    def list(self, n):
        try:
            if len(self._b) <= n:
                raise IndexError
            else:
                return self._b[:n]
        except (AttributeError, IndexError):
            self._precompute()
            # try again
            return self.list(n)



class A005117(SloaneSequence):
    r"""
    Square-free numbers

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A005117;a
        Square-free numbers.
        sage: a(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be a positive integer
        sage: a(2)
        2
        sage: a(12)
        17
        sage: a.list(12)
        [1, 2, 3, 5, 6, 7, 10, 11, 13, 14, 15, 17]

    AUTHOR:
        -- Jaap Spies (2007-01-25)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=1)
        self._b = [1]
        self._n = 2

    def _repr_(self):
        return "Square-free numbers."

    def _precompute(self, how_many=150):
        self._b += [i for i in range(self._n, self._n+how_many) if max(e for _,e in arith.factor(i)) <= 1]
        self._n += how_many

    def _eval(self, n):
        try:
            return self._b[n-1]
        except (AttributeError, IndexError):
            self._precompute()
            # try again
            return self._eval(n)

    def list(self, n):
        try:
            if len(self._b) <= n:
                raise IndexError
            else:
                return self._b[:n]
        except (AttributeError, IndexError):
            self._precompute()
            # try again
            return self.list(n)



# todo
# A020639  	 	 Lpf(n): least prime dividing n (a(1)=1).

class A000041(SloaneSequence):
    r"""
    $a(n)$ = number of partitions of $n$ (the partition numbers).

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000041;a
        a(n) = number of partitions of n (the partition numbers).
        sage: a(0)
        1
        sage: a(2)
        2
        sage: a(8)
        22
        sage: a(200)
        3972999029388
        sage: a.list(9)
        [1, 1, 2, 3, 5, 7, 11, 15, 22]

    AUTHOR:
        -- Jaap Spies (2007-01-18)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)

    def _repr_(self):
        return "a(n) = number of partitions of n (the partition numbers)."

    def _eval(self, n):
        return arith.number_of_partitions(n)




class A000045(SloaneSequence):
    r"""
    Sequence of Fibonacci numbers, offset 0,4.

    REFERENCES: S. Plouffe, Project Gutenberg,
    The First 1001 Fibonacci Numbers,
    \url{http://ibiblio.org/pub/docs/books/gutenberg/etext01/fbncc10.txt}
    We have one more. Our first Fibonacci number is 0.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000045; a
        Fibonacci numbers with index n >= 0
        sage: a(0)
        0
        sage: a(1)
        1
        sage: a.list(12)
        [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
        sage: a(1/3)
        Traceback (most recent call last):
        ...
        TypeError: no coercion of this rational to integer

    AUTHOR:
        -- Jaap Spies (2007-01-13)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)
        self._b = []
        self._precompute()  # force precomputation, e.g. a(0) will fail when asked first

    def _repr_(self):
        return "Fibonacci numbers with index n >= 0"

    def _precompute(self, how_many=500):
        try:
            f = self._f
        except AttributeError:
            self._f = self.fib()
            f = self._f
        self._b += [f.next() for i in range(how_many)]

    def fib(self):
        """
        Returns a generator over all Fibanacci numbers, starting with 0.
        """
        x, y = Integer(0), Integer(1)
        yield x
        while True:
            x, y = y, x+y
            yield x


    def _eval(self, n):
        if len(self._b) < n:
            self._precompute(n - len(self._b) + 1)
        return self._b[n]

    def list(self, n):
        self._eval(n)   # force computation
        return self._b[:n]

class A000108(SloaneSequence):
    r"""
    Catalan numbers: $C_n = \frac{{{2n}\choose{n}}}{n+1} = \frac {(2n)!}{n!(n+1)!}$. Also called Segner numbers.


    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000108;a
        Catalan numbers: C(n) = binomial(2n,n)/(n+1) = (2n)!/(n!(n+1)!). Also called Segner numbers.
        sage: a(0)
        1
        sage: a.offset
        0
        sage: a(8)
        1430
        sage: a(40)
        2622127042276492108820
        sage: a.list(9)
        [1, 1, 2, 5, 14, 42, 132, 429, 1430]

    AUTHOR:
        -- Jaap Spies (2007-01-12)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)

    def _repr_(self):
        return "Catalan numbers: C(n) = binomial(2n,n)/(n+1) = (2n)!/(n!(n+1)!). Also called Segner numbers."

    def _eval(self, n):
        return combinat.catalan_number(n)

class A000079(SloaneSequence):
    r"""
    Powers of 2: $a(n) = 2^n$.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000079;a
        Powers of 2: a(n) = 2^n.
        sage: a(0)
        1
        sage: a(2)
        4
        sage: a(8)
        256
        sage: a(100)
        1267650600228229401496703205376
        sage: a.list(9)
        [1, 2, 4, 8, 16, 32, 64, 128, 256]

    AUTHOR:
        -- Jaap Spies (2007-01-18)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)

    def _repr_(self):
        return "Powers of 2: a(n) = 2^n."

    def _eval(self, n):
        return Integer(2**n)

class A000578(SloaneSequence):
    r"""
    The cubes: $a(n) = n^3$.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000578;a
        The cubes: n^3
        sage: a(-1)
        Traceback (most recent call last):
        ...
        ValueError: input n (=-1) must be an integer >= 0
        sage: a(0)
        0
        sage: a(3)
        27
        sage: a(11)
        1331
        sage: a.list(12)
        [0, 1, 8, 27, 64, 125, 216, 343, 512, 729, 1000, 1331]

    AUTHOR:
        -- Jaap Spies (2007-01-26)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)

    def _repr_(self):
        return "The cubes: n^3"

    def _eval(self, n):
        return Integer(n**3)



class A000244(SloaneSequence):
    r"""
    Powers of 3: $a(n) = 3^n$.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000244;a
        Powers of 3: a(n) = 3^n.
        sage: a(-1)
        Traceback (most recent call last):
        ...
        ValueError: input n (=-1) must be an integer >= 0
        sage: a(0)
        1
        sage: a(3)
        27
        sage: a(11)
        177147
        sage: a.list(12)
        [1, 3, 9, 27, 81, 243, 729, 2187, 6561, 19683, 59049, 177147]

    AUTHOR:
        -- Jaap Spies (2007-01-26)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)

    def _repr_(self):
        return "Powers of 3: a(n) = 3^n."

    def _eval(self, n):
        return Integer(3**n)

class A000302(SloaneSequence):
    r"""
    Powers of 4: $a(n) = 4^n$.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000302;a
        Powers of 4: a(n) = 4^n.
        sage: a(0)
        1
        sage: a(1)
        4
        sage: a(2)
        16
        sage: a(10)
        1048576
        sage: a.list(12)
        [1, 4, 16, 64, 256, 1024, 4096, 16384, 65536, 262144, 1048576, 4194304]

    AUTHOR:
        -- Jaap Spies (2007-01-26)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)

    def _repr_(self):
        return "Powers of 4: a(n) = 4^n."

    def _eval(self, n):
        return Integer(4**n)




class A000142(SloaneSequence):
    r"""
    Factorial numbers: $n! = 1 \cdot 2 \cdot 3 \cdots n$

    Order of symmetric group $S_n$, number of permutations of $n$ letters.


    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000142;a
        Factorial numbers: n! = 1*2*3*4*...*n (order of symmetric group S_n, number of permutations of n letters).
        sage: a(0)
        1
        sage: a(8)
        40320
        sage: a(40)
        815915283247897734345611269596115894272000000000
        sage: a.list(9)
        [1, 1, 2, 6, 24, 120, 720, 5040, 40320]

    AUTHOR:
        -- Jaap Spies (2007-01-12)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)

    def _repr_(self):
        return "Factorial numbers: n! = 1*2*3*4*...*n (order of symmetric group S_n, number of permutations of n letters)."

    def _eval(self, n):
        return arith.factorial(n)

class A000165(SloaneSequence):
    r"""
    Double factorial numbers: $(2n)!! = 2^n*n!$.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000165;a
        Double factorial numbers: (2n)!! = 2^n*n!.
        sage: a(0)
        1
        sage: a.offset
        0
        sage: a(8)
        10321920
        sage: a(20)
        2551082656125828464640000
        sage: a.list(9)
        [1, 2, 8, 48, 384, 3840, 46080, 645120, 10321920]

    AUTHOR:
        -- Jaap Spies (2007-01-24)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)

    def _repr_(self):
        return "Double factorial numbers: (2n)!! = 2^n*n!."

    def _eval(self, n):
        return (2**n)*arith.factorial(n)



class A001147(SloaneSequence):
    r"""
    Double factorial numbers: $(2n-1)!! = 1 \cdot 3 \cdot 5 \cdots (2n-1)$.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A001147;a
        Double factorial numbers: (2n-1)!! = 1.3.5....(2n-1).
        sage: a(0)
        1
        sage: a.offset
        0
        sage: a(8)
        2027025
        sage: a(20)
        319830986772877770815625
        sage: a.list(9)
        [1, 1, 3, 15, 105, 945, 10395, 135135, 2027025]

    AUTHOR:
        -- Jaap Spies (2007-01-24)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)

    def _repr_(self):
        return "Double factorial numbers: (2n-1)!! = 1.3.5....(2n-1)."

    def _eval(self, n):
        return arith.factorial(2*n)/(arith.factorial(n)*2**n)

class A006882(SloaneSequence):
    r"""
    Double factorials $n!!$: $a(n)=n \cdot a(n-2)$.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A006882;a
        Double factorials n!!: a(n)=n*a(n-2).
        sage: a(0)
        1
        sage: a(2)
        2
        sage: a(8)
        384
        sage: a(20)
        3715891200
        sage: a.list(9)
        [1, 1, 2, 3, 8, 15, 48, 105, 384]

    AUTHOR:
        -- Jaap Spies (2007-01-24)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)
        self._b = []
        self._precompute(2)  # force precomputation, e.g. a(0) will fail when asked first

    def _repr_(self):
        return "Double factorials n!!: a(n)=n*a(n-2)."

    def _precompute(self, how_many=10):
        try:
            f = self._f
        except AttributeError:
            self._f = self.df()
            f = self._f
        self._b += [f.next() for i in range(how_many)]

    def df(self):
        """
        Double factorials n!!: a(n)=n*a(n-2).
        """
        x = Integer(1)
        k = 1
        y = x
        yield x
        while True:
            k = k+1
            x, y = y, k*x
            yield x


    def _eval(self, n):
        if len(self._b) <= n:
            self._precompute(n - len(self._b) + 1)
        return self._b[n]

    def list(self, n):
        self._eval(n)   # force computation
        return self._b[:n]

class A000984(SloaneSequence):
    r"""
    Central binomial coefficients: $2n \choose n = \frac {(2n)!} {(n!)^2}$.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000984;a
        Central binomial coefficients: C(2n,n) = (2n)!/(n!)^2
        sage: a(0)
        1
        sage: a(2)
        6
        sage: a(8)
        12870
        sage: a.list(9)
        [1, 2, 6, 20, 70, 252, 924, 3432, 12870]

    AUTHOR:
        -- Jaap Spies (2007-01-26)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)

    def _repr_(self):
        return "Central binomial coefficients: C(2n,n) = (2n)!/(n!)^2"

    def _eval(self, n):
        return arith.binomial(2*n,n)

class A001405(SloaneSequence):
    r"""
    Central binomial coefficients: $n \choose \lfloor \frac {n}{ 2} \rfloor$.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A001405;a
        Central binomial coefficients: C(n,floor(n/2)).
        sage: a(0)
        1
        sage: a(2)
        2
        sage: a(12)
        924
        sage: a.list(12)
        [1, 1, 2, 3, 6, 10, 20, 35, 70, 126, 252, 462]

    AUTHOR:
        -- Jaap Spies (2007-01-26)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)

    def _repr_(self):
        return "Central binomial coefficients: C(n,floor(n/2))."

    def _eval(self, n):
        return arith.binomial(n,arith.floor(n//2))

class A000292(SloaneSequence):
    r"""
    Tetrahedral (or pyramidal) numbers: ${n+2} \choose 3 = n(n+1)(n+2)/6$.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000292;a
        Tetrahedral (or pyramidal) numbers: C(n+2,3) = n(n+1)(n+2)/6.
        sage: a(0)
        0
        sage: a(2)
        4
        sage: a(11)
        286
        sage: a.list(12)
        [0, 1, 4, 10, 20, 35, 56, 84, 120, 165, 220, 286]

    AUTHOR:
        -- Jaap Spies (2007-01-26)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)

    def _repr_(self):
        return "Tetrahedral (or pyramidal) numbers: C(n+2,3) = n(n+1)(n+2)/6."

    def _eval(self, n):
        return Integer(n*(n+1)*(n+2)//6)  # or arith.binomial(n+2,3))

class A000330(SloaneSequence):
    r"""
    Square pyramidal numbers" $0^2 + 1^2 \cdots n^2 = n(n+1)(2n+1)/6$.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000330;a
        Square pyramidal numbers: 0^2+1^2+2^2+...+n^2 = n(n+1)(2n+1)/6.
        sage: a(-1)
        Traceback (most recent call last):
        ...
        ValueError: input n (=-1) must be an integer >= 0
        sage: a(0)
        0
        sage: a(3)
        14
        sage: a(11)
        506
        sage: a.list(12)
        [0, 1, 5, 14, 30, 55, 91, 140, 204, 285, 385, 506]

    AUTHOR:
        -- Jaap Spies (2007-01-26)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)

    def _repr_(self):
        return "Square pyramidal numbers: 0^2+1^2+2^2+...+n^2 = n(n+1)(2n+1)/6."

    def _eval(self, n):
        return Integer(n*(n+1)*(2*n+1)//6)




# Theme:  maximal permanent of an m x n (0,1)- matrix:
# Seok-Zun Song et al.  Extremes of permanents of (0,1)-matrices, p. 201-202.

class A000153(SloaneSequence):
    r"""
    $a(n) = n*a(n-1) + (n-2)*a(n-2)$, with $a(0) = 0$, $a(1) = 1$.

    With offset 1, permanent of (0,1)-matrix of size $n \times (n+d)$ with $d=2$ and $n$ zeros not on a line.
    This is a special case of Theorem 2.3 of Seok-Zun Song et al.
    Extremes of permanents of (0,1)-matrices, p. 201-202.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000153; a
        a(n) = n*a(n-1) + (n-2)*a(n-2), with a(0) = 0, a(1) = 1.
        sage: a(0)
        0
        sage: a(1)
        1
        sage: a(8)
        82508
        sage: a(20)
        10315043624498196944
        sage: a.list(8)
        [0, 1, 2, 7, 32, 181, 1214, 9403]

    AUTHOR:
        -- Jaap Spies (2007-01-13)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)
        self._b = []
        self._precompute(2)  # force precomputation, e.g. a(0) will fail when asked first

    def _repr_(self):
        return "a(n) = n*a(n-1) + (n-2)*a(n-2), with a(0) = 0, a(1) = 1."

    def _precompute(self, how_many=20):
        try:
            f = self._f
        except AttributeError:
            self._f = self.gen(0,1,2)
            f = self._f
        self._b += [f.next() for i in range(how_many)]

    def gen(self,a0,a1,d):
        """

        """
        x, y = ZZ(a0), ZZ(a1)
        k = 1
        yield x
        while True:
            k = k+1
            x, y = y, k*y+(k-d)*x
            yield x


    def _eval(self, n):
        if len(self._b) < n:
            self._precompute(n - len(self._b) + 1)
        return self._b[n]

    def list(self, n):
        self._eval(n)   # force computation
        return self._b[:n]

class A000255(SloaneSequence):
    r"""
    $a(n) = n*a(n-1) + (n-1)*a(n-2)$, with $a(0) = 1$, $a(1) = 1$.

    With offset 1, permanent of (0,1)-matrix of size $n \times (n+d)$ with $d=1$ and $n$ zeros not on a line.
    This is a special case of Theorem 2.3 of Seok-Zun Song et al.
    Extremes of permanents of (0,1)-matrices, p. 201-202.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000255;a
        a(n) = n*a(n-1) + (n-1)*a(n-2), a(0) = 1, a(1) = 1.
        sage: a(0)
        1
        sage: a(1)
        1
        sage: a.offset
        0
        sage: a(8)
        148329
        sage: a(22)
        9923922230666898717143
        sage: a.list(9)
        [1, 1, 3, 11, 53, 309, 2119, 16687, 148329]

    AUTHOR:
        -- Jaap Spies (2007-01-13)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)
        self._b = []
        self._precompute(2)  # force precomputation, e.g. a(0) will fail when asked first

    def _repr_(self):
        return "a(n) = n*a(n-1) + (n-1)*a(n-2), a(0) = 1, a(1) = 1."

    def _precompute(self, how_many=20):
        try:
            f = self._f
        except AttributeError:
            self._f = self.gen(1,1,1)
            f = self._f
        self._b += [f.next() for i in range(how_many)]

    def gen(self,a0,a1,d):
        """

        """
        x, y = ZZ(a0), ZZ(a1)
        k = 1
        yield x
        while True:
            k = k+1
            x, y = y, k*y+(k-d)*x
            yield x


    def _eval(self, n):
        if len(self._b) <= n:
            self._precompute(n - len(self._b) + 1)
        return self._b[n]

    def list(self, n):
        self._eval(n)   # force computation
        return self._b[:n]



class A000261(SloaneSequence):
    r"""
    $a(n) = n*a(n-1) + (n-3)*a(n-2)$, with $a(1) = 1$, $a(2) = 1$.

    With offset 1, permanent of (0,1)-matrix of size $n \times (n+d)$ with $d=3$ and $n$ zeros not on a line.
    This is a special case of Theorem 2.3 of Seok-Zun Song et al.
    Extremes of permanents of (0,1)-matrices, p. 201-202.

    Seok-Zun Song et al., Extremes of permanents of (0,1)-matrices, Lin. Algebra and its Applic. 373 (2003),
    p. 197-210.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000261;a
        a(n) = n*a(n-1) + (n-3)*a(n-2), a(1) = 0, a(2) = 1.
        sage: a(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be a positive integer
        sage: a(1)
        0
        sage: a.offset
        1
        sage: a(8)
        30637
        sage: a(22)
        1801366114380914335441
        sage: a.list(9)
        [0, 1, 3, 13, 71, 465, 3539, 30637, 296967]

    AUTHOR:
        -- Jaap Spies (2007-01-23)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=1)
        self._b = []

    def _repr_(self):
        return "a(n) = n*a(n-1) + (n-3)*a(n-2), a(1) = 0, a(2) = 1."

    def _precompute(self, how_many=20):
        try:
            f = self._f
        except AttributeError:
            self._f = self.gen(0,1,3)
            f = self._f
        self._b += [f.next() for i in range(how_many)]

    def gen(self,a0,a1,d):
        """

        """
        x, y = ZZ(a0), ZZ(a1)
        k = self.offset + 1
        yield x
        while True:
            k = k+1
            x, y = y, k*y+(k-d)*x
            yield x


    def _eval(self, n):
        if len(self._b) < n:
            self._precompute(n - len(self._b) + 1)
        return self._b[n - 1]

    def list(self, n):
        self._eval(n)   # force computation
        return self._b[:n]

class A001909(SloaneSequence):
    r"""
    $a(n) = n*a(n-1) + (n-4)*a(n-2)$, with $a(2) = 0$, $a(3) = 1$.

    With offset 1, permanent of (0,1)-matrix of size $n \times (n+d)$ with $d=4$ and $n$ zeros not on a line.
    This is a special case of Theorem 2.3 of Seok-Zun Song et al.
    Extremes of permanents of (0,1)-matrices, p. 201-202.

    Seok-Zun Song et al., Extremes of permanents of (0,1)-matrices, Lin. Algebra and its Applic. 373 (2003),
    p. 197-210.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A001909;a
        a(n) = n*a(n-1) + (n-4)*a(n-2), a(2) = 0, a(3) = 1.
        sage: a(1)
        Traceback (most recent call last):
        ...
        ValueError: input n (=1) must be an integer >= 2
        sage: a.offset
        2
        sage: a(2)
        0
        sage: a(8)
        8544
        sage: a(22)
        470033715095287415734
        sage: a.list(9)
        [0, 1, 4, 21, 134, 1001, 8544, 81901, 870274]

    AUTHOR:
        -- Jaap Spies (2007-01-13)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=2)
        self._b = []

    def _repr_(self):
        return "a(n) = n*a(n-1) + (n-4)*a(n-2), a(2) = 0, a(3) = 1."

    def _precompute(self, how_many=20):
        try:
            f = self._f
        except AttributeError:
            self._f = self.gen(0,1,4)
            f = self._f
        self._b += [f.next() for i in range(how_many)]

    def gen(self,a0,a1,d):
        """

        """
        x, y = ZZ(a0), ZZ(a1)
        k = self.offset + 1
        yield x
        while True:
            k = k+1
            x, y = y, k*y+(k-d)*x
            yield x


    def _eval(self, n):
        if len(self._b) < n:
            self._precompute(n - len(self._b) + 1)
        return self._b[n-self.offset]

    def list(self, n):
        self._eval(n)   # force computation
        return self._b[:n]

class A001910(SloaneSequence):
    r"""
    $a(n) = n*a(n-1) + (n-5)*a(n-2)$, with $a(3) = 0$, $a(4) = 1$.

    With offset 1, permanent of (0,1)-matrix of size $n \times (n+d)$ with $d=5$ and $n$ zeros not on a line.
    This is a special case of Theorem 2.3 of Seok-Zun Song et al.
    Extremes of permanents of (0,1)-matrices, p. 201-202.

    Seok-Zun Song et al., Extremes of permanents of (0,1)-matrices, Lin. Algebra and its Applic. 373 (2003),
    p. 197-210.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A001910;a
        a(n) = n*a(n-1) + (n-5)*a(n-2), a(3) = 0, a(4) = 1.
        sage: a(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be an integer >= 3
        sage: a(3)
        0
        sage: a.offset
        3
        sage: a(8)
        1909
        sage: a(22)
        98125321641110663023
        sage: a.list(9)
        [0, 1, 5, 31, 227, 1909, 18089, 190435, 2203319]

    AUTHOR:
        -- Jaap Spies (2007-01-13)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=3)
        self._b = []

    def _repr_(self):
        return "a(n) = n*a(n-1) + (n-5)*a(n-2), a(3) = 0, a(4) = 1."

    def _precompute(self, how_many=20):
        try:
            f = self._f
        except AttributeError:
            self._f = self.gen(0,1,5)
            f = self._f
        self._b += [f.next() for i in range(how_many)]

    def gen(self,a0,a1,d):
        """

        """
        x, y = ZZ(a0), ZZ(a1)
        k = self.offset + 1
        yield x
        while True:
            k = k+1
            x, y = y, k*y+(k-d)*x
            yield x


    def _eval(self, n):
        if len(self._b) < n:
            self._precompute(n - len(self._b) + 1)
        return self._b[n-self.offset]

    def list(self, n):
        self._eval(n)   # force computation
        return self._b[:n]

class A090010(SloaneSequence):
    r"""
    Permanent of (0,1)-matrix of size $n \times (n+d)$ with $d=6$ and
    $n$ zeros not on a line.

    $ a(n) = (n+5)*a(n-1) + (n-1)*a(n-2), a(1)=6, a(2)=43$.

    This is a special case of Theorem 2.3 of Seok-Zun Song et al.
    Extremes of permanents of (0,1)-matrices, p. 201-202.

    REFERENCES:
    Seok-Zun Song et al., Extremes of permanents of (0,1)-matrices, Lin. Algebra and its Applic. 373 (2003),
    p. 197-210.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A090010;a
        Permanent of (0,1)-matrix of size n X (n+d) with d=6 and n zeros not on a line.
        sage: a(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be a positive integer
        sage: a(1)
        6
        sage: a(2)
        43
        sage: a.offset
        1
        sage: a(8)
        67741129
        sage: a(22)
        192416593029158989003270143
        sage: a.list(9)
        [6, 43, 356, 3333, 34754, 398959, 4996032, 67741129, 988344062]

    AUTHOR:
        -- Jaap Spies (2007-01-23)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=1)
        self._b = []

    def _repr_(self):
        return "Permanent of (0,1)-matrix of size n X (n+d) with d=6 and n zeros not on a line."

    def _precompute(self, how_many=20):
        try:
            f = self._f
        except AttributeError:
            self._f = self.gen(6,43,6)
            f = self._f
        self._b += [f.next() for i in range(how_many)]

    def gen(self,a0,a1,d):
        """

        """
        x, y = ZZ(a0), ZZ(a1)
        k = self.offset + 1
        yield x
        while True:
            k = k+1
            x, y = y, (k-1)*x+(k+d-1)*y
            yield x


    def _eval(self, n):
        if len(self._b) < n:
            self._precompute(n - len(self._b) + 1)
        return self._b[n-self.offset]

    def list(self, n):
        self._eval(n)   # force computation
        return self._b[:n]

class A055790(SloaneSequence):
    r"""
    $a(n) = n*a(n-1) + (n-2)*a(n-2) [a(0) = 0, a(1) = 2]$.

    With offset 1, permanent of (0,1)-matrix of size n X (n+d) with d=1 and n-1 zeros not on a line.
    This is a special case of Theorem 2.3 of Seok-Zun Song et al.
    Extremes of permanents of (0,1)-matrices, p. 201-202.

    REFERENCES:
    Seok-Zun Song et al., Extremes of permanents of (0,1)-matrices, Lin. Algebra and its Applic. 373 (2003),
    p. 197-210.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A055790;a
        a(n) = n*a(n-1) + (n-2)*a(n-2) [a(0) = 0, a(1) = 2].
        sage: a(0)
        0
        sage: a(1)
        2
        sage: a(2)
        4
        sage: a.offset
        0
        sage: a(8)
        165016
        sage: a(22)
        10356214297533070441564
        sage: a.list(9)
        [0, 2, 4, 14, 64, 362, 2428, 18806, 165016]

    AUTHOR:
        -- Jaap Spies (2007-01-23)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)
        self._b = []
        self._precompute(2)

    def _repr_(self):
        return "a(n) = n*a(n-1) + (n-2)*a(n-2) [a(0) = 0, a(1) = 2]."


    def _precompute(self, how_many=20):
        try:
            f = self._f
        except AttributeError:
            self._f = self.gen(0,2,1)
            f = self._f
        self._b += [f.next() for i in range(how_many)]

    def gen(self,a0,a1,d):
        """

        """
        x, y = ZZ(a0), ZZ(a1)
        k = self.offset + 1
        yield x
        while True:
            k = k+1
            x, y = y, (k-2)*x+(k+d-1)*y
            yield x


    def _eval(self, n):
        if len(self._b) <= n:
            self._precompute(n - len(self._b) + 1)
        return self._b[n-self.offset]

    def list(self, n):
        self._eval(n)   # force computation
        return self._b[:n]

class A090012(SloaneSequence):
    r"""
    Permanent of (0,1)-matrix of size $n \times (n+d)$ with $d=2$ and $n-1$ zeros not on a line.

    $a(n) = (n+1)*a(n-1) + (n-2)*a(n-2)$, $a(1)=3$ and $a(2)=9$


    This is a special case of Theorem 2.3 of Seok-Zun Song et al.
    Extremes of permanents of (0,1)-matrices, p. 201-202.

    REFERENCES:
    Seok-Zun Song et al., Extremes of permanents of (0,1)-matrices, Lin. Algebra and its Applic. 373 (2003),
    p. 197-210.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A090012;a
        Permanent of (0,1)-matrix of size n X (n+d) with d=2 and n-1 zeros not on a line.
        sage: a(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be a positive integer
        sage: a(1)
        3
        sage: a(2)
        9
        sage: a.offset
        1
        sage: a(8)
        890901
        sage: a(22)
        129020386652297208795129
        sage: a.list(9)
        [3, 9, 39, 213, 1395, 10617, 91911, 890901, 9552387]

    AUTHOR:
        -- Jaap Spies (2007-01-23)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=1)

    def _repr_(self):
        return "Permanent of (0,1)-matrix of size n X (n+d) with d=2 and n-1 zeros not on a line."

    def _eval(self, n):
        if n == 1:
            return ZZ(3)
        else:
            return  sloane.A000153(n+1) + sloane.A000153(n)

# Just discovered this relation, so the following code is obsolete!
# Same goes for A090013-A090016
#
#    def _precompute(self, how_many=20):
#        try:
#            f = self._f
#        except AttributeError:
#            self._f = self.gen(3,9,2)
#            f = self._f
#        self._b += [f.next() for i in range(how_many)]
#
#    def gen(self,a0,a1,d):
#        """
#
#        """
#        x, y = ZZ(a0), ZZ(a1)
#        k = self.offset + 1
#        yield x
#        while True:
#            k = k+1
#            x, y = y, (k-2)*x+(k+d-1)*y
#            yield x
#
#
#    def _eval(self, n):
#        if len(self._b) < n:
#            self._precompute(n - len(self._b) + 1)
#        return self._b[n-self.offset]
#
#    def list(self, n):
#        self._eval(n)   # force computation
#        return self._b[:n]

class A090013(SloaneSequence):
    r"""
    Permanent of (0,1)-matrix of size $n \times (n+d)$ with $d=3$ and $n-1$ zeros not on a line.

    $a(n) = (n+1)*a(n-1) + (n-2)*a(n-2) [a(1)=4, a(2)=16]$


    This is a special case of Theorem 2.3 of Seok-Zun Song et al.
    Extremes of permanents of (0,1)-matrices, p. 201-202.

    REFERENCES:
    Seok-Zun Song et al., Extremes of permanents of (0,1)-matrices,
    Lin. Algebra and its Applic. 373 (2003), p. 197-210.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A090013;a
        Permanent of (0,1)-matrix of size n X (n+d) with d=3 and n-1 zeros not on a line.
        sage: a(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be a positive integer
        sage: a(1)
        4
        sage: a(2)
        16
        sage: a.offset
        1
        sage: a(8)
        3481096
        sage: a(22)
        1112998577171142607670336
        sage: a.list(9)
        [4, 16, 84, 536, 4004, 34176, 327604, 3481096, 40585284]

    AUTHOR:
        -- Jaap Spies (2007-01-23)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=1)

    def _repr_(self):
        return "Permanent of (0,1)-matrix of size n X (n+d) with d=3 and n-1 zeros not on a line."

    def _eval(self, n):
        if n == 1:
            return ZZ(4)
        else:
            return  sloane.A000261(n+2) + sloane.A000261(n+1)

class A090014(SloaneSequence):
    r"""
    Permanent of (0,1)-matrix of size $n \times (n+d)$ with $d=4$ and $n-1$ zeros not on a line.

    $a(n) = (n+1)*a(n-1) + (n-2)*a(n-2) [a(1)=5, a(2)=25]$


    This is a special case of Theorem 2.3 of Seok-Zun Song et al.
    Extremes of permanents of (0,1)-matrices, p. 201-202.

    REFERENCES:
    Seok-Zun Song et al., Extremes of permanents of (0,1)-matrices,
    Lin. Algebra and its Applic. 373 (2003), p. 197-210.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A090014;a
        Permanent of (0,1)-matrix of size n X (n+d) with d=4 and n-1 zeros not on a line.
        sage: a(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be a positive integer
        sage: a(1)
        5
        sage: a(2)
        25
        sage: a.offset
        1
        sage: a(8)
        11016595
        sage: a(22)
        7469733600354446865509725
        sage: a.list(9)
        [5, 25, 155, 1135, 9545, 90445, 952175, 11016595, 138864365]

    AUTHOR:
        -- Jaap Spies (2007-01-23)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=1)

    def _repr_(self):
        return "Permanent of (0,1)-matrix of size n X (n+d) with d=4 and n-1 zeros not on a line."

    def _eval(self, n):
        if n == 1:
            return ZZ(5)
        else:
            return  sloane.A001909(n+3) + sloane.A001909(n+2)


class A090015(SloaneSequence):
    r"""
    Permanent of (0,1)-matrix of size $n \times (n+d)$ with $d=5$ and $n-1$ zeros not on a line.

    $a(n) = (n+1)*a(n-1) + (n-2)*a(n-2) [a(1)=6, a(2)=36]$


    This is a special case of Theorem 2.3 of Seok-Zun Song et al.
    Extremes of permanents of (0,1)-matrices, p. 201-202.

    REFERENCES:
    Seok-Zun Song et al., Extremes of permanents of (0,1)-matrices,
    Lin. Algebra and its Applic. 373 (2003), p. 197-210.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A090015;a
        Permanent of (0,1)-matrix of size n X (n+d) with d=3 and n-1 zeros not on a line.
        sage: a(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be a positive integer
        sage: a(1)
        6
        sage: a(2)
        36
        sage: a.offset
        1
        sage: a(8)
        29976192
        sage: a(22)
        41552258517692116794936876
        sage: a.list(9)
        [6, 36, 258, 2136, 19998, 208524, 2393754, 29976192, 406446774]

    AUTHOR:
        -- Jaap Spies (2007-01-23)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=1)

    def _repr_(self):
        return "Permanent of (0,1)-matrix of size n X (n+d) with d=3 and n-1 zeros not on a line."

    def _eval(self, n):
        if n == 1:
            return ZZ(6)
        else:
            return  sloane.A001910(n+4) + sloane.A001910(n+3)

class A090016(SloaneSequence):
    r"""
    Permanent of (0,1)-matrix of size $n \times (n+d)$ with $d=6$ and $n-1$ zeros not on a line.

    $a(n) = (n+1)*a(n-1) + (n-2)*a(n-2) [a(1)=7, a(2)=49]$

    $A090016 a(n) = A090010(n-1) + A090010(n), a(1)=7$

    This is a special case of Theorem 2.3 of Seok-Zun Song et al.
    Extremes of permanents of (0,1)-matrices, p. 201-202.

    REFERENCES:
    Seok-Zun Song et al., Extremes of permanents of (0,1)-matrices,
    Lin. Algebra and its Applic. 373 (2003), p. 197-210.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A090016;a
        Permanent of (0,1)-matrix of size n X (n+d) with d=6 and n-1 zeros not on a line.
        sage: a(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be a positive integer
        sage: a(1)
        7
        sage: a(2)
        49
        sage: a.offset
        1
        sage: a(8)
        72737161
        sage: a(22)
        199341969448774341802426289
        sage: a.list(9)
        [7, 49, 399, 3689, 38087, 433713, 5394991, 72737161, 1056085191]

    AUTHOR:
        -- Jaap Spies (2007-01-23)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=1)

    def _repr_(self):
        return "Permanent of (0,1)-matrix of size n X (n+d) with d=6 and n-1 zeros not on a line."


    def _eval(self, n):
        if n == 1:
            return ZZ(7)
        else:
            return  sloane.A090010(n-1) + sloane.A090010(n)

class A000166(SloaneSequence):
    r"""
    Subfactorial or rencontres numbers, or derangements: number of permutations of $n$ elements with no fixed points.

    With offset 1 also the permanent of a (0,1)-matrix of order $n$ with $n$ 0's not on a line.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000166;a
        Subfactorial or rencontres numbers, or derangements: number of permutations of $n$ elements with no fixed points.
        sage: a(0)
        1
        sage: a(1)
        0
        sage: a(2)
        1
        sage: a.offset
        0
        sage: a(8)
        14833
        sage: a(20)
        895014631192902121
        sage: a.list(9)
        [1, 0, 1, 2, 9, 44, 265, 1854, 14833]

    AUTHOR:
        -- Jaap Spies (2007-01-13)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)

    def _repr_(self):
        return "Subfactorial or rencontres numbers, or derangements: number of permutations of $n$ elements with no fixed points."

    def _eval(self, n):
        return arith.subfactorial(n)


class A000203(SloaneSequence):
    r"""
    The sequence $\sigma(n)$, where $\sigma(n)$ is the sum of the
    divisors of $n$.   Also called $\sigma_1(n)$.

    The function \code{sigma(n, k)} implements $\sigma_k(n)$ in SAGE.

    INPUT:
        n -- positive integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000203; a
        sigma(n) = sum of divisors of n. Also called sigma_1(n).
        sage: a(1)
        1
        sage: a(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be a positive integer
        sage: a(256)
        511
        sage: a.list(12)
        [1, 3, 4, 7, 6, 12, 8, 15, 13, 18, 12, 28]
        sage: a(1/3)
        Traceback (most recent call last):
        ...
        TypeError: no coercion of this rational to integer

    AUTHOR:
        -- Jaap Spies (2007-01-13)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=1)

    def _repr_(self):
        return "sigma(n) = sum of divisors of n. Also called sigma_1(n)."

    def _eval(self, n):
        return sum(arith.divisors(n)) #alternative: return arith.sigma(n)

class A001157(SloaneSequence):
    r"""
    The sequence $\sigma_2(n)$, sum of squares of divisors of $n$.

    The function sigma(n, k) implements $\sigma_k*$ in SAGE.

    INPUT:
        n -- positive integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A001157;a
        sigma_2(n): sum of squares of divisors of n
        sage: a(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be a positive integer
        sage: a(2)
        5
        sage: a(8)
        85
        sage: a.list(9)
        [1, 5, 10, 21, 26, 50, 50, 85, 91]

    AUTHOR:
        -- Jaap Spies (2007-01-13)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=1)

    def _repr_(self):
        return "sigma_2(n): sum of squares of divisors of n"

    def _eval(self, n):
        return  arith.sigma(n,2)

class A008683(SloaneSequence):
    r"""
    Moebius (or M\"obius) function $\mu(n)$.

    INPUT:
        n -- positive integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A008683;a
        Moebius function mu(n).
        sage: a(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be a positive integer
        sage: a(2)
        -1
        sage: a(12)
        0
        sage: a.list(12)
        [1, -1, -1, 0, -1, 1, -1, 0, 0, 1, -1, 0]

    AUTHOR:
        -- Jaap Spies (2007-01-13)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=1)

    def _repr_(self):
        return "Moebius function mu(n)."

    def _eval(self, n):
        return  arith.moebius(n)



class A000204(SloaneSequence):
    r"""
     Lucas numbers (beginning with 1): $L(n) = L(n-1) + L(n-2)$ with $L(1) = 1$, $L(2) = 3$.

    EXAMPLES:
        sage: a = sloane.A000204; a
        Lucas numbers (beginning at 1): L(n) = L(n-1) + L(n-2), L(2) = 3.
        sage: a(1)
        1
        sage: a(8)
        47
        sage: a(200)
        627376215338105766356982006981782561278127
        sage: a(-4)
        Traceback (most recent call last):
        ...
        ValueError: input n (=-4) must be a positive integer
        sage: a.list(12)
        [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322]
        sage: a(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be a positive integer

    AUTHOR:
        -- Jaap Spies (2007-01-18)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=1)

    def _repr_(self):
        return "Lucas numbers (beginning at 1): L(n) = L(n-1) + L(n-2), L(2) = 3."

    def _eval(self, n):
        if n == 1:
            return 1
        elif n == 2:
            return 3
        else:
            return sloane.A000045(n+1) + sloane.A000045(n-1)

class A000217(SloaneSequence):
    r"""
    Triangular numbers: $a(n) = {n+1} \choose 2) = n(n+1)/2$.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000217;a
        Triangular numbers: a(n) = C(n+1,2) = n(n+1)/2 = 0+1+2+...+n.
        sage: a(0)
        0
        sage: a(2)
        3
        sage: a(8)
        36
        sage: a(2000)
        2001000
        sage: a.list(9)
        [0, 1, 3, 6, 10, 15, 21, 28, 36]

    AUTHOR:
        -- Jaap Spies (2007-01-25)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)

    def _repr_(self):
        return "Triangular numbers: a(n) = C(n+1,2) = n(n+1)/2 = 0+1+2+...+n."

    def _eval(self, n):
        return Integer(n*(n+1)//2)

class A002275(SloaneSequence):
    r"""
    Repunits: $\frac {(10^n - 1)}{9}$. Often denoted by $R_n$.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A002275;a
        Repunits: (10^n - 1)/9. Often denoted by R_n.
        sage: a(0)
        0
        sage: a(2)
        11
        sage: a(8)
        11111111
        sage: a(20)
        11111111111111111111
        sage: a.list(9)
        [0, 1, 11, 111, 1111, 11111, 111111, 1111111, 11111111]

    AUTHOR:
        -- Jaap Spies (2007-01-25)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)

    def _repr_(self):
        return "Repunits: (10^n - 1)/9. Often denoted by R_n."

    def _eval(self, n):
        return Integer(10**n-1)//9





# inhomogenous second order recurrences
def recur_gen2b(a0,a1,a2,a3,b):
    r"""
        inhomogenous second-order linear recurrence generator with fixed coefficients
        and $b = f(n)$

        $a(0) = a0$, $a(1) = a1$, $a(n) = a2*a(n-1) + a3*a(n-2) +f(n)$.
    """
    x, y = ZZ(a0), ZZ(a1)
    n = 1
    yield x
    while 1:
        n = n+1
        x, y = y, a3*x+a2*y + b(n)
        yield x

    # def f(n):
    #     if n > 1:
    #         return 7*n+1
    #     else:
    #         return 0
    # A051959 = recur_gen2b(1,10,2,1,f)


class A001110(SloaneSequence):
    r"""
    Numbers that are both triangular and square: $a(n) = 34a(n-1) - a(n-2) + 2$.


    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A001110; a
        Numbers that are both triangular and square: a(n) = 34a(n-1) - a(n-2) + 2.
        sage: a(0)
        0
        sage: a(1)
        1
        sage: a(8)
        55420693056
        sage: a(21)
        4446390382511295358038307980025
        sage: a.list(8)
        [0, 1, 36, 1225, 41616, 1413721, 48024900, 1631432881]

    AUTHOR:
        -- Jaap Spies (2007-01-19)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)
        self._b = []
        self._precompute()

    link = "http://www.research.att.com/~njas/sequences/A001110"

    def _repr_(self):
        return "Numbers that are both triangular and square: a(n) = 34a(n-1) - a(n-2) + 2."

    def g(self,k):
        if k > 1:
            return 2
        else:
            return 0

    def _precompute(self, how_many=20):
        try:
            f = self._f
        except AttributeError:
            self._f = recur_gen2b(0,1,34,-1,self.g)
            f = self._f
        self._b += [f.next() for i in range(how_many)]

    def _eval(self, n):
        if len(self._b) < n:
            self._precompute(n - len(self._b) + 1)
        return self._b[n]

    def list(self, n):
        self._eval(n)   # force computation
        return self._b[:n]

class A051959(SloaneSequence):
    r"""
    Linear second order recurrence. A051959.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A051959; a
        Linear second order recurrence. A051959.
        sage: a(0)
        1
        sage: a(1)
        10
        sage: a(8)
        9969
        sage: a(41)
        42834431872413650
        sage: a.list(12)
        [1, 10, 36, 104, 273, 686, 1688, 4112, 9969, 24114, 58268, 140728]

    AUTHOR:
        -- Jaap Spies (2007-01-19)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)
        self._b = []
        self._precompute(2)

    def _repr_(self):
        return "Linear second order recurrence. A051959."

    def g(self,k):
        if k > 1:
            return 7*k+1
        else:
            return 0

    def _precompute(self, how_many=30):
        try:
            f = self._f
        except AttributeError:
            self._f = recur_gen2b(1,10,2,1,self.g)
            f = self._f
        self._b += [f.next() for i in range(how_many)]

    def _eval(self, n):
        if len(self._b) < n:
            self._precompute(n - len(self._b) + 1)
        return self._b[n]

    def list(self, n):
        self._eval(n)   # force computation
        return self._b[:n]



class A001221(SloaneSequence):
    r"""
    Number of different prime divisors of $n$

    Also called omega(n) or $\omega(n)$.
    Maximal number of terms in any factorization of $n$.
    Number of prime powers that divide $n$.

    INPUT:
        n -- positive integer

    OUTPUT:
        integer -- function value


    EXAMPLES:
        sage: a = sloane.A001221; a
        Number of distinct primes dividing n (also called omega(n)).
        sage: a(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be a positive integer
        sage: a(1)
        0
        sage: a(8)
        1
        sage: a(41)
        1
        sage: a(84792)
        3
        sage: a.list(12)
        [0, 1, 1, 1, 1, 2, 1, 1, 1, 2, 1, 2]

    AUTHOR:
        - Jaap Spies (2007-01-19)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=1)

    def _repr_(self):
        return "Number of distinct primes dividing n (also called omega(n))."

    def _eval(self, n):
        return len(arith.prime_divisors(n)) # there is a PARI function omega



class A001222(SloaneSequence):
    r"""
    Number of prime divisors of $n$ (counted with multiplicity).

    Also called bigomega(n) or $\Omega(n)$.
    Maximal number of terms in any factorization of $n$.
    Number of prime powers that divide $n$.

    INPUT:
        n -- positive integer

    OUTPUT:
        integer -- function value


    EXAMPLES:
        sage: a = sloane.A001222; a
        Number of prime divisors of n (counted with multiplicity).
        sage: a(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be a positive integer
        sage: a(1)
        0
        sage: a(8)
        3
        sage: a(41)
        1
        sage: a(84792)
        5
        sage: a.list(12)
        [0, 1, 1, 2, 1, 2, 1, 3, 2, 2, 1, 3]

    AUTHOR:
        - Jaap Spies (2007-01-19)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=1)

    def _repr_(self):
        return "Number of prime divisors of n (counted with multiplicity)."

    def _eval(self, n):
        return sum([e for i,e in arith.factor(n)])

# A046660() = A001222(n) - A001221(n)
class A046660(SloaneSequence):
    r"""
    Excess of $n$ = number of prime divisors (with multiplicity) - number of prime divisors (without multiplicity).

    $\Omega(n) - \omega(n)$.

    INPUT:
        n -- positive integer

    OUTPUT:
        integer -- function value


    EXAMPLES:
        sage: a = sloane.A046660; a
        Excess of n = Bigomega (with multiplicity) - omega (without multiplicity).
        sage: a(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be a positive integer
        sage: a(1)
        0
        sage: a(8)
        2
        sage: a(41)
        0
        sage: a(84792)
        2
        sage: a.list(12)
        [0, 0, 0, 1, 0, 0, 0, 2, 1, 0, 0, 1]

    AUTHOR:
        - Jaap Spies (2007-01-19)
    """
    def _repr_(self):
        return "Excess of n = Bigomega (with multiplicity) - omega (without multiplicity)."

    def _eval(self, n):
        return sloane.A001222(n) - sloane.A001221(n)




class A001227(SloaneSequence):
    r"""
    Number of odd divisors of $n$.

    INPUT:
        n -- positive integer

    OUTPUT:
        integer -- function value


    EXAMPLES:
        sage: a = sloane.A001227; a
        Number of odd divisors of n
        sage: a.offset
        1
        sage: a(1)
        1
        sage: a(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be a positive integer
        sage: a(100)
        3
        sage: a(256)
        1
        sage: a(29)
        2
        sage: a.list(20)
        [1, 1, 2, 1, 2, 2, 2, 1, 3, 2, 2, 2, 2, 2, 4, 1, 2, 3, 2, 2]
        sage: a(-1)
        Traceback (most recent call last):
        ...
        ValueError: input n (=-1) must be a positive integer

        AUTHOR:
            - Jaap Spies (2007-01-14)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=1)

    def _repr_(self):
        return "Number of odd divisors of n"

    def _eval(self, n):
        return sum(i%2 for i in arith.divisors(n))

class A001358(SloaneSequence):
    r"""
    Products of two primes.

    These numbers have been called semiprimes (or semi-primes), biprimes or 2-almost primes.

    INPUT:
        n -- positive integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A001358;a
        Products of two primes.
        sage: a(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be a positive integer
        sage: a(2)
        6
        sage: a(8)
        22
        sage: a(200)
        669
        sage: a.list(9)
        [4, 6, 9, 10, 14, 15, 21, 22, 25]

    AUTHOR:
        -- Jaap Spies (2007-01-25)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=1)

    def _repr_(self):
        return "Products of two primes."

    def _precompute(self, how_many=150):
        try:
            self._b
            n = self._n
        except AttributeError:
            self._b = []
            n = 1
            self._n = n
        self._b += [i for i in range(self._n, self._n+how_many) if sum(e for _,e in arith.factor(i)) == 2]
        self._n += how_many

    def _eval(self, n):
        try:
            return self._b[n-1]
        except (AttributeError, IndexError):
            self._precompute()
            # try again
            return self._eval(n)

    def list(self, n):
        try:
            if len(self._b) < n:
                raise IndexError
            else:
                return self._b[:n]
        except (AttributeError, IndexError):
            self._precompute()
            # try again
            return self.list(n)



class A001694(SloaneSequence):
    r"""
        This function returns the $n$-th Powerful Number:

        A positive integer $n$ is powerful if for every prime $p$ dividing
        $n$, $p^2$ also divides $n$.

    INPUT:
        n -- positive integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A001694; a
        Powerful Numbers (also called squarefull, square-full or 2-full numbers).
        sage: a.offset
        1
        sage: a(1)
        1
        sage: a(4)
        9
        sage: a(100)
        3136
        sage: a(156)
        7225
        sage: a.list(19)
        [1, 4, 8, 9, 16, 25, 27, 32, 36, 49, 64, 72, 81, 100, 108, 121, 125, 128, 144]
        sage: a(-1)
        Traceback (most recent call last):
        ...
        ValueError: input n (=-1) must be a positive integer

    AUTHOR:
        -- Jaap Spies (2007-01-14)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=1)

    def _repr_(self):
        return "Powerful Numbers (also called squarefull, square-full or 2-full numbers)."

    def _precompute(self, how_many=10000):
        try:
            self._b
            n = self._n
        except AttributeError:
            self._b = [1]
            n = 1
            self._n = n
        self._b += self._powerful_numbers_in_range(self._n, self._n+how_many)
        self._n += how_many

    def _powerful_numbers_in_range(self, n, m):

        # This is naive -- too slow; too much overhead
        #  return [i for i in range(self._n, self._n+how_many) if self.is_powerful(i)]

        if n < 4:
            n = 4
        # Use PARI directly -- much faster.
        pari("is_powerful(n)=vecmin(mattranspose(factor(n)[,2]))>1;")
        s = str(pari('v=listcreate(%s); for(n=%s,%s,if(is_powerful(n),listput(v,n))); v'%(m,n,m)))
        s = s[5:-1]

        ## GP version -- it's slower, but for completeness we leave it.
        ## from sage.interfaces.gp import gp
        ## gp.eval("is_powerful(n)=vecmin(mattranspose(factor(n)[,2]))>1;")
        ## s = '[' + gp.eval('for(n=%s,%s,if(is_powerful(n),print1(n,",")))'%(n,m)).strip()[1:-1] + ']'

        v = eval(s)
        return [ZZ(x) for x in v]  # not very many, so not much overhead

    def _eval(self, n):
        try:
            return self._b[n-1]
        except AttributeError:
            self._b = [1]
        except IndexError:
            pass
        while len(self._b) < n:
            self._precompute(10000)
        # try again, but we could also return self._b[n-1]
        return self._eval(n)

    def list(self, n):
        try:
            if len(self._b) < n:
                raise IndexError
            else:
                return self._b[:n]
        except AttributeError:
            self._b = [1]
        except IndexError:
            pass
        while len(self._b) < n:
            self._precompute(10000)
        return self._b[:n]

    def is_powerful(self,n):
        r"""
        This function returns True if and only if $n$ is a Powerful Number:

        A positive integer $n$ is powerful if for every prime $p$ dividing
        $n$, $p^2$ also divides $n$.
        See Sloane's OEIS A001694.

        INPUT:
            n -- integer

        OUTPUT:
            True -- if $n$ is a Powerful number, else False

        EXAMPLES:
            sage: a = sloane.A001694
            sage: a.is_powerful(2500)
            True
            sage: a.is_powerful(20)
            False

        AUTHOR:
            - Jaap Spies (2006-12-07)
        """
#        for p in arith.prime_divisors(n):
#            if n % p**2 > 0:
#                return False
#        return True

        if n <= 1:
            return True
        ex = [e for _,e in arith.factor(n)]
        for e in ex:
            if e < 2:
                return False
        return True


class A001836(SloaneSequence):
    r"""
    Numbers $n$ such that $\phi(2n-1) < \phi(2n)$, where $\phi$ is
    Euler's totient function.

    Eulers totient function is also known as euler_phi,
    euler_phi is a standard SAGE function.

       INPUT:
        n -- positive integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A001836; a
        Numbers n such that phi(2n-1) < phi(2n), where phi is Euler's totient function A000010.
        sage: a.offset
        1
        sage: a(1)
        53
        sage: a(8)
        683
        sage: a(300)
        17798
        sage: a.list(12)
        [53, 83, 158, 263, 293, 368, 578, 683, 743, 788, 878, 893]
        sage: a(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be a positive integer

        Compare:
        Searching Sloane's online database...
        Numbers n such that phi(2n-1) < phi(2n), where phi is Eler's totient function A000010.
        [53, 83, 158, 263, 293, 368, 578, 683, 743, 788, 878, 893]

    AUTHOR:
        -- Jaap Spies (2007-01-17)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=1)


    def _repr_(self):
        return "Numbers n such that phi(2n-1) < phi(2n), where phi is Euler's totient function A000010."

    def _precompute(self, how_many=150):
        try:
            self._b
            n = self._n
        except AttributeError:
            self._b = []
            n = self.offset
            self._n = n
        self._b += [i for i in range(self._n, self._n+how_many) if arith.euler_phi(2*i-1) < arith.euler_phi(2*i)]
        self._n += how_many

    def _eval(self, n):
        try:
            return self._b[n-1]
        except (AttributeError, IndexError):
            self._precompute()
            # try again
            return self._eval(n)

    def list(self, n):
        try:
            if len(self._b) < n:
                raise IndexError
            else:
                return self._b[:n]
        except (AttributeError, IndexError):
            self._precompute()
            # try again
            return self.list(n)




# a group of sequences uses this function:
def recur_gen2(a0,a1,a2,a3):
    """
        homogenous general second-order linear recurrence generator with fixed coefficients

        a(0) = a0, a(1) = a1, a(n) = a2*a(n-1) + a3*a(n-2)
    """
    x, y = ZZ(a0), ZZ(a1)
    n = 0
    yield x
    while 1:
        n = n+1
        x, y = y, a3*x+a2*y
        yield x


# A001906 = recur_gen2(0,1,3,-1)
# This can be done much more simple: return sloane.A000045(2*n).
# but this is a proof of technology!
class A001906(SloaneSequence):
    r"""
    $F(2n) =$ bisection of Fibonacci sequence: $a(n)=3a(n-1)-a(n-2)$.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A001906; a
        F(2n) = bisection of Fibonacci sequence: a(n)=3a(n-1)-a(n-2).
        sage: a(0)
        0
        sage: a(1)
        1
        sage: a(8)
        987
        sage: a(22)
        701408733
        sage: a.list(12)
        [0, 1, 3, 8, 21, 55, 144, 377, 987, 2584, 6765, 17711]

    AUTHOR:
        -- Jaap Spies (2007-01-19)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)
        self._b = []
        self._precompute(2)  # force precomputation

    def _repr_(self):
        return "F(2n) = bisection of Fibonacci sequence: a(n)=3a(n-1)-a(n-2)."

    def _precompute(self, how_many=150):
        try:
            f = self._f
        except AttributeError:
            self._f = recur_gen2(0,1,3,-1)
            f = self._f
        self._b += [f.next() for i in range(how_many)]

    def _eval(self, n):
        if len(self._b) <= n:
            self._precompute(n - len(self._b) + 1)
        return self._b[n]

    def list(self, n):
        self._eval(n)   # force computation
        return self._b[:n]

class A001045(SloaneSequence):
    r"""
    Jacobsthal sequence: $a(n) = a(n-1) + 2a(n-2)$, $a(0) = 0$ and $a(1) = 1$.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A001045;a
        Jacobsthal sequence: a(n) = a(n-1) + 2a(n-2).
        sage: a(0)
        0
        sage: a(1)
        1
        sage: a(2)
        1
        sage: a(11)
        683
        sage: a.list(12)
        [0, 1, 1, 3, 5, 11, 21, 43, 85, 171, 341, 683]

    AUTHOR:
        -- Jaap Spies (2007-01-26)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)
        self._b = []
        self._precompute(2)  # force precomputation

    def _repr_(self):
        return "Jacobsthal sequence: a(n) = a(n-1) + 2a(n-2)."

    def _precompute(self, how_many=50):
        try:
            f = self._f
        except AttributeError:
            self._f = recur_gen2(0,1,1,2)
            f = self._f
        self._b += [f.next() for i in range(how_many)]

    def _eval(self, n):
        if len(self._b) <= n:
            self._precompute(n - len(self._b) + 1)
        return self._b[n]

    def list(self, n):
        self._eval(n)   # force computation
        return self._b[:n]



class A000129(SloaneSequence):
    r"""
    Pell numbers: $a(0) = 0$, $a(1) = 1$; for $n > 1$, $a(n) = 2a(n-1) + a(n-2)$.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000129;a
        Pell numbers: a(0) = 0, a(1) = 1; for n > 1, a(n) = 2*a(n-1) + a(n-2).
        sage: a(0)
        0
        sage: a(2)
        2
        sage: a(12)
        13860
        sage: a.list(12)
        [0, 1, 2, 5, 12, 29, 70, 169, 408, 985, 2378, 5741]

    AUTHOR:
        -- Jaap Spies (2007-01-25)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)
        self._b = []
        self._precompute(2)  # force precomputation

    def _repr_(self):
        return "Pell numbers: a(0) = 0, a(1) = 1; for n > 1, a(n) = 2*a(n-1) + a(n-2)."

    def _precompute(self, how_many=150):
        try:
            f = self._f
        except AttributeError:
            self._f = recur_gen2(0,1,2,1)
            f = self._f
        self._b += [f.next() for i in range(how_many)]

    def _eval(self, n):
        if len(self._b) <= n:
            self._precompute(n - len(self._b) + 1)
        return self._b[n]

    def list(self, n):
        self._eval(n)   # force computation
        return self._b[:n]


class A001109(SloaneSequence):
    r"""
    $a(n)^2$ is a triangular number: $a(n) = 6*a(n-1) - a(n-2)$ with $a(0)=0$, $a(1)=1$.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A001109;a
        a(n)^2 is a triangular number: a(n) = 6*a(n-1) - a(n-2) with a(0)=0, a(1)=1
        sage: a(0)
        0
        sage: a(1)
        1
        sage: a(2)
        6
        sage: a.offset
        0
        sage: a(8)
        235416
        sage: a(60)
        1515330104844857898115857393785728383101709300
        sage: a.list(9)
        [0, 1, 6, 35, 204, 1189, 6930, 40391, 235416]

    AUTHOR:
        -- Jaap Spies (2007-01-24)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)
        self._b = []
        self._precompute(2)  # force precomputation

    def _repr_(self):
        return "a(n)^2 is a triangular number: a(n) = 6*a(n-1) - a(n-2) with a(0)=0, a(1)=1"

    def _precompute(self, how_many=50):
        try:
            f = self._f
        except AttributeError:
            self._f = recur_gen2(0,1,6,-1)
            f = self._f
        self._b += [f.next() for i in range(how_many)]

    def _eval(self, n):
        if len(self._b) <= n:
            self._precompute(n - len(self._b) + 1)
        return self._b[n]

    def list(self, n):
        self._eval(n)   # force computation
        return self._b[:n]



class A015521(SloaneSequence):
    r"""
    Linear 2nd order recurrence, $a(0)=0$, $a(1)=1$ and $a(n) = 3 a(n-1) + 4 a(n-2)$.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A015521; a
        Linear 2nd order recurrence, a(n) = 3 a(n-1) + 4 a(n-2).
        sage: a(0)
        0
        sage: a(1)
        1
        sage: a(8)
        13107
        sage: a(41)
        967140655691703339764941
        sage: a.list(12)
        [0, 1, 3, 13, 51, 205, 819, 3277, 13107, 52429, 209715, 838861]

    AUTHOR:
        -- Jaap Spies (2007-01-19)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)
        self._b = []
        self._precompute(2)

    def _repr_(self):
        return "Linear 2nd order recurrence, a(n) = 3 a(n-1) + 4 a(n-2)."

    def _precompute(self, how_many=150):
        try:
            f = self._f
        except AttributeError:
            self._f = recur_gen2(0,1,3,4)
            f = self._f
        self._b += [f.next() for i in range(how_many)]

    def _eval(self, n):
        if len(self._b) <= n:
            self._precompute(n - len(self._b) + 1)
        return self._b[n]

    def list(self, n):
        self._eval(n)   # force computation
        return self._b[:n]

class A015523(SloaneSequence):
    r"""
    Linear 2nd order recurrence, $a(0)=0$, $a(1)=1$ and $a(n) = 3 a(n-1) + 5 a(n-2)$.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A015523; a
        Linear 2nd order recurrence, a(n) = 3 a(n-1) + 5 a(n-2).
        sage: a(0)
        0
        sage: a(1)
        1
        sage: a(8)
        17727
        sage: a(41)
        6173719566474529739091481
        sage: a.list(12)
        [0, 1, 3, 14, 57, 241, 1008, 4229, 17727, 74326, 311613, 1306469]

    AUTHOR:
        -- Jaap Spies (2007-01-19)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)
        self._b = []
        self._precompute(2)

    def _repr_(self):
        return "Linear 2nd order recurrence, a(n) = 3 a(n-1) + 5 a(n-2)."

    def _precompute(self, how_many=150):
        try:
            f = self._f
        except AttributeError:
            self._f = recur_gen2(0,1,3,5)
            f = self._f
        self._b += [f.next() for i in range(how_many)]

    def _eval(self, n):
        if len(self._b) <= n:
            self._precompute(n - len(self._b) + 1)
        return self._b[n]

    def list(self, n):
        self._eval(n)   # force computation
        return self._b[:n]

class A015530(SloaneSequence):
    r"""
    Linear 2nd order recurrence, $a(0)=0$, $a(1)=1$ and $a(n) = 4 a(n-1) + 3 a(n-2)$.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A015530;a
        Linear 2nd order recurrence, a(n) = 4 a(n-1) + 3 a(n-2).
        sage: a(0)
        0
        sage: a(1)
        1
        sage: a(2)
        4
        sage: a.offset
        0
        sage: a(8)
        41008
        sage: a.list(9)
        [0, 1, 4, 19, 88, 409, 1900, 8827, 41008]

    AUTHOR:
        -- Jaap Spies (2007-01-19)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)
        self._b = []
        self._precompute(2)

    def _repr_(self):
        return "Linear 2nd order recurrence, a(n) = 4 a(n-1) + 3 a(n-2)."

    def _precompute(self, how_many=50):
        try:
            f = self._f
        except AttributeError:
            self._f = recur_gen2(0,1,4,3)
            f = self._f
        self._b += [f.next() for i in range(how_many)]

    def _eval(self, n):
        if len(self._b) <= n:
            self._precompute(n - len(self._b) + 1)
        return self._b[n]

    def list(self, n):
        self._eval(n)   # force computation
        return self._b[:n]


class A015531(SloaneSequence):
    r"""
    Linear 2nd order recurrence, $a(0)=0$, $a(1)=1$ and $a(n) = 4 a(n-1) + 5 a(n-2)$.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A015531;a
        Linear 2nd order recurrence, a(n) = 4 a(n-1) + 5 a(n-2).
        sage: a(0)
        0
        sage: a(1)
        1
        sage: a(2)
        4
        sage: a.offset
        0
        sage: a(8)
        65104
        sage: a(60)
        144560289664733924534327040115992228190104
        sage: a.list(9)
        [0, 1, 4, 21, 104, 521, 2604, 13021, 65104]

    AUTHOR:
        -- Jaap Spies (2007-01-19)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)
        self._b = []
        self._precompute(2)

    def _repr_(self):
        return "Linear 2nd order recurrence, a(n) = 4 a(n-1) + 5 a(n-2)."

    def _precompute(self, how_many=50):
        try:
            f = self._f
        except AttributeError:
            self._f = recur_gen2(0,1,4,5)
            f = self._f
        self._b += [f.next() for i in range(how_many)]

    def _eval(self, n):
        if len(self._b) <= n:
            self._precompute(n - len(self._b) + 1)
        return self._b[n]

    def list(self, n):
        self._eval(n)   # force computation
        return self._b[:n]

class A015551(SloaneSequence):
    r"""
    Linear 2nd order recurrence, $a(0)=0$, $a(1)=1$ and $a(n) = 4 a(n-1) + 5 a(n-2)$.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A015531;a
        Linear 2nd order recurrence, a(n) = 4 a(n-1) + 5 a(n-2).
        sage: a(0)
        0
        sage: a(1)
        1
        sage: a(2)
        4
        sage: a.offset
        0
        sage: a(8)
        65104
        sage: a(60)
        144560289664733924534327040115992228190104
        sage: a.list(9)
        [0, 1, 4, 21, 104, 521, 2604, 13021, 65104]

    AUTHOR:
        -- Jaap Spies (2007-01-19)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)
        self._b = []
        self._precompute(2)

    def _repr_(self):
        return "Linear 2nd order recurrence, a(n) = 4 a(n-1) + 5 a(n-2)."

    def _precompute(self, how_many=50):
        try:
            f = self._f
        except AttributeError:
            self._f = recur_gen2(0,1,4,5)
            f = self._f
        self._b += [f.next() for i in range(how_many)]

    def _eval(self, n):
        if len(self._b) <= n:
            self._precompute(n - len(self._b) + 1)
        return self._b[n]

    def list(self, n):
        self._eval(n)   # force computation
        return self._b[:n]




# todo jsp
#
#
# A015551 = recur_gen2(0,1,6,5)
# A015552 = recur_gen2(0,1,6,7)
# A015553 = recur_gen2(0,1,6,11)
# A015555 = recur_gen2(0,1,7,2)
#
# A015565 = recur_gen2(0,1,7,8)
#
# A015585 = recur_gen2(0,1,9,10)
#
# A053404 = recur_gen2(1,1,1,12)
#
# A053428 = recur_gen2(1,1,1,20)
#
# A053430 = recur_gen2(1,1,1,30)
#
# A065874 = recur_gen2(1,1,1,42)
#
# A083858 = recur_gen2(0,1,3,6)
# and more!

# Wilf_A083216 = recur_gen2(20615674205555510, 3794765361567513,1,1)  family
class A082411(SloaneSequence):
    r"""
    Second-order linear recurrence sequence with $a(n) = a(n-1) + a(n-2)$.

    $a(0) = 407389224418$,
    $a(1) = 76343678551$. This is the second-order linear
    recurrence sequence with $a(0)$ and $a(1)$ co- prime, that R. L. Graham in 1964
    stated did not contain any primes.


    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A082411;a
        Second-order linear recurrence sequence with a(n) = a(n-1) + a(n-2).
        sage: a(1)
        76343678551
        sage: a(2)
        483732902969
        sage: a(3)
        560076581520
        sage: a(20)
        2219759332689173
        sage: a.list(4)
        [407389224418, 76343678551, 483732902969, 560076581520]

    AUTHOR:
        -- Jaap Spies (2007-01-23)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)
        self._b = []
        self._precompute(2)

    def _repr_(self):
        return "Second-order linear recurrence sequence with a(n) = a(n-1) + a(n-2)."

    def _precompute(self, how_many=10):
        try:
            f = self._f
        except AttributeError:
            self._f = recur_gen2(407389224418,76343678551,1,1)
            f = self._f
        self._b += [f.next() for i in range(how_many)]

    def _eval(self, n):
        if len(self._b) <= n:
            self._precompute(n - len(self._b) + 1)
        return self._b[n]

    def list(self, n):
        self._eval(n)   # force computation
        return self._b[:n]



class A083103(SloaneSequence):
    r"""
    Second-order linear recurrence sequence with $a(n) = a(n-1) + a(n-2)$.

    $a(0) = 1786772701928802632268715130455793$,
    $a(1) = 1059683225053915111058165141686995$. This is the second-order linear
    recurrence sequence with $a(0)$ and $a(1)$ co- prime, that R. L. Graham in 1964
    stated did not contain any primes. It has not been verified.
    Graham made a mistake in the calculation that was corrected by D. E. Knuth in 1990.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A083103;a
        Second-order linear recurrence sequence with a(n) = a(n-1) + a(n-2).
        sage: a(1)
        1059683225053915111058165141686995
        sage: a(2)
        2846455926982717743326880272142788
        sage: a(3)
        3906139152036632854385045413829783
        sage: a.offset
        0
        sage: a(8)
        45481392851206651551714764671352204
        sage: a(20)
        14639253684254059531823985143948191708
        sage: a.list(4)
        [1786772701928802632268715130455793, 1059683225053915111058165141686995, 2846455926982717743326880272142788, 3906139152036632854385045413829783]

    AUTHOR:
        -- Jaap Spies (2007-01-23)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)
        self._b = []
        self._precompute(2)

    def _repr_(self):
        return "Second-order linear recurrence sequence with a(n) = a(n-1) + a(n-2)."

    def _precompute(self, how_many=10):
        try:
            f = self._f
        except AttributeError:
            self._f = recur_gen2(1786772701928802632268715130455793,1059683225053915111058165141686995,1,1)
            f = self._f
        self._b += [f.next() for i in range(how_many)]

    def _eval(self, n):
        if len(self._b) <= n:
            self._precompute(n - len(self._b) + 1)
        return self._b[n]

    def list(self, n):
        self._eval(n)   # force computation
        return self._b[:n]

class A083104(SloaneSequence):
    r"""
    Second-order linear recurrence sequence with $a(n) = a(n-1) + a(n-2)$.

    $a(0) = 331635635998274737472200656430763$,
    $a(1) = 1510028911088401971189590305498785$. This is the second-order linear
    recurrence sequence with $a(0)$ and $a(1)$ co-prime.
    It was found by Ronald Graham in 1990.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A083104;a
        Second-order linear recurrence sequence with a(n) = a(n-1) + a(n-2).
        sage: a(3)
        3351693458175078679851381267428333
        sage: a.offset
        0
        sage: a(8)
        36021870400834012982120004949074404
        sage: a(20)
        11601914177621826012468849361236300628

    AUTHOR:
        -- Jaap Spies (2007-01-23)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)
        self._b = []
        self._precompute(2)

    def _repr_(self):
        return "Second-order linear recurrence sequence with a(n) = a(n-1) + a(n-2)."

    def _precompute(self, how_many=10):
        try:
            f = self._f
        except AttributeError:
            self._f = recur_gen2(331635635998274737472200656430763,1510028911088401971189590305498785,1,1)
            f = self._f
        self._b += [f.next() for i in range(how_many)]

    def _eval(self, n):
        if len(self._b) <= n:
            self._precompute(n - len(self._b) + 1)
        return self._b[n]

    def list(self, n):
        self._eval(n)   # force computation
        return self._b[:n]

class A083105(SloaneSequence):
    r"""
    Second-order linear recurrence sequence with $a(n) = a(n-1) + a(n-2)$.

    $a(0) = 62638280004239857$,
    $a(1) = 49463435743205655$. This is the second-order linear
    recurrence sequence with $a(0)$ and $a(1)$ co-prime.
    It was found by Donald Knuth in 1990.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A083105;a
        Second-order linear recurrence sequence with a(n) = a(n-1) + a(n-2).
        sage: a(1)
        49463435743205655
        sage: a(2)
        112101715747445512
        sage: a(3)
        161565151490651167
        sage: a.offset
        0
        sage: a(8)
        1853029790662436896
        sage: a(20)
        596510791500513098192
        sage: a.list(4)
        [62638280004239857, 49463435743205655, 112101715747445512, 161565151490651167]

    AUTHOR:
        -- Jaap Spies (2007-01-23)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)
        self._b = []
        self._precompute(2)

    def _repr_(self):
        return "Second-order linear recurrence sequence with a(n) = a(n-1) + a(n-2)."

    def _precompute(self, how_many=10):
        try:
            f = self._f
        except AttributeError:
            self._f = recur_gen2(62638280004239857,49463435743205655,1,1)
            f = self._f
        self._b += [f.next() for i in range(how_many)]

    def _eval(self, n):
        if len(self._b) <= n:
            self._precompute(n - len(self._b) + 1)
        return self._b[n]

    def list(self, n):
        self._eval(n)   # force computation
        return self._b[:n]




class A083216(SloaneSequence):
    r"""
    Second-order linear recurrence sequence with $a(n) = a(n-1) + a(n-2)$.

    $a(0) = 20615674205555510$, $a(1) = 3794765361567513$. This is a
    second-order linear recurrence sequence with $a(0)$ and $a(1)$
    co-prime that does not contain any primes. It was found by Herbert Wilf in 1990.

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A083216; a
        Second-order linear recurrence sequence with a(n) = a(n-1) + a(n-2).
        sage: a(0)
        20615674205555510
        sage: a(1)
        3794765361567513
        sage: a(8)
        347693837265139403
        sage: a(41)
        2738025383211084205003383
        sage: a.list(4)
        [20615674205555510, 3794765361567513, 24410439567123023, 28205204928690536]

    AUTHOR:
        -- Jaap Spies (2007-01-19)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)
        self._b = []
        self._precompute(2)

    def _repr_(self):
        return "Second-order linear recurrence sequence with a(n) = a(n-1) + a(n-2)."

    def _precompute(self, how_many=10):
        try:
            f = self._f
        except AttributeError:
            self._f = recur_gen2(20615674205555510, 3794765361567513,1,1)
            f = self._f
        self._b += [f.next() for i in range(how_many)]

    def _eval(self, n):
        if len(self._b) < n:
            self._precompute(n - len(self._b) + 1)
        return self._b[n]

    def list(self, n):
        self._eval(n)   # force computation
        return self._b[:n]





class A061084(SloaneSequence):
    r"""
    Fibonacci-type sequence based on subtraction: $a(0) = 1$, $a(1) = 2$ and $a(n) = a(n-2)-a(n-1)$.

    EXAMPLES:
        sage: a = sloane.A061084; a
        Fibonacci-type sequence based on subtraction: a(0) = 1, a(1) = 2 and a(n) = a(n-2)-a(n-1).
        sage: a(0)
        1
        sage: a(1)
        2
        sage: a(8)
        -29
        sage: a(22)
        -24476
        sage: a.list(12)
        [1, 2, -1, 3, -4, 7, -11, 18, -29, 47, -76, 123]
        sage: a.keyword
        ['sign', 'easy', 'nice']

    AUTHOR:
        -- Jaap Spies (2007-01-18)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)

    keyword = ["sign", "easy","nice"]

    def _repr_(self):
        return "Fibonacci-type sequence based on subtraction: a(0) = 1, a(1) = 2 and a(n) = a(n-2)-a(n-1)."

    def _eval(self, n):
        if n == 0:
            return 1
        elif n == 1:
            return 2
        else:
            return (-1)**(n-1)*sloane.A000204(n-1)


# a group of sequences uses this function:
def recur_gen3(a0,a1,a2,a3,a4,a5):
    """
        homogenous general second-order linear recurrence generator with fixed coefficients

        a(0) = a0, a(1) = a1, a(2) = a2, a(n) = a3*a(n-1) + a4*a(n-2) + a5*a(n-3)
    """
    x, y ,z = Integer(a0), Integer(a1), Integer(a2)
    n = 0
    yield x
    while 1:
        n = n+1
        x, y, z = y, z, a5*x+a4*y+a3*z
        yield x

class A000213(SloaneSequence):
    r"""
    Tribonacci numbers: a(n) = a(n-1) + a(n-2) + a(n-3). Starting with 1, 1, 1, ...


    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000213;a
        Tribonacci numbers: a(n) = a(n-1) + a(n-2) + a(n-3).
        sage: a(0)
        1
        sage: a(1)
        1
        sage: a(2)
        1
        sage: a(11)
        355
        sage: a.list(12)
        [1, 1, 1, 3, 5, 9, 17, 31, 57, 105, 193, 355]

    AUTHOR:
        -- Jaap Spies (2007-01-19)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)
        self._b = []
        self._precompute()

    def _repr_(self):
        return "Tribonacci numbers: a(n) = a(n-1) + a(n-2) + a(n-3)."

    def _precompute(self, how_many=20):
        try:
            f = self._f
        except AttributeError:
            self._f = recur_gen3(1,1,1,1,1,1)
            f = self._f
        self._b += [f.next() for i in range(how_many)]

    def _eval(self, n):
        if len(self._b) <= n:
            self._precompute(n - len(self._b) + 1)
        return self._b[n]

    def list(self, n):
        self._eval(n)   # force computation
        return self._b[:n]

# Tribonacci numbers: a(n) = a(n-1) + a(n-2) + a(n-3). Starting with 0, 0, 1.
class A000073(SloaneSequence):
    r"""
    Tribonacci numbers: a(n) = a(n-1) + a(n-2) + a(n-3). Starting with 0, 0, 1, ...


    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000073;a
        Tribonacci numbers: a(n) = a(n-1) + a(n-2) + a(n-3).
        sage: a(0)
        0
        sage: a(1)
        0
        sage: a(2)
        1
        sage: a(11)
        149
        sage: a.list(12)
        [0, 0, 1, 1, 2, 4, 7, 13, 24, 44, 81, 149]

    AUTHOR:
        -- Jaap Spies (2007-01-19)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)
        self._b = []
        self._precompute()

    def _repr_(self):
        return "Tribonacci numbers: a(n) = a(n-1) + a(n-2) + a(n-3)."

    def _precompute(self, how_many=20):
        try:
            f = self._f
        except AttributeError:
            self._f = recur_gen3(0,0,1,1,1,1)
            f = self._f
        self._b += [f.next() for i in range(how_many)]

    def _eval(self, n):
        if len(self._b) <= n:
            self._precompute(n - len(self._b) + 1)
        return self._b[n]

    def list(self, n):
        self._eval(n)   # force computation
        return self._b[:n]




def perm_mh(m, h):
    """
    This functions calculates $f(g,h)$ from Sloane's sequences A079908-A079928

    INPUT:
        m -- positive integer
        h -- non negative integer

    OUTPUT:
        permanent of the m x (m+h) matrix, etc.

    EXAMPLES:
        sage: from sage.combinat.sloane_functions import perm_mh
        sage: perm_mh(3,3)
        36
        sage: perm_mh(3,4)
        76

    AUTHOR: Jaap Spies (2006)
    """
    n = m + h
    M = MatrixSpace(QQ, m, n) # shouldn't this be 'ZZ' because A is (0,1) matrix?
    A = M(0)
    for i in range(m):
        for j in range(n):
            if i <= j and j <= i + h:
                A[i,j] = 1
    return A.permanent()



class A079922(SloaneSequence):
    r"""
    function returns solutions to the Dancing School problem with $n$ girls and $n+3$ boys.

    The value is $per(B)$, the permanent of the (0,1)-matrix $B$
    of size $n \times n+3$ with $b(i,j)=1$ if and only if $i \le j \le i+n$.

    REFERENCES:
        Jaap Spies, Nieuw Archief voor Wiskunde, 5/7 nr 4, December 2006


    INPUT:
        n -- positive integer

    OUTPUT:
        integer -- function value


    EXAMPLES:
        sage: a = sloane.A079922; a
        Solutions to the Dancing School problem with n girls and n+3 boys
        sage: a.offset
        1
        sage: a(1)
        4
        sage: a(8)
        2227
        sage: a.list(8)
        [4, 13, 36, 90, 212, 478, 1044, 2227]

        Compare:
        Searching Sloane's online database...
        Solution to the Dancing School Problem with n girls and n+3 boys: f(n,3).
        [4, 13, 36, 90, 212, 478, 1044, 2227]

        sage: a(-1)
        Traceback (most recent call last):
        ...
        ValueError: input n (=-1) must be a positive integer

        AUTHOR:
            - Jaap Spies (2007-01-14)
    """

    def _repr_(self):
        return "Solutions to the Dancing School problem with n girls and n+3 boys"

    offset = 1

    def _eval(self, n):
        return perm_mh(n, 3)



class A079923(SloaneSequence):
    r"""
    function returns solutions to the Dancing School problem with $n$ girls and $n+4$ boys.

    The value is $per(B)$, the permanent of the (0,1)-matrix $B$
    of size $n \times n+3$ with $b(i,j)=1$ if and only if $i \le j \le i+n$.

    REFERENCES:
        Jaap Spies, Nieuw Archief voor Wiskunde, 5/7 nr 4, December 2006

    INPUT:
        n -- positive integer

    OUTPUT:
        integer -- function value


    EXAMPLES:
        sage: a = sloane.A079923; a
        Solutions to the Dancing School problem with n girls and n+4 boys
        sage: a.offset
        1
        sage: a(1)
        5
        sage: a(8)
        15458
        sage: a.list(8)
        [5, 21, 76, 246, 738, 2108, 5794, 15458]

        Compare:
        Searching Sloane's online database...
        Solution to the Dancing School Problem with n girls and n+4 boys: f(n,4).
        [5, 21, 76, 246, 738, 2108, 5794, 15458]

        sage: a(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be a positive integer

    AUTHOR:
        - Jaap Spies (2007-01-17)
    """

    def _repr_(self):
        return "Solutions to the Dancing School problem with n girls and n+4 boys"

    offset = 1

    def _eval(self, n):
        return perm_mh(n, 4)


class A111774(SloaneSequence):
    r"""
    Sequence of numbers of the third kind, i.e., numbers that can be
    written as a sum of at least three consecutive positive integers.

    Odd primes can only be written as a sum of two consecutive integers.
    Powers of 2 do not have a representation as a sum of $k$ consecutive
    integers (other than the trivial $n = n$ for $k = 1$).

    See: http://www.jaapspies.nl/mathfiles/problem2005-2C.pdf


    INPUT:
        n -- positive integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A111774; a
        Numbers that can be written as a sum of at least three consecutive positive integers.
        sage: a(1)
        6
        sage: a(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be a positive integer
        sage: a(100)
        141
        sage: a(156)
        209
        sage: a(302)
        386
        sage: a.list(12)
        [6, 9, 10, 12, 14, 15, 18, 20, 21, 22, 24, 25]
        sage: a(1/3)
        Traceback (most recent call last):
        ...
        TypeError: no coercion of this rational to integer

    AUTHOR:
        -- Jaap Spies (2007-01-13)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=1)

    def _repr_(self):
        return "Numbers that can be written as a sum of at least three consecutive positive integers."

    def _precompute(self, how_many=150):
        try:
            self._b
            n = self._n
        except AttributeError:
            self._b = []
            n = 1
            self._n = n
        self._b += [i for i in range(self._n, self._n+how_many) if self.is_number_of_the_third_kind(i)]
        self._n += how_many

    def _eval(self, n):
        try:
            return self._b[n-1]
        except (AttributeError, IndexError):
            self._precompute()
            # try again
            return self._eval(n)

    def list(self, n):
        try:
            if len(self._b) < n:
                raise IndexError
            else:
                return self._b[:n]
        except (AttributeError, IndexError):
            self._precompute()
            # try again
            return self.list(n)

    def is_number_of_the_third_kind(self, n):
        r"""
        This function returns True if and only if $n$ is a number of the third kind.

        A number is of the third kind if it can be written as a sum of at
        least three consecutive positive integers.  Odd primes can only be
        written as a sum of two consecutive integers.  Powers of 2 do not
        have a representation as a sum of $k$ consecutive integers (other
        than the trivial $n = n$ for $k = 1$).

        See: \url{http://www.jaapspies.nl/mathfiles/problem2005-2C.pdf}

        INPUT:
            n -- positive integer

        OUTPUT:
            True -- if n is not prime and not a power of 2
            False --

        EXAMPLES:
            sage: a = sloane.A111774
            sage: a.is_number_of_the_third_kind(6)
            True
            sage: a.is_number_of_the_third_kind(100)
            True
            sage: a.is_number_of_the_third_kind(16)
            False
            sage: a.is_number_of_the_third_kind(97)
            False

        AUTHOR:
            -- Jaap Spies (2006-12-09)
        """
        if (not arith.is_prime(n)) and (not arith.is_power_of_two(n)):
            return True
        else:
            return False


class A111775(SloaneSequence):
    r"""
    Number of ways $n$ can be written as a sum of at least three consecutive integers.

    Powers of 2 and (odd) primes can not be written as a sum of at least
    three consecutive integers. $a(n)$ strongly depends on the number
    of odd divisors of $n$ (A001227):
    Suppose $n$ is to be written as sum of $k$ consecutive integers
    starting with $m$, then $2n = k(2m + k - 1)$.
    Only one of the factors is odd. For each odd divisor of $n$
    there is a unique corresponding $k$, $k=1$ and $k=2$ must be excluded.

    See: \url{http://www.jaapspies.nl/mathfiles/problem2005-2C.pdf}

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A111775; a
        Number of ways n can be written as a sum of at least three consecutive integers.

        sage: a(1)
        0
        sage: a(0)
        0

        We have a(15)=2 because 15 = 4+5+6 and 15 = 1+2+3+4+5. The number of odd divisors of 15 is 4.
        sage: a(15)
        2

        sage: a(100)
        2
        sage: a(256)
        0
        sage: a(29)
        0
        sage: a.list(20)
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 2, 0, 0, 2, 0]
        sage: a(1/3)
        Traceback (most recent call last):
        ...
        TypeError: no coercion of this rational to integer

    AUTHOR:
        -- Jaap Spies (2006-12-09)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)

    def _repr_(self):
        return "Number of ways n can be written as a sum of at least three consecutive integers."

    def _eval(self, n):
        if n == 1 or n == 0:
            return 0
        k = sum(i%2 for i in arith.divisors(n)) # A001227, the number of odd divisors
        if n % 2 ==0:
            return k-1
        else:
            return k-2

class A111776(SloaneSequence):
    r"""
    The $n$th term of the sequence $a(n)$ is the largest $k$ such that
    $n$ can be written as sum of $k$ consecutive integers.

    $n$ is the sum of at most $a(n)$ consecutive positive integers.
    Suppose $n$ is to be written as sum of $k$ consecutive integers starting
    with $m$, then $2n = k(2m + k - 1)$. Only one of the factors is odd.
    For each odd divisor $d$ of $n$ there is a unique corresponding
    $k = min(d,2n/d)$. $a(n)$ is the largest among those $k$
.
    See: \url{http://www.jaapspies.nl/mathfiles/problem2005-2C.pdf}

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    AUTHOR:
        -- Jaap Spies (2007-01-13)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)

    def _repr_(self):
        return "a(n) is the largest k such that n can be written as sum of k consecutive integers."

    def _eval(self, n):
        if n == 1 or n == 0:
            return 1
        m = 0
        for d in [i for i in arith.divisors(n) if i%2]: # d is odd divisor
            k = min(d, 2*n/d)
            if k > m:
                m = k
        return ZZ(m)

class A111787(SloaneSequence):
    r"""
    This function returns the $n$-th number of Sloane's sequence A111787


    $a(n)=0$ if $n$ is an odd prime or a power of 2. For numbers of the third
    kind (see A111774) we proceed as follows: suppose $n$ is to be written as sum of $k$
    consecutive integers starting with $m$, then $2n = k(2m + k - 1)$.
    Let $p$ be the smallest odd prime divisor of $n$ then
    $a(n) = min(p,2n/p)$.



       See: \url{http://www.jaapspies.nl/mathfiles/problem2005-2C.pdf}

    INPUT:
        n -- positive integer

    OUTPUT:
        integer -- function value


    EXAMPLES:
        sage: a = sloane.A111787; a
        a(n) is the least k >= 3 such that n can be written as sum of k consecutive integers. a(n)=0 if such a k does not exist.
        sage: a.offset
        1
        sage: a(1)
        0
        sage: a(0)
        Traceback (most recent call last):
        ...
        ValueError: input n (=0) must be a positive integer
        sage: a(100)
        5
        sage: a(256)
        0
        sage: a(29)
        0
        sage: a.list(20)
        [0, 0, 0, 0, 0, 3, 0, 0, 3, 4, 0, 3, 0, 4, 3, 0, 0, 3, 0, 5]
        sage: a(-1)
        Traceback (most recent call last):
        ...
        ValueError: input n (=-1) must be a positive integer

    AUTHOR:
        - Jaap Spies (2007-01-14)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=1)

    def _repr_(self):
        return "a(n) is the least k >= 3 such that n can be written as sum of k consecutive integers. a(n)=0 if such a k does not exist."

    def _eval(self, n):
        if arith.is_prime(n) or arith.is_power_of_two(n):
            return 0
        else:
            for d in srange(3,n,2):
                if n % d == 0:
                    return min(d, 2*n/d)


class ExponentialNumbers(SloaneSequence):
    r"""
    A sequence of Exponential numbers.
    """
    def __init__(self, a):
        SloaneSequence.__init__(self, offset=0)
        self.a = a

    def _repr_(self):
        return "Sequence of Exponential numbers around %s" % self.a

    def _eval(self, n):
        if hasattr(self, '__n'):
            if n < self.__n:
                return self.__data[n]
        from sage.combinat.expnums import expnums
        self.__data = expnums(n+1, self.a)
        self.__n = n+1
        return self.__data[n]

class A000110(ExponentialNumbers):
    r"""
    The sequence of Bell numbers.

    The Bell number $B_n$ counts the number of ways to put $n$
    distinguishable things into indistinguishable boxes such that no
    box is empty.

    Let $S(n, k)$ denote the Stirling number of the second kind.  Then
    $$B_n = \sum{k=0}^{n} S(n, k) .$$

    INPUT:
        n -- integer >= 0

    OUTPUT:
        integer -- $B_n$

    EXAMPLES:
        sage: a = sloane.A000110; a
        Sequence of Bell numbers
        sage: a.offset
        0
        sage: a(0)
        1
        sage: a(100)
        47585391276764833658790768841387207826363669686825611466616334637559114497892442622672724044217756306953557882560751
        sage: a.list(10)
        [1, 1, 2, 5, 15, 52, 203, 877, 4140, 21147]

    AUTHOR:
        -- Nick Alexander
    """
    def __init__(self):
        ExponentialNumbers.__init__(self, a=1)

    def _repr_(self):
        return "Sequence of Bell numbers"


class A000587(ExponentialNumbers):
    r"""
    The sequence of Uppuluri-Carpenter numbers.

    The Uppuluri-Carpenter number $C_n$ counts the imbalance in the
    number of ways to put $n$ distinguishable things into an even
    number of indistinguishable boxes versus into an odd number of
    indistinguishable boxes, such that no box is empty.

    Let $S(n, k)$ denote the Stirling number of the second kind.  Then
    $$C_n = \sum{k=0}^{n} (-1)^k S(n, k) .$$

    INPUT:
        n -- integer >= 0

    OUTPUT:
        integer -- $C_n$

    EXAMPLES:
        sage: a = sloane.A000587; a
        Sequence of Uppuluri-Carpenter numbers
        sage: a.offset
        0
        sage: a(0)
        1
        sage: a(100)
        397577026456518507969762382254187048845620355238545130875069912944235105204434466095862371032124545552161
        sage: a.list(10)
        [1, -1, 0, 1, 1, -2, -9, -9, 50, 267]

    AUTHOR:
        -- Nick Alexander
    """
    def __init__(self):
        ExponentialNumbers.__init__(self, a=-1)

    def _repr_(self):
        return "Sequence of Uppuluri-Carpenter numbers"



# A000100  a(n) = number of compositions of n in which the maximum part size is 3. Milestone!
#  a(n+3) = Sum[k=0..n, F(k)*T(n-k) ], F(i)=A000045(i+1), T(i)=A000073(i+2).
#  0, 0, 0, 1, 2, 5, 11, 23, 47, 94, 185, 360, 694, 1328, 2526, 4781, 9012, 16929, 31709, 59247

class A000100(SloaneSequence):
    r"""

    INPUT:
        n -- non negative integer

    OUTPUT:
        integer -- function value

    EXAMPLES:
        sage: a = sloane.A000100;a
        Number of compositions of n in which the maximum part size is 3.
        sage: a(0)
        0
        sage: a(1)
        0
        sage: a(2)
        0
        sage: a(3)
        1
        sage: a(11)
        360
        sage: a.list(12)
        [0, 0, 0, 1, 2, 5, 11, 23, 47, 94, 185, 360]

    AUTHOR:
        -- Jaap Spies (2007-01-26)
    """
    def __init__(self):
        SloaneSequence.__init__(self, offset=0)

    def _repr_(self):
        return "Number of compositions of n in which the maximum part size is 3."

    def _eval(self, n):
        if n <= 2:
            return 0
        else:
            return sum(sloane.A000045(i+1)*sloane.A000073(n-i-1) for i in range(n-2))





#############################################################
# III. Create the Sloane object, off which all the sequence
#      objects are members.
#############################################################

class Sloane(SageObject):
    r"""
    A collection of Sloane generating functions.

    This class inspects sage.combinat.sloane_functions, accumulating all the SloaneSequence classes starting with 'A'.  These are listed for tab completion, but not instantiated until requested.

    EXAMPLES:
        Ensure we have lots of entries:
        sage: len(sloane.trait_names()) > 100
        True

        And ensure none are being incorrectly returned:
        sage: [ None for n in sloane.trait_names() if not n.startswith('A') ]
        []

        Ensure we can access dynamic constructions and cache correctly:
        sage: s = sloane.A000587
        sage: s is sloane.A000587
        True

        And that we can access other functions in parent classes:
        sage: sloane.__class__
        <class 'sage.combinat.sloane_functions.Sloane'>

    AUTHOR: Nick Alexander
    """

    def trait_names(self):
        r"""List Sloane generating functions for tab-completion.

        The member classes are inspected from module sage.combinat.sloane_functions.

        They must be sub classes of SloaneSequence and must start with 'A'.  These
        restrictions are only to prevent typos, incorrect inspecting, etc.
        """
        try:
            return self.__trait_names
        except AttributeError:
            import sage.combinat.sloane_functions
            xs = inspect.getmembers(sage.combinat.sloane_functions, inspect.isclass)
            self.__trait_names = [ n for (n, c) in xs if n.startswith('A') and issubclass(c, SloaneSequence) ]
            return self.__trait_names

    def __getattribute__(self, name):
        r"""Construct and cache unique instances of Sloane generating function objects
        .
        """
        try:
            return SageObject.__getattribute__(self, name)
        except AttributeError:
            try:
                import sage.combinat.sloane_functions
                f = getattr(sage.combinat.sloane_functions, name)
                seq = f()
                setattr(self, name, seq)
                return seq
            except AttributeError:
                raise AttributeError, name

sloane = Sloane()
