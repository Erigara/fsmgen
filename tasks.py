import os
from pathlib import Path

from pylatex import (
    Document,
    Section,
    Subsection,
    Figure,
    Package,
)
from pylatex.base_classes import Options, CommandBase, Arguments


class Listing(CommandBase):
    """
    Environment for adding listings.
    """

    _latex_name = "inputpython"
    packages = [Package("pythonhighlight")]


if __name__ == "__main__":
    image_filename = os.path.join("tasks", "shanin1000@yandex.ru")

    geometry_options = {"tmargin": "1cm", "lmargin": "2cm"}
    doc = Document(geometry_options=geometry_options)

    doc.packages.append(Package("babel", options=Options("russian")))
    doc.packages.append(Package("float"))

    with doc.create(Section("Задача: реализуйте конечный автомат.", numbering=False)):
        for variant in sorted(Path("tasks").glob("*"), key=lambda path: int(path.stem)):
            with doc.create(Subsection(f"Вариант: {variant.stem}", numbering=False)):
                with open("payload.txt") as payload:
                    for line in payload:
                        doc.append(line)

                with doc.create(
                    Subsection(f"Схема конечного автомата:", numbering=False)
                ):
                    with doc.create(Figure(position="H")) as pic:
                        pic.add_image(str(variant.joinpath("fsm.png")), width="200px")

                with doc.create(Subsection(f"Примеры выполнения:", numbering=False)):
                    for path in variant.glob("path*.txt"):
                        doc.append(
                            Listing(
                                arguments=Arguments(str(path), 0, 5),
                            )
                        )
    doc.generate_pdf("tasks", clean_tex=False)
