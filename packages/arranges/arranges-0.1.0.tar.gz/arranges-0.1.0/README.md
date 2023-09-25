# Arranges

## Range string fields for Pydantic BaseModels

I needed a way to parse batches of byte, row and line and other object ranges
in my `merge-files` app, in a way that I can just drop it in as a string field
type. The reason for this is so the machine-generated command line help is
flat and readable by humans.

It it kinda grew into a monster so I've split it out into this separate
package. The main feature is a pair of classes that can represent ranges:

* `Segment` is a class that can be treated like a `set` and its constructor is
  compatible with `range` and `slice`. It is derived from `str` so serializes
  without custom JSON encoders. It is immutable, hashable and has a stable
  string representation.
* `Ranges` is an ordered `tuple` of `Segment`s. It is also immutable and
  derived from `str` so serializes without custom JSON encoders like the above.
  It can be constructed from comma-separated Python-style slice notation strings
  (e.g. `"1:10, 20:"`, `"0x00:0xff` and `":"`), integers, `slice`s, `range`s,
  integers and (nested) iterables of the above.
* An `inf` singleton that is a `float` with a value of `math.inf` but has an
  `__index__` that returns `sys.maxsize` and compares equal to infinity and
  `maxsize`, and its string representation is `"inf"`.

The range classes are designed to be used as fields in Pydantic `BaseModel`s,
but they can be used anywhere you need a range. They are not designed with
speed in mind, and comparisons usually use the canonical string form by
converting other things into `Ranges` objects.

## Constraints

I made it to select lines or bytes in a stream of data, so it:

* only supports `int`s;
* does not allow negative indices, the minimum is 0 and the maximum is
  unbounded;
* it's compatible with `range` and `slice`, but `step` is fixed to `1`. If
  you pass something with a step into its constructor it'll be converted to
  a list of `int`s (`range(0, 10, 2)` becomes `"0,2,4,6,8"`);
* does not support duplicate ranges. Ranges are merged together as they are
  added to the `Ranges` object;
* it is unpydantic in that its constructors are duck-typed, which is what I
  need; and
* it violates the Zen of Python by having multiple ways to do the same thing,
  but it's also useful.
* Currently the interface is *unstable*, so lock the exact version in if you
  don't want breaking changes.

## Installation

`pip install arranges` if you want to use it. You'll need Python 3.10 or
above.

### Dev setup

To add features etc you'll ideally need `git`, `make`, `bash` and something
with a debugger. Config for Visual Studio Code is included.

Clone the repo and `make dev` to make the venv, install dependencies, then
`code .` to open the project up in the venv with tests and debugging and all
that jazz.

Type `make help` to see the other options, or run the one-liner scripts in the
`./build` dir if you want to run steps without all that fancy caching nonsense.

## Usage

* [RTFM](https://bitplane.github.io/arranges/)
* Read [the tests](../arranges/tests/), which have full coverage.
* [Read the pydocs](../docs/pydocs.md)

## License

Free as in freedom from legalese; the [WTFPL with a warranty clause](../LICENSE).

Political note: I don't want to live in a world where lawyers tell me how to
speak. If you don't trust me enough to use the WTFPL then you shouldn't be
running my code in the first place.
