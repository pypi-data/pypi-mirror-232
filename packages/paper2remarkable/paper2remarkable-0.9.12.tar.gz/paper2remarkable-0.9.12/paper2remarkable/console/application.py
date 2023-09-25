# -*- coding: utf-8 -*-

from wilderness import Application

from paper2remarkable.__version__ import __version__

DOCS = {
    "description": (
        "Fetch an academic paper, local pdf file, or any web article and send "
        "it to the reMarkable tablet. The input to the script can be a URL to "
        "a PDF file or article on a website, or a local file. For supported "
        "scientific outlets, the program will collect the metadata for the "
        "paper and create a nice filename (unless --filename is "
        "specified). See [SUPPORTED SOURCES](#supported-sources) for an "
        "overview of supported scientific paper sources.By default, "
        "paper2remarkable crops the unnecessary whitespace from a PDF file to "
        "make the paper fit better on the reMarkable. The default setting "
        "yields a left-aligned document on the reMarkable which can be useful "
        "for taking margin notes. Alternatively, the program supports the "
        "--center, --right, and --no-crop options to change this "
        "crop setting."
    )
}


class Paper2RemarkableApplication(Application):
    def __init__(self):
        super().__init__(
            "p2r",
            version=__version__,
            title="Fetch an academic paper or web article and send it to the reMarkable tablet with a single command",
            author="Gertjan van den Burg",
            description=DOCS["description"],
            extra_sections=DOCS["extra"],
        )

    def register(self):
        self.add_argument(
            "-v",
            "--verbose",
            help="Enable verbose mode",
            action="store_true",
        )
        self.add_argument(
            "-V",
            "--version",
            help="Show version and exit",
            action="version",
            version=__version__,
        )
        self.add_argument(
            "-e",
            "--experimental",
            help="Enable experimental features of paper2remarkable",
            action="store_true",
            description=(
                "Enable the experimental features of paper2remarkable. See "
                "below under EXPERIMENTAL FEATURES for an overview."
            ),
        )
