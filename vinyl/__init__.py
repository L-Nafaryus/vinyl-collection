import discogs_client
import logging
import os
import toml

logging.basicConfig(
    level = logging.INFO,
    format = "%(levelname)s: %(message)s",
    handlers = [
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("vinyl")

from vinyl.models import db, Master, Release
from vinyl.utils import latexTemplate, latexmk

env = { "ROOT": os.path.abspath(".") }
env.update({
    "BUILD": os.path.join(env["ROOT"], "build"),
    "LOG": os.path.join(env["ROOT"], "logs"),
    "CONFIG": os.path.join(env["ROOT"], "config.toml")
})
env["db_path"] = os.path.join(env["BUILD"], "vinyl.db")
env["pdf_path"] = env["BUILD"] 
env["pdf_template"] = os.path.join(env["ROOT"], "vinyl/templates/vinyl.tex")

if os.path.exists(env["CONFIG"]):
    config = toml.load(env["CONFIG"])

    for restricted in ["BUILD", "LOG", "CONFIG"]:
        if config.get(restricted):
            config.pop(restricted)

    env.update(config)


class Collection(object):
    def __init__(self):
        if not os.path.exists(env["BUILD"]):
            os.mkdir(env["BUILD"])

        if not os.path.exists(env["LOG"]):
            os.mkdir(env["LOG"])

        self.db = self._setupDB()
        self.client = self._setupClient()

    def _setupClient(self):
        if "discogs_token" in env.keys():
            client = discogs_client.Client(
                "vinyl-collection/1.0",
                consumer_key = env["consumer_key"],
                consumer_secret = env["consumer_secret"],
                token = env["discogs_token"],
                secret = env["discogs_secret"]
            )

        else:
            client = discogs_client.Client("vinyl-collection/1.0")

        return client

    def _setupDB(self):
        db.init(env["db_path"])

        if not os.path.exists(env["db_path"]):
            db.create_tables([Master, Release])

        return db


    def pull(self, user: str, overwrite: bool = False):
        try:
            u = self.client.user(user)

        except Exception as e:
            logger.error(e)
            exit(1)

        clearline = "\033[A"
        stats = [0, 0, 0]

        releases = u.collection_folders[0].releases
        count = len(releases)

        logger.info(f"Found { count } releases")

        if not count:
            logger.info("No one release was found. Exiting ..")
            exit(1)

        for n, r in enumerate(releases):
            release = r.release
            release_id = r.id
            master = release.master
            master_id = master.id if master else None
            
            if master:
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
                    master_id = master_id,
                    url = release.url
                )

                stats[0] += 1
                logger.info(f"Added release { r.id } with master { master_id }")

            elif overwrite:
                Release.update(
                    release_id = r.id,
                    artist = release.artists[0].name,
                    country = release.country,
                    title = release.title,
                    year = release.year,
                    master_id = master_id,
                    url = release.url
                )

                stats[1] += 1
                logger.info(f"Updated release { r.id } with master { master_id }")

            else:
                stats[2] += 1

        logger.info(f"Summary: { stats[0] } added, { stats[1] } updated, { stats[2] } skipped")
        logger.info("Done.")

    def topdf(self):
        template = latexTemplate(env["pdf_template"])
        releases = list(Release.select().dicts())
        masters = list(Master.select().dicts())
        items = []

        for n, release in enumerate(releases):
            year_filter = list(filter(lambda o: o["master_id"] == release["master_id"], masters))
            
            items.append({
                "artist": release["artist"].replace("&", "\&"),
                "year": year_filter[0]["year"] if year_filter else release["year"],
                "title": release["title"].replace("&", "\&")
            })

        items = sorted(items, key = lambda item: f"{ item['artist'] } { item['year'] } { item['title'] }")
        
        for n, item in enumerate(items):
            item["id"] = n

        renderpath = os.path.join(env["BUILD"], "vinyl-collection.tex")

        with open(renderpath, "w") as io:
            io.write(template.render(items = items))
        
        latexmk(renderpath, env["pdf_path"])

