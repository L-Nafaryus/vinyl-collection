cwd:= $(shell pwd)
src:= $(cwd)/src
build:= $(cwd)/build

.PHONY: all clean

all: vinylList.pdf

vinylList.pdf: vinylList.tex
	pdflatex -output-directory=$(build) -output-format=pdf $(src)/vinylList.tex

vinylList.tex:
	mkdir -p $(build)
	julia --project=$(cwd) $(src)/vinylList.jl

clean:
	rm -rf $(build)
