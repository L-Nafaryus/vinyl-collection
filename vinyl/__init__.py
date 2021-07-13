import discogs_client
#import pylatex
import logging
from dotenv import dotenv_values
import os
import jinja2

logging.basicConfig(
    level = logging.INFO,
    format = "%(levelname)s: %(message)s",
    handlers = [
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("vinyl")

def setupEnvValues():
    ROOT = os.path.abspath(".")
    BUILD = os.path.join(ROOT, "build")
    LOG = os.path.join(ROOT, "logs")

    env = {
        "ROOT": ROOT,
        "BUILD": BUILD,
        "LOG": LOG,
        "VINYL_DB": os.path.join(BUILD, "vinyl.db"),
        "VINYL_PDF": os.path.join(BUILD, "vinyl.pdf")
    }

    envfile = os.path.join(ROOT, ".env")

    if os.path.exists(envfile):
        env.update(dotenv_values(envfile))

    return env

def setupClient():
    if "TOKEN" in ENV.keys():
        client = discogs_client.Client(
            "vinyl-collection/1.0",
            consumer_key = ENV["CONSUMER_KEY"],
            consumer_secret = ENV["CONSUMER_SECRET"],
            token = ENV["TOKEN"],
            secret = ENV["SECRET"]
        )

        logger.info("Using client with OAuth")

    else:
        client = discogs_client.Client("vinyl-collection/1.0")

        logger.info("Using naked client")

    return client

def receive(user: str, overwrite = False):
    try:
        u = client.user(user)

    except Exception as e:
        logger.error(e)
        exit(1)

    clearline = "\033[A"
    stats = [0, 0, 0]

    releases = u.collection_folders[0].releases
    count = len(releases)

    logging.info(f"Found { count } releases")

    if not count:
        logging.info("Exiting ..")
        exit(1)

    for n, r in enumerate(releases):
        release = r.release
        release_id = r.id
        master = release.master
        master_id = None

        if master is not None:
            master_id = master.id
            query = Master.select().where(Master.master_id == master_id)
            
            if not query.exists():
                Master.create(
                    master_id = master_id,
                    year = master.main_release.year,
                    url = master.url
                )

            elif overwrite:
                Master.update(
                    master_id = master_id,
                    year = master.main_release.year,
                    url = master.url
                )

        query = Release.select().where(Release.release_id == release_id)

        if not query.exists():
            Release.create(
                release_id = r.id,
                artist = release.artists[0].name,
                country = release.country,
                title = release.title,
                year = release.year,
                master = master_id,
                url = release.url
            )
            stats[0] += 1
        
        elif overwrite:
            Release.update(
                release_id = r.id,
                artist = release.artists[0].name,
                country = release.country,
                title = release.title,
                year = release.year,
                master = master_id,
                url = release.url
            )
            stats[1] += 1

        else:
            stats[2] += 1

        logging.info(f"Received { n + 1 } from { count } ( { stats[0] } added, { stats[1] } updated, { stats[2] } skipped) { clearline }")

    logging.info("Done.")

def latexTemplate(name: str):
    env = jinja2.Environment(
        block_start_string = "\BLOCK{",
        block_end_string = "}",
        variable_start_string = "\VAR{",
        variable_end_string = "}",
        trim_blocks = True,
        autoescape = False,
        loader = jinja2.FileSystemLoader(os.path.join(ENV["ROOT"], "vinyl/templates"))
    )

    return env.get_template(name)

def topdf():
    template = latexTemplate("vinyl.tex")
    releases = list(Release.select().dicts())
    masters = list(Master.select().dicts())
    items = []

    for n, release in enumerate(releases):
        year_filter = list(filter(lambda o: o["master_id"] == release["master_id"], masters))
        
        items.append({
            "id": n,
            "artist": release.artist,
            "year": year_filter[0] if year_filter else release["year"],
            "title": release.title
        })
    
    tex = template.render(items)

    return tex
        

    

def main():
    ENV = setupEnvValues() 

    from vinyl.db import db, Master, Release
    db.create_tables([Master, Release])

    client = setupClient()

#__all__ = ["logger", "client"]
