.PHONY: install run test clean shell init

install:
	pip install -r requirements.txt

run:
	flask run --debug

test:
	pytest -v

shell:
	flask shell

init:
	flask db init
	flask db migrate -m "initial"
	flask db upgrade

clean:
	rm -rf __pycache__ */__pycache__ */*/__pycache__
	rm -rf instance
	rm -rf logs
