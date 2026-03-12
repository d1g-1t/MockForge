import random
import uuid
from datetime import datetime, timedelta

from faker import Faker

fake_ru = Faker("ru_RU")
fake_en = Faker("en_US")


class FakerEngine:
    FIELD_HEURISTICS: dict[str, callable] = {
        "name": lambda: fake_ru.name(),
        "first_name": lambda: fake_ru.first_name(),
        "last_name": lambda: fake_ru.last_name(),
        "email": lambda: fake_en.email(),
        "phone": lambda: fake_ru.phone_number(),
        "address": lambda: fake_ru.address(),
        "city": lambda: fake_ru.city(),
        "country": lambda: fake_ru.country(),
        "zip_code": lambda: fake_ru.postcode(),
        "postal_code": lambda: fake_ru.postcode(),
        "id": lambda: str(uuid.uuid4()),
        "user_id": lambda: str(uuid.uuid4()),
        "order_id": lambda: f"ORD-{random.randint(10000, 99999)}",
        "product_id": lambda: str(uuid.uuid4()),
        "price": lambda: round(random.uniform(100, 50000), 2),
        "amount": lambda: round(random.uniform(1000, 500000), 2),
        "total": lambda: round(random.uniform(100, 100000), 2),
        "currency": lambda: random.choice(["RUB", "USD", "EUR"]),
        "iban": lambda: fake_en.iban(),
        "card_number": lambda: fake_en.credit_card_number(),
        "created_at": lambda: datetime.now().isoformat(),
        "updated_at": lambda: datetime.now().isoformat(),
        "deleted_at": lambda: None,
        "birth_date": lambda: fake_ru.date_of_birth(minimum_age=18, maximum_age=80).isoformat(),
        "expires_at": lambda: (datetime.now() + timedelta(days=365)).isoformat(),
        "inn": lambda: fake_ru.numerify("##########"),
        "kpp": lambda: fake_ru.numerify("#########"),
        "ogrn": lambda: fake_ru.numerify("#############"),
        "case_number": lambda: f"А40-{random.randint(10000, 999999)}/{random.randint(2018, 2025)}",
        "court_name": lambda: random.choice([
            "Арбитражный суд г. Москвы",
            "Арбитражный суд г. Санкт-Петербурга",
            "Девятый арбитражный апелляционный суд",
        ]),
        "title": lambda: fake_ru.sentence(nb_words=4),
        "description": lambda: fake_ru.text(max_nb_chars=200),
        "comment": lambda: fake_ru.text(max_nb_chars=100),
        "url": lambda: fake_en.url(),
        "image_url": lambda: f"https://picsum.photos/seed/{random.randint(1, 1000)}/400/300",
        "avatar": lambda: f"https://i.pravatar.cc/150?u={uuid.uuid4()}",
        "status": lambda: random.choice(["active", "pending", "completed", "cancelled"]),
        "username": lambda: fake_en.user_name(),
        "password": lambda: fake_en.password(length=12),
        "token": lambda: fake_en.sha256(),
        "slug": lambda: fake_en.slug(),
        "count": lambda: random.randint(1, 100),
        "quantity": lambda: random.randint(1, 50),
        "page": lambda: random.randint(1, 10),
        "per_page": lambda: random.choice([10, 20, 50]),
        "total_pages": lambda: random.randint(1, 20),
    }

    def generate(self, schema: dict, field_name: str = "") -> object:
        if not schema:
            return {}

        enum_values = schema.get("enum")
        if enum_values:
            return random.choice(enum_values)

        const = schema.get("const")
        if const is not None:
            return const

        field_lower = field_name.lower()
        for key, generator in self.FIELD_HEURISTICS.items():
            if key == field_lower or field_lower.endswith(f"_{key}") or field_lower.startswith(f"{key}_"):
                return generator()

        schema_format = schema.get("format", "")
        schema_type = schema.get("type")

        match schema_format:
            case "uuid":
                return str(uuid.uuid4())
            case "date-time":
                return datetime.now().isoformat()
            case "date":
                return datetime.now().date().isoformat()
            case "time":
                return datetime.now().time().isoformat()
            case "email":
                return fake_en.email()
            case "uri" | "url":
                return fake_en.url()
            case "iban":
                return fake_en.iban()
            case "hostname":
                return fake_en.hostname()
            case "ipv4":
                return fake_en.ipv4()
            case "ipv6":
                return fake_en.ipv6()

        one_of = schema.get("oneOf") or schema.get("anyOf")
        if one_of:
            return self.generate(random.choice(one_of), field_name)

        all_of = schema.get("allOf")
        if all_of:
            merged: dict = {}
            for sub in all_of:
                result = self.generate(sub, field_name)
                if isinstance(result, dict):
                    merged.update(result)
            return merged

        match schema_type:
            case "object":
                return {
                    k: self.generate(v, field_name=k)
                    for k, v in schema.get("properties", {}).items()
                }
            case "array":
                count = random.randint(
                    schema.get("minItems", 1),
                    schema.get("maxItems", 5),
                )
                return [self.generate(schema.get("items", {})) for _ in range(count)]
            case "string":
                min_len = schema.get("minLength", 3)
                max_len = schema.get("maxLength", 50)
                pattern = schema.get("pattern")
                if pattern:
                    try:
                        from faker.providers.misc import Provider as MiscProvider
                        return fake_en.bothify(text="?" * min_len)
                    except Exception:
                        pass
                return fake_en.pystr(min_chars=min_len, max_chars=max_len)
            case "integer":
                return random.randint(
                    schema.get("minimum", 1),
                    schema.get("maximum", 10000),
                )
            case "number":
                return round(
                    random.uniform(
                        schema.get("minimum", 0.1),
                        schema.get("maximum", 9999.99),
                    ),
                    2,
                )
            case "boolean":
                return random.choice([True, False])
            case "null":
                return None
            case _:
                return None
