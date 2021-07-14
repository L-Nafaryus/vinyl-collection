import os
import jinja2
import logging
import subprocess

def latexTemplate(filepath: str):
    splitted = filepath.split("/")
    file = splitted[-1]
    directory = "/".join(splitted[ :-1])

    env = jinja2.Environment(
        block_start_string = "\BLOCK{",
        block_end_string = "}",
        variable_start_string = "\VAR{",
        variable_end_string = "}",
        trim_blocks = True,
        autoescape = False,
        loader = jinja2.FileSystemLoader(directory)
    )

    return env.get_template(file)

def latexmk(filepath: str, outdir: str):
    cmd = [
        "pdflatex", 
        "-interaction=nonstopmode", 
        "-shell-escape",
        "-output-format=pdf",
        f"-output-directory={ outdir }",
        filepath, 
    ]

    try:
        with subprocess.Popen(cmd) as p:
            out, err = p.communicate()

            if err:
                logging.error(str(err, "utf-8"))

    except OSError as e:
        logging.error(e)

