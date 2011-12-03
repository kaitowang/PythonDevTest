# This makefile is for the server to release the source tarball automatically.
# make dist: create a source tarball in the source directory.
# make clean: remove the source tarball.

dist:
	python setup.py sdist
	mv ./dist/*.tar.gz .
	rm -rf ./dist
clean:
	rm *.tar.gz
