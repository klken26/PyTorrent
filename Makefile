all: main

main: main.py
	cp main.py main
	chmod +x main

clean:
	rm main
	
clean_all:
	rm main
	rm -r __pycache__