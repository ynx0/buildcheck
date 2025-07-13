# buildcheck


## To add a package

Do this instead of `pip install <package>`

1. Run `uv add <package>`
2. Run `uv sync`
3. Add and commit the `pyproject.toml` and `uv.lock` files

## When making changes to **`Model`s**

1. Run `reflex db makemigrations`
2. Run `reflex db migrate`


## Authors

- Joud
- Mohammed Alyami
- Noura
- Yaseen
