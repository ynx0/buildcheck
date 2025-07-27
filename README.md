# ARCH

## Motivation

<img width="300" alt="image" src="https://github.com/user-attachments/assets/d3d71cfa-3f16-4d98-855d-adb6a9a8b1a8" />


This is you whenever you feel like it's impossible.


## Reflex resources

- Components library - https://reflex.dev/docs/library/
- Templates to copy code from - https://reflex.dev/templates/

## How to run the application

1. `uv sync`
2. `uv run reflex run`



## How to test someone's PR

1. Save your current changes by either committing them or stashing them
2. Checkout the PR branch
3. **MAKE SURE TO RUN `uv sync`!!!**
4. Test as needed
5. Switch back to your branch
6. Run `uv sync`



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
