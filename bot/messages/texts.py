class TextFactory:
    _L = f"\n+---+{'-' * 41}+"
    _E = "\n|   |"
    _I = "\n| i |"
    _Q = "\n| ? |"
    _1 = "\n| 1 |"
    _2 = "\n| 2 |"
    _3 = "\n| 3 |"
    _4 = "\n| 4 |"

    @classmethod
    def _draw(cls, parts: list[str], text: str, footer: str) -> None:
        used = 0

        for word in text.split():
            if used + len(word) > 39:
                parts.append(f"{' ' * (40 - used)}|{cls._E}")
                used = 0

            parts.append(word)
            used += len(word) + 1

        parts.append(f"{' ' * (40 - used)}|{cls._L}{footer}")

    @classmethod
    def for_task(cls, step: str, question: str, option1: str, option2: str, option3: str, option4: str) -> str:
        parts = [f"{cls._L}{cls._I} {step.ljust(40)}|{cls._L}\n{cls._L}{cls._Q}"]

        cls._draw(parts, question, f"\n{cls._L}{cls._1}")
        cls._draw(parts, option1, cls._2)
        cls._draw(parts, option2, cls._3)
        cls._draw(parts, option3, cls._4)
        cls._draw(parts, option4, "")

        return " ".join(parts)
