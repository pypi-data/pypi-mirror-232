from typing import Dict


def sanitize(hub, raw_cli: Dict[str, Dict], opt: Dict) -> bool:
    """
    Perform bulletproofing and sanitization of arguments

    If this function grows any larger it should be broken into a subsystem
    """
    for dyne, config in opt.items():
        for option, final_value in config.items():
            if option not in raw_cli:
                continue

            option_cli_config = raw_cli[option]

            # If the CLI_CONFIG specifies "choices" for the option,
            # ensure that the final value chosen for this option is one of them
            if "choices" in option_cli_config:
                choices = option_cli_config["choices"]
                # Cast the final value to a string to check it against choices
                if final_value not in choices:
                    raise ValueError(
                        f"invalid choice: {repr(final_value)} (choose from {', '.join(map(repr, choices))})"
                    )

    return True
