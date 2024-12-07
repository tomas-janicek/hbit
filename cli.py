import os

import typer
from langchain_core.globals import set_debug, set_llm_cache, set_verbose
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

cli = typer.Typer()


@cli.command(name="translate_text_to")
def translate_text_to(language: str, text: str, debug: bool = False) -> None:
    set_verbose(True)
    set_debug(debug)
    set_llm_cache(None)

    model = ChatGroq(model="llama3-8b-8192")  # type: ignore

    system_template = "Translate the following from English into {language}"

    prompt_template = ChatPromptTemplate.from_messages(
        [("system", system_template), ("user", "{text}")]
    )
    prompt = prompt_template.invoke({"language": language, "text": text})

    response = model.invoke(prompt)
    print(response.content)


@cli.command(name="get_recommended_num_workers")
def get_recommended_num_workers() -> None:
    max_workers = min(32, (os.cpu_count() or 1))
    print(f"Recommendation for max number of workers is {max_workers}. ")


if __name__ == "__main__":
    cli()
