from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

app = FastAPI(title="Customer API", version="1.0.0")

class Customer(BaseModel):
    id: int
    email: EmailStr
    name: str
    dob: date


class Product(BaseModel):
    code: str
    name: str
    list_price: float
    buy_price: float
    date: date
    has_warranty: bool
    warranty_date: Optional[date] = None


# Mock database with sample customers
customers_db = [
    Customer(
        id=1,
        email="john.doe@example.com",
        name="John Doe",
        dob=date(1990, 5, 15)
    ),
    Customer(
        id=2,
        email="jane.smith@example.com",
        name="Jane Smith",
        dob=date(1985, 8, 22)
    ),
    Customer(
        id=3,
        email="bob.wilson@example.com",
        name="Bob Wilson",
        dob=date(1992, 3, 10)
    ),
]

# Mock database of products purchased by customers
customer_products_db = {
    1: [  # John Doe's purchases
        Product(
            code="LAP001",
            name="Dell XPS 15 Laptop",
            list_price=1899.99,
            buy_price=1699.99,
            date=date(2024, 1, 15),
            has_warranty=True,
            warranty_date=date(2027, 1, 15)
        ),
        Product(
            code="MOU002",
            name="Logitech MX Master 3",
            list_price=99.99,
            buy_price=89.99,
            date=date(2024, 2, 20),
            has_warranty=True,
            warranty_date=date(2025, 2, 20)
        ),
        Product(
            code="USB003",
            name="USB-C Hub Adapter",
            list_price=49.99,
            buy_price=39.99,
            date=date(2024, 3, 10),
            has_warranty=False,
            warranty_date=None
        ),
    ],
    2: [  # Jane Smith's purchases
        Product(
            code="PHO001",
            name="iPhone 15 Pro",
            list_price=1199.99,
            buy_price=1099.99,
            date=date(2024, 6, 5),
            has_warranty=True,
            warranty_date=date(2026, 6, 5)
        ),
        Product(
            code="CAB002",
            name="USB-C to Lightning Cable",
            list_price=29.99,
            buy_price=24.99,
            date=date(2024, 6, 5),
            has_warranty=False,
            warranty_date=None
        ),
    ],
    3: [  # Bob Wilson's purchases
        Product(
            code="TAB001",
            name="iPad Air",
            list_price=599.99,
            buy_price=549.99,
            date=date(2023, 11, 20),
            has_warranty=True,
            warranty_date=date(2024, 11, 20)
        ),
        Product(
            code="PEN001",
            name="Apple Pencil 2nd Gen",
            list_price=129.99,
            buy_price=119.99,
            date=date(2023, 11, 20),
            has_warranty=True,
            warranty_date=date(2024, 11, 20)
        ),
        Product(
            code="KEY001",
            name="Magic Keyboard",
            list_price=299.99,
            buy_price=279.99,
            date=date(2023, 12, 5),
            has_warranty=True,
            warranty_date=date(2024, 12, 5)
        ),
        Product(
            code="BAG001",
            name="Laptop Backpack",
            list_price=79.99,
            buy_price=59.99,
            date=date(2024, 1, 10),
            has_warranty=False,
            warranty_date=None
        ),
    ],
}


@app.get("/")
async def root():
    return {"message": "Customer API is running. Use /customer?email=<email> to get customer details."}


@app.get("/customer", response_model=Customer)
async def get_customer_by_email(email: EmailStr):
    """
    Get customer by email address.

    Args:
        email: Customer's email address

    Returns:
        Customer object with id, email, name, and dob

    Raises:
        HTTPException: 404 if customer not found
    """
    for customer in customers_db:
        if customer.email.lower() == email.lower():
            return customer

    raise HTTPException(
        status_code=404,
        detail=f"Customer with email '{email}' not found"
    )


@app.get("/customers", response_model=list[Customer])
async def get_all_customers():
    """Get all customers in the database."""
    return customers_db


@app.get("/customer/{customer_id}/products", response_model=list[Product])
async def get_customer_products(customer_id: int):
    """
    Get all products purchased by a customer.

    Args:
        customer_id: The ID of the customer

    Returns:
        List of Product objects purchased by the customer

    Raises:
        HTTPException: 404 if customer not found or has no purchases
    """
    # First check if customer exists
    customer_exists = any(c.id == customer_id for c in customers_db)
    if not customer_exists:
        raise HTTPException(
            status_code=404,
            detail=f"Customer with ID {customer_id} not found"
        )

    # Get products for the customer
    products = customer_products_db.get(customer_id, [])

    if not products:
        raise HTTPException(
            status_code=404,
            detail=f"No products found for customer with ID {customer_id}"
        )

    return products


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
