# zadanie 1
def greet(name: str, surname: str) -> str:
    return f"Cześć {name} {surname}!"

greeting = greet("Jan", "Kowalski")
print(greeting)


# zadanie 2
def multiply(a: int, b: int) -> int:
    return a * b


# zadanie 3
def is_even(number: int) -> bool:
    return number % 2 == 0

check = is_even(4)
if check:
    print("Liczba parzysta")
else:
    print("Liczba nieparzysta")


# zadanie 4
def check_sum(a: int, b: int, c: int) -> bool:
    return a + b >= c


# zadanie 5
def contains_number(numbers: list, target: int) -> bool:
    return target in numbers


# zadanie 6
def process_lists(list1: list, list2: list) -> list:
    unique_elements = set(list1 + list2)
    return [x**3 for x in unique_elements]


# zadanie 7
import requests
from typing import Optional


class Brewery:
    def __init__(
        self,
        id: str,
        name: str,
        brewery_type: str,
        address_1: Optional[str] = None,
        address_2: Optional[str] = None,
        address_3: Optional[str] = None,
        city: Optional[str] = None,
        state_province: Optional[str] = None,
        postal_code: Optional[str] = None,
        country: Optional[str] = None,
        longitude: Optional[str] = None,
        latitude: Optional[str] = None,
        phone: Optional[str] = None,
        website_url: Optional[str] = None,
        state: Optional[str] = None,
        street: Optional[str] = None,
    ):
        self.id: str = id
        self.name: str = name
        self.brewery_type: str = brewery_type
        self.address_1: Optional[str] = address_1
        self.address_2: Optional[str] = address_2
        self.address_3: Optional[str] = address_3
        self.city: Optional[str] = city
        self.state_province: Optional[str] = state_province
        self.postal_code: Optional[str] = postal_code
        self.country: Optional[str] = country
        self.longitude: Optional[str] = longitude
        self.latitude: Optional[str] = latitude
        self.phone: Optional[str] = phone
        self.website_url: Optional[str] = website_url
        self.state: Optional[str] = state
        self.street: Optional[str] = street

    def __str__(self) -> str:
        return f"{self.name} ({self.brewery_type}) - {self.city}, {self.country}"


response = requests.get(
    "https://api.openbrewerydb.org/v1/breweries", params={"per_page": 20}
)
data = response.json()

breweries = [Brewery(**item) for item in data]
for brewery in breweries:
    print(brewery)

# zadanie 8
import argparse
import requests
from typing import Optional


class Brewery:
    def __init__(
        self,
        id: str,
        name: str,
        brewery_type: str,
        address_1: Optional[str] = None,
        address_2: Optional[str] = None,
        address_3: Optional[str] = None,
        city: Optional[str] = None,
        state_province: Optional[str] = None,
        postal_code: Optional[str] = None,
        country: Optional[str] = None,
        longitude: Optional[str] = None,
        latitude: Optional[str] = None,
        phone: Optional[str] = None,
        website_url: Optional[str] = None,
        state: Optional[str] = None,
        street: Optional[str] = None,
    ):
        self.id: str = id
        self.name: str = name
        self.brewery_type: str = brewery_type
        self.address_1: Optional[str] = address_1
        self.address_2: Optional[str] = address_2
        self.address_3: Optional[str] = address_3
        self.city: Optional[str] = city
        self.state_province: Optional[str] = state_province
        self.postal_code: Optional[str] = postal_code
        self.country: Optional[str] = country
        self.longitude: Optional[str] = longitude
        self.latitude: Optional[str] = latitude
        self.phone: Optional[str] = phone
        self.website_url: Optional[str] = website_url
        self.state: Optional[str] = state
        self.street: Optional[str] = street

    def __str__(self) -> str:
        return f"{self.name} ({self.brewery_type}) - {self.city}, {self.country}"


parser = argparse.ArgumentParser()
parser.add_argument("--city", type=str, default=None)
args = parser.parse_args()

params = {"per_page": 20}
if args.city:
    params["by_city"] = args.city

response = requests.get(
    "https://api.openbrewerydb.org/v1/breweries", params=params
)
data = response.json()

breweries = [Brewery(**item) for item in data]
for brewery in breweries:
    print(brewery)