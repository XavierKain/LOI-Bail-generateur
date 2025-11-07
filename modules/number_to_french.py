"""
Module de conversion de nombres en mots français.
Utilisé pour les montants "en lettres" dans les documents BAIL.
"""

def number_to_french_words(number: float) -> str:
    """
    Convertit un nombre en mots français.

    Args:
        number: Nombre à convertir (peut être float ou int)

    Returns:
        Représentation en mots français en MAJUSCULES

    Examples:
        5000 -> "CINQ MILLE"
        160000 -> "CENT SOIXANTE MILLE"
        40000 -> "QUARANTE MILLE"
    """
    # Arrondir à l'entier le plus proche pour les montants
    n = int(round(number))

    if n == 0:
        return "ZÉRO"

    if n < 0:
        return "MOINS " + number_to_french_words(abs(n))

    # Tableaux de conversion
    ones = ["", "UN", "DEUX", "TROIS", "QUATRE", "CINQ", "SIX", "SEPT", "HUIT", "NEUF"]
    teens = ["DIX", "ONZE", "DOUZE", "TREIZE", "QUATORZE", "QUINZE", "SEIZE",
             "DIX-SEPT", "DIX-HUIT", "DIX-NEUF"]
    tens = ["", "DIX", "VINGT", "TRENTE", "QUARANTE", "CINQUANTE",
            "SOIXANTE", "SOIXANTE", "QUATRE-VINGT", "QUATRE-VINGT"]

    def convert_below_thousand(n: int) -> str:
        """Convertit un nombre < 1000."""
        if n == 0:
            return ""
        elif n < 10:
            return ones[n]
        elif n < 20:
            return teens[n - 10]
        elif n < 100:
            tens_digit = n // 10
            ones_digit = n % 10

            if tens_digit == 7:  # 70-79
                return "SOIXANTE-" + teens[ones_digit]
            elif tens_digit == 9:  # 90-99
                return "QUATRE-VINGT-" + teens[ones_digit]
            elif tens_digit == 8 and ones_digit == 0:  # 80
                return "QUATRE-VINGTS"
            elif tens_digit == 8:  # 81-89
                return "QUATRE-VINGT-" + ones[ones_digit]
            else:
                if ones_digit == 0:
                    return tens[tens_digit]
                elif ones_digit == 1 and tens_digit != 8:
                    return tens[tens_digit] + " ET " + ones[ones_digit]
                else:
                    return tens[tens_digit] + "-" + ones[ones_digit]
        else:  # 100-999
            hundreds = n // 100
            rest = n % 100

            if hundreds == 1:
                result = "CENT"
            else:
                result = ones[hundreds] + " CENT"
                if rest == 0:
                    result += "S"

            if rest > 0:
                result += " " + convert_below_thousand(rest)

            return result

    def convert_with_scale(n: int) -> str:
        """Convertit un nombre complet avec milliers, millions, etc."""
        if n < 1000:
            return convert_below_thousand(n)

        result = []

        # Millions
        if n >= 1000000:
            millions = n // 1000000
            if millions == 1:
                result.append("UN MILLION")
            else:
                result.append(convert_below_thousand(millions) + " MILLIONS")
            n = n % 1000000

        # Milliers
        if n >= 1000:
            thousands = n // 1000
            if thousands == 1:
                result.append("MILLE")
            else:
                result.append(convert_below_thousand(thousands) + " MILLE")
            n = n % 1000

        # Unités
        if n > 0:
            result.append(convert_below_thousand(n))

        return " ".join(result)

    return convert_with_scale(n)


def format_amount_with_words(amount: float, currency: str = "EUROS", add_space: bool = True) -> str:
    """
    Formate un montant avec sa représentation en lettres.

    Args:
        amount: Montant numérique
        currency: Devise (défaut: "EUROS")
        add_space: Ajouter un espace avant la devise (défaut: True)

    Returns:
        Montant formaté selon le modèle BAIL

    Example:
        160000 -> "CENT SOIXANTE MILLE EUROS"
        40000 -> "QUARANTE MILLE EUROS"
    """
    words = number_to_french_words(amount)

    # Gérer le singulier/pluriel pour "euro"
    if amount == 1:
        currency = "EURO"

    if add_space:
        return f"{words} {currency}"
    else:
        return f"{words}{currency}"
