# Reference
#
# This Makefile was built with help form an excellent tutorial:
#
#     Mike Jackson (ed.): "Software Carpentry: Automation and Make."
#     Version 2016.06, June 2016,
#     https://github.com/swcarpentry/make-novice, 10.5281/zenodo.57473.

ORIGINAL_VIDEOS = $(wildcard /home/aubreytensor1/Guam02/rawdata/*.mp4)
OUTPUT_VIDEOS = $(patsubst /home/aubreytensor1/Guam02/rawdata/%.mp4,/home/aubreytensor1/Guam02/output/%a.mp4,$(ORIGINAL_VIDEOS))

NUM_FRAMES = 2
SKIP_NO = 100
OUTPUT_DIR = /home/aubreytensor1/Guam02/output

all : $(OUTPUT_VIDEOS)

$(OUTPUT_VIDEOS) : $(ORIGINAL_VIDEOS)

/home/aubreytensor1/Guam02/output/%a.mp4 : /home/aubreytensor1/Guam02/rawdata/%.mp4
	./run-object-detectors.sh $< $(NUM_FRAMES) $(SKIP_NO) $(OUTPUT_DIR)

#default: $(OUTPUT_VIDEOS)

#%.mp4 : rawdata/%.mp4
#	ffmpeg -i $< -filter:v fps=fps=3 $@

clean:
	rm -f /home/aubreytensor1/Guam02/output/*


#f'ffmpeg -i {new_path} -filter:v fps=fps=3 {video_path}

## variables   : Print variables.

.PHONY : variables
variables:
	@echo 'ORIGINAL_VIDEOS (These videos already exist)'
	@echo $(ORIGINAL_VIDEOS)
	@echo
	@echo 'OUTPUT_VIDEOS (These files may not have been generated yet)'	
	@echo $(OUTPUT_VIDEOS)

help : Makefile
	@sed -n 's/^##//p' $<
