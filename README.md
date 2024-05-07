# E commerce project
> Basic Django project for E-commerce system with basic features

## Installation
- Clone the repository
    ```bash
    git clone https://github.com/kfrawee/django-ecom.git
    ```
- Create a virtual environment and activate it
    ```bash
    python -m venv .venv && source .venv/bin/activate
    ```
- Install dependencies
    ```bash
    pip install -r requirements.txt
    ```
## Prerequisites
- Create .env file
    ```bash
    mv .env-template .env
    ```
- Change any values in .env file as required

## Usage
- Migrate database
    ```bash
    python manage.py cmakemigrations
    python manage.py migrate
    ```
- Run data seeders
    ```bash
    python manage.py seedusers
    python manage.py seeditems
    python manage.py seedcart
    ```
- Create superuser
    ```bash
    python manage.py createsuperuser
    ```

- Run server
    ```bash
    python manage.py runserver
    ```

**NOTE** Authentication is not implemented yet. Views have been bypassed with `user0` for testing purposes.

---

## Available endpoints:
- GET `/` endpoint to get all endpoints
    ```json
        {
            "all_endpoints": [
                "<URLPattern '' [name='get-endpoints']>",
                "<URLPattern 'health-check/' [name='health-check']>",
                "<URLPattern 'user/' [name='user-list-create']>",
                "<URLPattern 'user/<str:username>/' [name='user-detail-delete']>",
                "<URLPattern 'cart/' [name='cart-get-post-delete']>",
                "<URLPattern 'order/' [name='order-list-create']>",
                "<URLPattern 'order/<int:order_id>/' [name='order-detail']>",
                "<URLPattern 'pay_order/<int:order_id>/' [name='pay_order']>"
            ]
        }
    ```

## Workflow:
### After initial setup and running server with seeded data
#### Cart:
- View cart: `GET /cart/`
- Add item to cart: `POST /cart/ {"item_id": 1, "quantity": 2}`
- Item has status `Pending` by default. It can't be purchased until it has `Accepted` status.
    > You can add Items to cart or empty cart. You can add Items from admin panel using the created `superuser`,

#### Order:
- View orders: `GET /order/`
- View order detail: `GET /order/<int:order_id>/` 
- Create order: `POST /order/ {"order": true}`. This will create an order with only the cart items of status `Accepted`.
    > **NOTES**:<br> 
    > You can only place an order if there are items in the cart with status `Accepted`.<br>
    > Created order will have status `is_paid = false` till payment successful. <br>
    > Accepted items will be removed from cart.

#### Payment:
- Pay order: `POST /pay_order/<int:order_id>/ {"pay": true}` 
    > **NOTE**: This will mark order as `is_paid = true`.

---