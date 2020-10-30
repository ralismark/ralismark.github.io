#
# Build the individual resources
#

SVG = em-wave.tex \
      $(wildcard *.dot) \

SVGOUT = $(addprefix build/,$(patsubst %.tex,%.svg,$(patsubst %.dot,%.svg,$(SVG))))

build/%.svg: %.tex
	pdflatex -output-directory=build -output-format=dvi -interaction=batchmode $<
	dvisvgm build/$*.dvi -p1 -n -o $@
	-rm build/$*.dvi build/$*.aux build/$*.log # Remove extra files

all: $(SVGOUT)

clean:
	-rm build/*

.PHONY: all clean
