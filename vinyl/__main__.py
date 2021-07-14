from vinyl import Collection
import click

pass_collection = click.make_pass_decorator(Collection)

@click.group()
@click.pass_context
def vinyl(ctx):
    ctx.obj = Collection()

@vinyl.command(short_help = "Pull collection from discogs")
@click.argument("user")
@click.option("--overwrite", default = False, help = "Overwrite entries in local db")
@pass_collection
def pull(collection, user, overwrite):
    collection.pull(user, overwrite)

@vinyl.command(short_help = "Export collection to some format")
@click.option("--fmt", required = True, type = click.Choice(["pdf"]), help = "Specify export format")
@pass_collection
def export(collection, fmt):
    if fmt == "pdf":
        collection.topdf()

vinyl()
