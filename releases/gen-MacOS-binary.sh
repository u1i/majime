version=$(grep version ../setup.py | sed "s/.*version=\"//; s/\".*//;")

cat ../majime/__main__.py majime.py | sed "s/##VERSION_PARSE##/version=\"$version\"/g;" > majime.py

pyinstaller --onefile majime.py

mv dist/majime .

rm majime-darwin-386.zip

zip majime-darwin-386.zip majime
