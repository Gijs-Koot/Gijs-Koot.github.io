convert_notebooks:
	jupyter-nbconvert ./notebooks/birth-clustering.ipynb --to markdown
	cp ./notebooks/2017-12-31-birth-clustering.md ./_posts/
	sed ./notebooks/birth-clustering.md -e 's/birth-clustering_files/\/assets\/images/g' >> ./_posts/2017-12-31-birth-clustering.md
	cp ./notebooks/birth-clustering_files/birth-clustering_16_1.png ./assets/images
