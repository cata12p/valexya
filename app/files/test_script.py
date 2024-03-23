from datetime import datetime, timedelta

def get_dates_range(date_type):
    # Obține data curentă
    today = datetime.now()

    if date_type == 'week':
        # Calculează ziua săptămânii (0 - Luni, 1 - Marți, ..., 6 - Duminică)
        day_of_week = today.weekday()

        # Calculează data de la începutul săptămânii (Luni)
        start_date = today - timedelta(days=day_of_week)
        # Calculează data de la sfârșitul săptămânii (Duminică)
        end_date = start_date + timedelta(days=6)

    elif date_type == 'month':
        # Calculează data de la începutul lunii
        start_date = today.replace(day=1)
        # Calculează data de la sfârșitul lunii
        next_month = today.replace(day=28) + timedelta(days=4)  # Adaugăm 4 zile pentru a fi siguri că suntem în luna următoare
        end_date = next_month - timedelta(days=next_month.day)

    elif date_type == 'year':
        # Calculează data de la începutul anului
        start_date = today.replace(month=1, day=1)
        # Calculează data de la sfârșitul anului
        end_date = today.replace(month=12, day=31)

    else:
        raise ValueError("Tip de data invalid")

    return start_date, end_date

# Testează funcția
date_types = ['week', 'month', 'year']

for date_type in date_types:
    start_date, end_date = get_dates_range(date_type)
    print(f"Data de la începutul {date_type} curent:", start_date.date())
    print(f"Data de la sfârșitul {date_type} curent:", end_date.date())