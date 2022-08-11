ifeq ($(OS),Windows_NT)
    RM = cmd /C del /Q /F
    RRM = cmd /C rmdir /Q /S
else
    RM = rm -f
    RRM = rm -f -r
endif


run:
	@poetry run python -m jentropy.wordle

v:
	poetry run nvim .

i:
	poetry run ipython

shell:
	poetry shell
