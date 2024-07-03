def get_years_ukrainian(age):
    if 11 <= age % 100 <= 14:
        return f"{age} років"
    else:
        last_digit = age % 10
        if last_digit == 1:
            return f"{age} рік"
        elif last_digit in [2, 3, 4]:
            return f"{age} роки"
        else:
            return f"{age} років"


def get_days_ukrainian(days):
    if 11 <= days % 100 <= 14:
        return f"{days} днів"
    else:
        last_digit = days % 10
        if last_digit == 1:
            return f"{days} день"
        elif last_digit in [2, 3, 4]:
            return f"{days} дні"
        else:
            return f"{days} днів"
