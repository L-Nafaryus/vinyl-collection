from vinyl.db import db, Master, Release
import discogs_client
#import pylatex
import logging
from dotenv import dotenv_values

logging.basicConfig(
    level = logging.INFO,
    format = "%(levelname)s: %(message)s",
    handlers = [
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("vinyl")

ENV = dotenv_values(".env")


class Collection:
    def __init__(self):
        self.db = db
        db.create_tables([Master, Release])

        self.client = self._client()

    def _client(self):
        if "TOKEN" in ENV.keys():
            client = discogs_client.Client(
                "vinyl-collection/1.0",
                consumer_key = ENV["CONSUMER_KEY"],
                consumer_secret = ENV["CONSUMER_SECRET"],
                token = ENV["TOKEN"],
                secret = ENV["SECRET"]
            )

        else:
            client = discogs_client.Client("vinyl-collection/1.0")

        return client

    def receive(self, user: str, overwrite = False):
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

            logging.info(f"Received { n + 1 } from { count } ({ stats[0] } added, { stats[1] } updated, { stats[2] } skipped) { clearline }")

        logging.info("Done.")

    def toPDF(self):
        releases = list(Release.select().dicts())
        data = {}

        doc = pylatex.Document(
            page_numbers = True, 
            geometry_options = {
                "left": "2cm",
                "right": "2cm",
                "top": "0.5cm",
                "bottom": "1.5cm"
            }
        )

        header = pylatex.PageStyle("header")
        
        with header.create(pylatex.Foot("R")):
            header.append(pylatex.simple_page_number())
        
        doc.preamble.append(header)
        doc.change_document_style("header")

        with doc.create(pylatex.LongTable("l l l l")) as table:
            table.add_hline()
            table.add_row(["ID", "Artist", "Year", "Title"])
            table.add_hline()
            table.end_table_header()

            table.add_hline()
            table.end_table_footer()

            table.add_hline()
            table.end_table_last_footer()
            
            buf = data[0]["artist"]
            for n in range(len(data)):
                if buf != data[n]["artist"]:
                    table.add_hline()

                table.add_row([str(n + 1), data[n]["artist"], data[n]["year"], data[n]["title"]])
                buf = data[n]["artist"]

        doc.generate_tex(os.path.join(buildpath, "collection"))

