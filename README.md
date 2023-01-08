# envargs

`envargs` gives you an easy way of specifying which environment variables to
look for as program arguments/config. This library aims at providing an as 
similar as possible experience to that of using Python's `argparse` package.

## Why envargs?
As most containerized applications take most or at least part of their 
runtime config from environment variables I always seemed to reimplement the 
same parsing utilities for new projects. `envargs.EnvParser` gives you a 
no-dependencies quick way of specifying which variables your program needs 
to run, which are mandatory and which are not, and their data types. A 
single call to `parse_env` and your registered environment variables are 
decoded, ready to be used.

## Usage
Registering interesting variables and getting a hold of them in your running
program is very straight forward:
```python
import envargs

NUM_WORKERS = "NUM_WORKERS"
RETENTION_POLICY = "RETENTION_POLICY"
RETENTION_POLICY_DEFAULT = "keep-alive"

parser = envargs.EnvParser()
parser.add_variable(NUM_WORKERS, type=int, default=1)
parser.add_variable(RETENTION_POLICY, default=RETENTION_POLICY_DEFAULT)
namespace = parser.parse_env()

num_workers = namespace.num_workers
retention_policy = namespace.retention_policy
...
```
Register interesting variables with `add_variable` and call `parse_env()` to 
obtain a populated namespace. The namespace will have one property per found 
*registered* variable, named the same as the environment variable in lower 
case. Variable `NUM_WORKERS` thus gets the field name `namespace.num_workers`.

### Generating a description text
In addition, to further clarify how your 
application uses environment variables, an `envargs.EnvParser` provides a 
helpful description property that can help determine if you have set up your 
variables as expected. After calling `add_variables` on your `EnvParser` 
instance for each interesting variable, the parsers `description` field will 
contain a helpful text which describes all added variables, if they're 
required, their types, and their default values (if any).

```python
import envargs
import logging

LOGGER = logging.getLogger(__name__)

env_parser = envargs.EnvParser()
env_parser.add_variable("NUM_WORKERS", type=int)
env_parser.add_variable("RETRY_COUNTER", required=False, type=int)
env_parser.add_variable("OVERLOAD_LIMIT", default="high")

LOGGER.debug(env_parser.description)
```
This text can be added to an `argparse.ArgumentParser` description to show 
the text easily from the commandline. Note the use of the raw formatter 
class to avoid stripping line breaks.
```python
import argparse
import envargs

env_parser = envargs.EnvParser()
env_parser.add_variable("WORK_DIST_STRATEGY", default="round-robin")
env_parser.add_variable("CPU_OVERLOAD_LIMIT_PERCENT", type=int, default=80)

arg_parser = argparse.ArgumentParser(
   formatter_class=argparse.RawDescriptionHelpFormatter,
   description="""
This is the best program, ever written, clearly.

Below, some info on environment variables used \/
""" + env_parser.description)
...
```

### Variable properties
An environment variable, when registered, can be given a set of properties, 
all available as keyword arguments given to `EnvParser.add_variable(...)`. 
If no keyword arguments are given, just the name of the environment variable 
itself, it will be assumed that:
1. The variable is required (raising a `RequiredError` in case it's missing)
2. The variable is a string (meaning no special decoding of the string 
   gotten from `os.getenv(...)`) is done
3. There is no default value

Read the docstring on `EnvParser.add_variable` to see all available options. 
Below is an example of a non-required boolean variable with a default value:

```python
import envargs

def do_throttling(acceptor_throttling: bool):
    ...

env_parser = envargs.EnvParser()
env_parser.add_variable("ACCEPTOR_THROTTLING", type=bool, required=False, 
                        default=False)
ns = env_parser.parse_env()

do_throttling(ns.acceptor_throttling)
```
The above will attempt to find the environment variable 
`ACCEPTOR_THROTTLING` and if it doesn't exist, fall back on `False` as a 
default value. The namespace returned by `parse_env` will therefore always 
be populated with the `acceptor_throttling` property.

An optional environment variable that isn't present at the time of calling 
`parse_env` will still yield an attribute in the returmed namespace, set to 
`None`.

```python
import envargs

env_parser = envargs.EnvParser()
env_parser.add_variable("OPTIONAL_SETTING", required=False)
namespace = env_parser.parse_env()

# Will not raise an assertion error
assert namespace.optional_setting is None
```

### Parsing booleans
To simplify things for this library, booleans can be expressed in only a few 
selected ways:
```python
TRUTH_SET = {"true", "True", "1"}
FALSE_SET = {"false", "False", "0"}
```
These definitions are available at `envargs.envargs.TRUTH_SET/FALSE_SET`. 
Deviating from these values for a boolean variable will result in a 
`ParseError`:

```python
import envargs
import os

from envargs.errors import ParseError

SYSTEM_ONLINE = "SYSTEM_ONLINE"

# Set the env var to something other than what's defined in the 
# TRUTH_SET/FALSE_SET
os.environ[SYSTEM_ONLINE] = "YES"

env_parser = envargs.EnvParser()
env_parser.add_variable(SYSTEM_ONLINE, type=bool)

# This statement raises a ParseError
try:
    env_parser.parse_env()
except ParseError as e:
    print(e)
```
