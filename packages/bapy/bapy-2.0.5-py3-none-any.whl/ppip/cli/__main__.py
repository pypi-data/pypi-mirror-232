import typer

app = typer.Typer(add_completion=False, context_settings={'help_option_names': ['-h', '--help']},
                  name="ppip")

try:
    typer.Exit(app())
except KeyboardInterrupt:
    print('Aborted!')
    typer.Exit(1)
