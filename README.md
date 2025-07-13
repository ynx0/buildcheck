# buildcheck


## To add a package

Do this instead of `pip install <package>`

1. Run `uv add <package>`
2. Run `uv sync`
3. Add and commit the `pyproject.toml` and `uv.lock` files

## How to test someone's PR

1. Save your current changes by either committing them or stashing them
2. Checkout the PR branch
3. **MAKE SURE TO RUN `uv sync`!!!**
4. Test as needed
5. Switch back to your branch
6. Run `uv sync`


## When making changes to **`Model`s**

1. Run `reflex db makemigrations`
2. Run `reflex db migrate`


## Authors

- Joud
- Mohammed Alyami
- Noura
- Yaseen
