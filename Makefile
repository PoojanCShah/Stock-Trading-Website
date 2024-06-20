git:
	git add .
	git commit -m "$(m)"
	git pull origin main
	git push origin main
