STATUS="$(git status)"

if [[ $STATUS == *"nothing to commit, working tree clean"* ]]
then
    make -C ./docs html
    git push origin --delete gh-pages
    grep -v "build" ./.gitignore > tmpfile && mv tmpfile ./.gitignore
    cp docs/.nojekyll docs/build/html
    git add .
    git commit -m "autodeploy docs"
    git subtree push --prefix docs/build/html origin gh-pages
    git reset HEAD~
    git checkout .gitignore
else
    echo "Need clean working directory to publish"
fi