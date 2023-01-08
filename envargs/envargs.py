import os

from typing import Optional, Union

from envargs.errors import RequiredError, ParseError

# Used to decode boolean env vars, other values result in an error
TRUTH_SET = {"true", "True", "1"}
FALSE_SET = {"false", "False", "0"}


class Variable:
    """
    Variable == Environment variable including rules for if it's required, its
    data type, destination name and more. The options for a Variable's
    instantiation is similar to that of ArgumentParser.add_variable, the
    accepted options are directly taken from EnvParser.add_variable.
    """

    def __init__(self,
                 name: str,
                 var_type: type,
                 required: bool,
                 default: Union[str, int, float, bool],
                 dest: str):
        self.name: str = name
        self.var_type: type = var_type
        self.required: bool = required
        self.default: Union[str, int, float, bool] = default
        self.dest: str = dest

    def decode(self, env_var: str) -> Union[str, int, float, bool]:
        """
        Decode an environment variable value string using the Variable
        instance fields.
        :param env_var: environment variable string
        :raises: ParseError in case the string cannot be decoded into the
                 variable's data type
        :return: a decoded environment variable string
        """
        # String, no need to decode
        if self.var_type == str:
            return env_var

        if self.var_type == bool:
            if env_var in TRUTH_SET:
                return True
            elif env_var in FALSE_SET:
                return False
            else:
                raise ParseError(self.name, self.var_type, env_var)

        try:
            decoded = self.var_type(env_var)
        except ValueError:
            raise ParseError(self.name, self.var_type, env_var)

        return decoded

    def __str__(self):  # pragma: no cover
        return f"<Variable at {hex(id(self))}: name={self.name} var_type={self.var_type} required={self.required} default={self.default} dest={self.dest}>"  # noqa


class EnvParser:
    """
    EnvParser performs lookups on the local environment variables and compares
    the present variables to what the class instance was prepared with using
    'add_variable'. EnvParser draws inspiration from argparse.ArgumentParser,
    and it should be used in the same way. Of course, EnvParser does not have
    a concept of positional arguments as it parses variables and not arguments
    provided in a set order.
    """

    class Namespace:
        """
        Holds the result of parsing an environment, where each registered (and
        found) variable can be referenced by 'ns.env_var_name_in_lower_caps'.
        """

    def __init__(self):
        self.variables: list[Variable] = list()

    @property
    def description(self) -> str:
        """
        Generates a description based on all added variables (via
        add_variable).
        :return: a helpful description string
        """
        def default_text(default) -> str:
            return "" if default is None else f" default={default}"

        def required_text(required: bool) -> str:
            return " required" if required else ""

        # max_name_length = 0
        # for var in self.variables:
        #     var.name

        desc = "Environment variables: \n\n"
        for var in self.variables:
            desc += f"  {var.name} ({var.var_type.__name__}):{required_text(var.required)}{default_text(var.default)} dest={var.dest}\n"  # noqa

        return desc

    def add_variable(self,
                     name: str,
                     type: type = str,
                     required: bool = True,
                     default: Union[str, int, float, bool] = None,
                     dest: Optional[str] = None) -> None:
        """
        Add an environment variable to the parser that will be looked up and
        set in the namespace container returned by a future call to
        EnvParser.parse_env.

        :param name: name of the environment variable, used for os.getenv
        :param type: primitive type that the environment variable will be
                     decoded to
        :param required: if a required environment variable cannot be found,
                         a RequiredError is raised
        :param default: sets a default value to be used in case the
                        environment variable isn't present. A required variable
                        with a default value can not yield a RequiredError
        :param dest: field name on the namespace container returned by
                     EnvParser.parse_env. Defaults to the name parameter in
                     lower case
        :raises: TypeError if type and the default type do not match
        :return: None
        """
        EnvParser._type_check_default(name, type, default)

        self.variables.append(
            Variable(name,
                     type,
                     required,
                     default,
                     dest if dest is not None else name.lower())
        )

    def parse_env(self) -> Namespace:
        """
        Performs lookups for each registered variable via
        EnvParser.add_variable and decodes the gotten string(s) into the
        wanted data type. If a variable was not found and a default exists,
        then the default value is used.

        :raises: RequiredError in case a required variable isn't found and it
                 has no default value
        :return: Namespace container with fields for each registered
                 environment variable that could be found in the current
                 environment
        """
        ns = EnvParser.Namespace()
        for var in self.variables:
            # Fetch the variable and check required
            env_var = os.getenv(var.name)
            # Environment variable does not exist
            if env_var is None:
                # Check required and default
                if var.required and var.default is None:
                    # Required and no default, ERROR
                    raise RequiredError(var.name)
                elif var.default is not None:
                    # Regardless of if required or not, if there's a default,
                    # use it (since env var was None)
                    decoded_var = var.default
                else:
                    # If no default and not required, set decoded value to None
                    decoded_var = None
            else:
                # Decode string according to type
                decoded_var = var.decode(env_var)

            ns.__setattr__(var.dest, decoded_var)

        return ns

    @staticmethod
    def _type_check_default(name: str,
                            t: type,
                            default: Union[str, int, float, bool]) -> None:
        """
        Check the type of the input t and the default type, if they don't
        match a ValueError is raised.

        :param name: name of the environment variable checked
        :param t: the variable's type
        :param default: the default value of the variable
        :raises: TypeError if the default type and t do not match
        :return: None
        """
        if default is not None and t != type(default):
            raise TypeError(f"Cannot register variable '{name}' since the "
                            f"default value type does not match the "
                            f"variable's type")
