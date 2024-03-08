from Exceptions import *
from CommandProcessor import CommandProcessor
from ExploitProcessor import ExploitProcessor
from PHPExploitProcessor import PHPExploitProcessor

class LocalCommandProcessor(CommandProcessor):
    def __init__(self):
        super().__init__()

        self.commands["exploit"] = { 
                "method": self.__exploit,
                "description": ("Start the exploit, "
                    "given the preconditions are met.")
            }
        
        self.commands["set"] = {
                "method": self.__set,
                "description": "Set or display exploit variables."
            }
            
        # exploit variables
        self.variables = {
            "TARGET_HOST": {"value": "", "required": True},
            "TARGET_PATH": {"value": "/", "required": True},
            "TARGET_TYPE": {"value": "PHP", "required": True},
            "METHOD": {"value": "GET", "required": True},
            "HEADER": {"value": "EXPLOIT", "required": True}
        }

        self.exploit: ExploitProcessor = None
        
    """
    @brief exploit the target machine.
    @param options Not used.
    @pre the required exploit variables have been set, and are valid.
    @throw CommandException if the pre-condition is not met.
    """
    def __exploit(self, options: str):
        if self.exploit_status() == True:
            raise CommandException("Already exploited target.")
        for var in self.variables:
            if (self.variables[var]["required"] and
                len(self.variables[var]["value"]) == 0):
                raise CommandException(f"{var} not set.")
        print((f"Attempting to exploit "
               f"{self.variables['TARGET_HOST']['value']} "
               f"at {self.variables['TARGET_PATH']['value']}"))
        
        self.exploit = (
            PHPExploitProcessor(self.variables['TARGET_HOST']['value'],
                             self.variables['TARGET_PATH']['value'],
                             self.variables['METHOD']['value'],
                             self.variables['HEADER']['value']))
        
    """
    @brief Command to set and display exploit variables.
    @param options the variable to be set and the value, if any.
    @throw CommandException if the variable does not exist, or if the value is
            invalid.
    """
    def __set(self, options: str):
        if len(options) == 0:  # list all variables
            print((f"{'{0: <20}'.format(f'VARIABLE')} "
                   f"{'{0: <50}'.format('VALUE')} "
                   f"REQUIRED"))
            for var in self.variables:
                print((f"{'{0: <20}'.format(var)} "
                       f"{'{0: <50}'.format(self.variables[var]['value'])} "
                       f"{str(self.variables[var]['required']).upper()}"))
        else:
            split = options.split(" ", 1)
            var = split[0].upper()
            if var in self.variables:
                value = ""
                if len(split) > 1:
                    value = split[1]
                self.variables[var]["value"] = value
                print(f"'{var}' set to '{value}'")
            else:
                raise CommandException(f"'{var}' is not a variable.")

    """
    @brief Getter for exploit status (True or False)
    @return bool for if we are in the exploit shell.
    """
    def exploit_status(self):
        return self.exploit is not None
    
    """
    @brief Processes a command string.
    @param command a string representing the whole command to be processed.
    @pre \p command is a valid command to be ran.
    @pre \p command has its preconditions met. 
    @throw CommandException if the command doesn't exist.
    """
    def process_command(self, command: str):
        if self.exploit_status():
            try:
                self.exploit.process_command(command)
            except ExitException:
                self.exploit = None
                print("Disconnected from exploit shell.")
        else:
            super().process_command(command)
    