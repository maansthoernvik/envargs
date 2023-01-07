# envargs

`envargs` gives you an easy way of specifying which environment variables to
look for as program arguments/config. This library aims at providing an as 
similar as possible experience to that of using Python's `argparse` package.

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
case. Variable `NUM_WORKERS` thus gets the field name `namespace.
num_workers`.

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
