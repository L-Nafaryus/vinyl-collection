from vinyl import db, Release, Master
import discogs_client
import pylatex
import logging

logger = logging.getLogger("vinyl")

db.create_tables([Release, Master])
client = discogs_client.Client("Vinyl/0.1")

clearline = "\033[A"

def receiveCollection(user: str, overwrite = True):
    try:
        u = client.user(user)

    except Exception as e:
        logger.error(e)
        exit(1)

    releases = u.collection_folders[0].releases
    count = len(releases)
    logging.info(f"Found { count } releases")

    if not count:
        logging.info("Exiting ..")
        exit(1)

    for n, r in enumerate(releases):
        release = r.release
        master = release.master

        m = Master.create(
            master_id = master.id,
            year = master.main_release.year,
            url = master.url
        )

        Release.create(
            release_id = r.id,
            artist = release.artists[0].name,
            country = release.country,
            title = release.title,
            year = release.year,
            master = m,
            url = release.url
        )
        
        logging.info(f"Received { n + 1 } from { count } { clearline }")

    logging.info("Done.")

def generatePDF():
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

