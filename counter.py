from collections import Counter, defaultdict, namedtuple
from os import listdir
from re import search

from docx import Document


def func(file: str) -> None:
    doc = Document(f"documents/{file}")
    results, tables = defaultdict(list), []

    for table in doc.tables:
        cells = [
            Cell(i, j, cell.text.replace("\n", "->"))
            for i, row in enumerate(table.rows)
            for j, cell in enumerate(row.cells)
        ]

        multipliers = {
            cell.row: (len([s for s in cell.text if s.isdecimal()]) + 2) // 4
            for cell in cells
            if not cell.column
        }

        groups = {
            cell.text: cell for cell in cells if search(r"(?i)гр\. [оз]ф", cell.text)
        }.values()

        for group in groups:
            results[group.text].extend(
                [
                    f'"{cell.text}"'
                    for cell in cells
                    if all(
                        [
                            cell.column == group.column,
                            cell.text.strip(),
                            cell.text != group.text,
                        ]
                    )
                    for _ in range(multipliers[cell.row])
                ]
            )

        table = defaultdict(dict)
        for cell in cells:
            table[cell.row][cell.column] = cell.text[:8].ljust(8)

        tables.append(
            "\n".join(f"{' | '.join(columns.values())}" for _, columns in table.items())
        )

    with open(f"counts/{file[:-5]}.txt", "w", encoding="utf-8") as file:
        for group, result in results.items():
            separator = "-" * len(group)
            file.write(f"{separator}\n{group}\n{separator}\n")
            for discipline, amount in sorted(Counter(result).items()):
                file.write(f"{discipline}: {amount}\n")
        separator = "-" * 19
        file.write(f"{separator}\nДанные для проверки\n{separator}\n")
        file.write("\n\n".join(tables))


if __name__ == "__main__":
    Cell = namedtuple("Cell", ["row", "column", "text"])
    files = [file for file in listdir("documents") if file.endswith(".docx")]

    for file in files:
        func(file)
